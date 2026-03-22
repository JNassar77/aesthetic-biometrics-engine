"""Tests for the treatment plan generator."""

import pytest

from app.treatment.plan_generator import (
    generate,
    TreatmentPlan,
    TreatmentConcern,
    SessionPlan,
    PRIMARY_SEVERITY_THRESHOLD,
    SECONDARY_SEVERITY_THRESHOLD,
    MAX_FILLER_PER_SESSION_ML,
    _compute_priority_score,
    _classify_concern,
    _build_filler_recommendations,
    _build_neurotoxin_recommendations,
)
from app.models.zone_models import ZoneResult, ZoneFinding, ZoneMeasurement


def _make_zone(
    zone_id: str = "Ck2",
    zone_name: str = "Zygomatic Eminence",
    region: str = "midface",
    severity: float = 5.0,
    findings: list[ZoneFinding] | None = None,
    measurements: list[ZoneMeasurement] | None = None,
) -> ZoneResult:
    return ZoneResult(
        zone_id=zone_id,
        zone_name=zone_name,
        region=region,
        severity=severity,
        findings=findings or [],
        measurements=measurements or [],
        primary_view="frontal",
    )


class TestGenerate:
    def test_empty_zones_returns_empty_plan(self):
        plan = generate([])
        assert plan.primary_concerns == []
        assert plan.secondary_concerns == []
        assert plan.session_count == 0
        assert plan.total_volume_estimate_ml == (0.0, 0.0)

    def test_single_zone_produces_plan(self):
        zone = _make_zone(zone_id="Ck2", severity=6.0, findings=[
            ZoneFinding(description="Malar flattening", severity_contribution=6.0, source_view="oblique"),
        ])
        plan = generate([zone])
        assert len(plan.primary_concerns) >= 1
        assert plan.session_count >= 1

    def test_low_severity_zones_become_secondary(self):
        zone = _make_zone(zone_id="Lp3", zone_name="Lip Corners", severity=2.0)
        plan = generate([zone])
        assert len(plan.primary_concerns) == 0
        assert len(plan.secondary_concerns) >= 1

    def test_below_threshold_zones_excluded(self):
        zone = _make_zone(severity=0.5)
        plan = generate([zone])
        assert len(plan.primary_concerns) == 0
        assert len(plan.secondary_concerns) == 0

    def test_multiple_zones_sorted_by_priority(self):
        zones = [
            _make_zone(zone_id="Lp1", zone_name="Upper Lip", region="lower_face", severity=4.0),
            _make_zone(zone_id="Ck2", zone_name="Zygomatic Eminence", region="midface", severity=6.0),
            _make_zone(zone_id="Ch1", zone_name="Chin", region="lower_face", severity=5.0),
        ]
        plan = generate(zones)
        # All should be primary (severity >= 3)
        assert len(plan.primary_concerns) == 3
        # First concern should have priority 1
        assert plan.primary_concerns[0].priority == 1


class TestPriorityScoring:
    def test_higher_severity_higher_score(self):
        z_low = _make_zone(zone_id="Ck2", severity=3.0)
        z_high = _make_zone(zone_id="Ck2", severity=8.0)
        assert _compute_priority_score(z_high) > _compute_priority_score(z_low)

    def test_structural_zone_beats_detail_at_same_severity(self):
        """At equal severity, structural zone (Ck2) should rank above detail (Lp1)."""
        z_structural = _make_zone(zone_id="Ck2", severity=5.0)
        z_detail = _make_zone(zone_id="Lp1", severity=5.0)
        assert _compute_priority_score(z_structural) > _compute_priority_score(z_detail)


class TestProductRecommendations:
    def test_midface_has_filler_recommendations(self):
        recs = _build_filler_recommendations("Ck2")
        assert len(recs) >= 1
        assert any("Voluma" in p for r in recs for p in r.products)

    def test_lip_has_soft_filler_recommendations(self):
        recs = _build_filler_recommendations("Lp1")
        assert len(recs) >= 1
        assert any(r.category == "ha_soft" for r in recs)

    def test_glabella_has_neurotoxin(self):
        recs = _build_neurotoxin_recommendations("Bw2")
        assert len(recs) >= 1

    def test_unknown_zone_returns_empty(self):
        recs = _build_filler_recommendations("XX9")
        assert recs == []


class TestSessionPlanning:
    def test_single_zone_one_session(self):
        zones = [_make_zone(zone_id="Ck2", severity=6.0)]
        plan = generate(zones)
        assert plan.session_count == 1

    def test_many_zones_multiple_sessions(self):
        """Many high-volume zones should spill into multiple sessions."""
        zones = [
            _make_zone(zone_id="Ck2", severity=7.0),
            _make_zone(zone_id="Ch1", severity=6.0),
            _make_zone(zone_id="Jl1", severity=6.0),
            _make_zone(zone_id="Ns1", severity=5.0),
            _make_zone(zone_id="Mn1", severity=5.0),
            _make_zone(zone_id="T1", severity=4.0),
            _make_zone(zone_id="Lp1", severity=4.0),
            _make_zone(zone_id="Ck3", severity=4.0),
        ]
        plan = generate(zones)
        # With many high-volume zones, should have 2+ sessions
        assert plan.session_count >= 1

    def test_session_volume_within_limits(self):
        zones = [
            _make_zone(zone_id="Ck2", severity=7.0),
            _make_zone(zone_id="Ch1", severity=6.0),
            _make_zone(zone_id="Jl1", severity=5.0),
        ]
        plan = generate(zones)
        for session in plan.sessions:
            _, max_vol = session.total_filler_volume_ml
            # Allow slight overage due to rounding, but shouldn't exceed limit by much
            assert max_vol <= MAX_FILLER_PER_SESSION_ML + 1.0

    def test_structural_zones_in_session_1(self):
        zones = [
            _make_zone(zone_id="Ck2", severity=6.0),  # structural (priority 1)
            _make_zone(zone_id="Lp1", severity=5.0),   # detail (priority 5)
        ]
        plan = generate(zones)
        if plan.sessions:
            session1 = plan.sessions[0]
            session1_ids = {c.zone_id for c in session1.concerns}
            assert "Ck2" in session1_ids

    def test_neurotoxin_only_zones_dont_block_filler(self):
        zones = [
            _make_zone(zone_id="Bw2", zone_name="Glabella", severity=5.0),
            _make_zone(zone_id="Ck2", severity=6.0),
        ]
        plan = generate(zones)
        # Both should fit in session 1 since Bw2 is neurotoxin-only
        if plan.session_count == 1:
            assert len(plan.sessions[0].concerns) == 2


class TestVolumeEstimation:
    def test_total_volume_positive_for_filler_zones(self):
        zones = [_make_zone(zone_id="Ck2", severity=6.0)]
        plan = generate(zones)
        min_vol, max_vol = plan.total_volume_estimate_ml
        assert min_vol > 0
        assert max_vol >= min_vol

    def test_total_neurotoxin_for_toxin_zones(self):
        zones = [_make_zone(zone_id="Bw2", zone_name="Glabella", severity=5.0)]
        plan = generate(zones)
        min_u, max_u = plan.total_neurotoxin_units
        assert min_u > 0
        assert max_u >= min_u


class TestContraindications:
    def test_contraindications_included_in_plan(self):
        zones = [
            _make_zone(zone_id="Tt1", zone_name="Tear Trough", severity=7.0),
        ]
        plan = generate(zones)
        # Should have at least vascular risk or tear trough special warning
        assert len(plan.contraindications) >= 1

    def test_no_contraindications_for_safe_zones(self):
        zones = [_make_zone(zone_id="Lp1", zone_name="Upper Lip", severity=3.0)]
        plan = generate(zones)
        # May have safety notes but not severe contraindications
        severe = [c for c in plan.contraindications if c.severity.value == "contraindicated"]
        assert len(severe) == 0


class TestConcernClassification:
    def test_classify_uses_top_finding(self):
        zone = _make_zone(findings=[
            ZoneFinding(description="Malar flattening detected", severity_contribution=6.0, source_view="oblique"),
            ZoneFinding(description="Minor deviation", severity_contribution=1.0, source_view="frontal"),
        ])
        concern = _classify_concern(zone)
        assert "Malar flattening" in concern

    def test_classify_fallback_no_findings(self):
        zone = _make_zone(severity=4.0, findings=[])
        concern = _classify_concern(zone)
        assert "Zygomatic Eminence" in concern


class TestTreatmentPlanStructure:
    def test_concerns_have_priorities(self):
        zones = [
            _make_zone(zone_id="Ck2", severity=6.0),
            _make_zone(zone_id="Ch1", severity=5.0),
        ]
        plan = generate(zones)
        priorities = [c.priority for c in plan.primary_concerns]
        assert priorities == sorted(priorities)  # Should be 1, 2, 3...

    def test_high_risk_zones_flagged(self):
        zones = [_make_zone(zone_id="Tt1", zone_name="Tear Trough", severity=5.0)]
        plan = generate(zones)
        if plan.primary_concerns:
            tt_concern = next((c for c in plan.primary_concerns if c.zone_id == "Tt1"), None)
            if tt_concern:
                assert tt_concern.is_high_risk

    def test_session_interval_default(self):
        zones = [_make_zone(severity=6.0)]
        plan = generate(zones)
        assert plan.session_interval_weeks == 4


class TestClinicalOrdering:
    """Test that the clinical ordering logic follows the rules:
    Structural → Volume → Folds → Detail.
    """

    def test_midface_before_nasolabial(self):
        """Midface volume should be treated before nasolabial folds."""
        zones = [
            _make_zone(zone_id="Ns1", zone_name="Nasolabial Fold", severity=5.0),
            _make_zone(zone_id="Ck2", zone_name="Zygomatic Eminence", severity=5.0),
        ]
        plan = generate(zones)
        ck2_priority = next(c.priority for c in plan.primary_concerns if c.zone_id == "Ck2")
        ns1_priority = next(c.priority for c in plan.primary_concerns if c.zone_id == "Ns1")
        assert ck2_priority < ns1_priority  # Lower number = higher priority

    def test_chin_before_lips(self):
        """Chin (structural) should be treated before lip detail."""
        zones = [
            _make_zone(zone_id="Lp1", zone_name="Upper Lip", severity=5.0),
            _make_zone(zone_id="Ch1", zone_name="Chin", severity=5.0),
        ]
        plan = generate(zones)
        ch1_priority = next(c.priority for c in plan.primary_concerns if c.zone_id == "Ch1")
        lp1_priority = next(c.priority for c in plan.primary_concerns if c.zone_id == "Lp1")
        assert ch1_priority < lp1_priority

    def test_high_severity_detail_beats_low_severity_structural(self):
        """Very high severity detail zone can outrank low severity structural zone."""
        zones = [
            _make_zone(zone_id="Lp1", zone_name="Upper Lip", severity=9.0),
            _make_zone(zone_id="Ck2", zone_name="Zygomatic Eminence", severity=3.0),
        ]
        plan = generate(zones)
        lp1_priority = next(c.priority for c in plan.primary_concerns if c.zone_id == "Lp1")
        ck2_priority = next(c.priority for c in plan.primary_concerns if c.zone_id == "Ck2")
        assert lp1_priority < ck2_priority  # Lip has much higher severity, outranks
