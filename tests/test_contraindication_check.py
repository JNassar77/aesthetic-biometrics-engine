"""Tests for the contraindication checker."""

import pytest

from app.treatment.contraindication_check import (
    check_contraindications,
    Contraindication,
    ContraindicationSeverity,
    EXTREME_ASYMMETRY_THRESHOLD,
    PATHOLOGY_SEVERITY_THRESHOLD,
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


class TestExtremeAsymmetry:
    def test_no_flag_below_threshold(self):
        zone = _make_zone(severity=5.0, findings=[
            ZoneFinding(description="asymmetry detected", severity_contribution=5.0, source_view="frontal"),
        ])
        results = check_contraindications([zone])
        codes = [c.code for c in results]
        assert "EXTREME_ASYMMETRY" not in codes

    def test_flag_extreme_asymmetry(self):
        zone = _make_zone(severity=8.5, findings=[
            ZoneFinding(description="Extreme asymmetry 15mm", severity_contribution=8.0, source_view="frontal"),
        ])
        results = check_contraindications([zone])
        codes = [c.code for c in results]
        assert "EXTREME_ASYMMETRY" in codes

    def test_no_flag_high_severity_without_asymmetry_findings(self):
        """High severity alone without asymmetry findings should not trigger."""
        zone = _make_zone(severity=9.0, findings=[
            ZoneFinding(description="severe volume loss", severity_contribution=9.0, source_view="frontal"),
        ])
        results = check_contraindications([zone])
        codes = [c.code for c in results]
        assert "EXTREME_ASYMMETRY" not in codes


class TestPathologicalSeverity:
    def test_no_flag_moderate_severity(self):
        zone = _make_zone(severity=7.0)
        results = check_contraindications([zone])
        codes = [c.code for c in results]
        assert "HIGH_SEVERITY" not in codes

    def test_flag_very_high_severity(self):
        zone = _make_zone(severity=9.5)
        results = check_contraindications([zone])
        codes = [c.code for c in results]
        assert "HIGH_SEVERITY" in codes


class TestVascularRisk:
    def test_high_risk_zone_flagged(self):
        zone = _make_zone(zone_id="Tt1", zone_name="Tear Trough", severity=6.0)
        results = check_contraindications([zone])
        codes = [c.code for c in results]
        assert "VASCULAR_RISK" in codes

    def test_low_severity_high_risk_zone_not_flagged(self):
        zone = _make_zone(zone_id="Tt1", zone_name="Tear Trough", severity=2.0)
        results = check_contraindications([zone])
        codes = [c.code for c in results]
        assert "VASCULAR_RISK" not in codes

    def test_non_vascular_zone_not_flagged(self):
        zone = _make_zone(zone_id="Fo1", zone_name="Forehead", severity=7.0)
        results = check_contraindications([zone])
        codes = [c.code for c in results]
        assert "VASCULAR_RISK" not in codes


class TestTearTroughSpecial:
    def test_deep_tear_trough_flagged(self):
        zone = _make_zone(zone_id="Tt1", zone_name="Tear Trough", severity=6.5)
        results = check_contraindications([zone])
        codes = [c.code for c in results]
        assert "TEAR_TROUGH_DEEP" in codes

    def test_mild_tear_trough_not_flagged(self):
        zone = _make_zone(zone_id="Tt1", zone_name="Tear Trough", severity=3.0)
        results = check_contraindications([zone])
        codes = [c.code for c in results]
        assert "TEAR_TROUGH_DEEP" not in codes


class TestOvertreatmentRisk:
    def test_no_flag_normal_total(self):
        zones = [_make_zone(severity=5.0) for _ in range(3)]
        results = check_contraindications(zones)
        codes = [c.code for c in results]
        assert "OVERTREATMENT_RISK" not in codes

    def test_flag_excessive_total(self):
        zones = [_make_zone(zone_id=f"Z{i}", severity=8.0) for i in range(10)]
        results = check_contraindications(zones)
        codes = [c.code for c in results]
        assert "OVERTREATMENT_RISK" in codes


class TestGlabellaForeheadDependency:
    def test_forehead_without_glabella_warned(self):
        zones = [
            _make_zone(zone_id="Fo1", zone_name="Forehead", severity=5.0),
        ]
        results = check_contraindications(zones)
        codes = [c.code for c in results]
        assert "FOREHEAD_WITHOUT_GLABELLA" in codes

    def test_forehead_with_glabella_no_warning(self):
        zones = [
            _make_zone(zone_id="Fo1", zone_name="Forehead", severity=5.0),
            _make_zone(zone_id="Bw2", zone_name="Glabella", severity=4.0),
        ]
        results = check_contraindications(zones)
        codes = [c.code for c in results]
        assert "FOREHEAD_WITHOUT_GLABELLA" not in codes


class TestSortOrder:
    def test_results_sorted_by_severity(self):
        zones = [
            _make_zone(zone_id="Tt1", zone_name="Tear Trough", severity=7.0),
            _make_zone(zone_id="Ck2", zone_name="Zygomatic", severity=9.5,
                       findings=[ZoneFinding(description="extreme asymmetry", severity_contribution=9.0, source_view="frontal")]),
        ]
        results = check_contraindications(zones)
        if len(results) >= 2:
            severity_order = {
                ContraindicationSeverity.CONTRAINDICATED: 0,
                ContraindicationSeverity.REFERRAL: 1,
                ContraindicationSeverity.CAUTION: 2,
                ContraindicationSeverity.WARNING: 3,
            }
            for i in range(len(results) - 1):
                assert severity_order[results[i].severity] <= severity_order[results[i + 1].severity]


class TestEmptyInput:
    def test_no_zones_no_contraindications(self):
        results = check_contraindications([])
        assert results == []

    def test_all_low_severity_no_contraindications(self):
        zones = [_make_zone(severity=0.5), _make_zone(zone_id="Lp1", severity=0.3)]
        results = check_contraindications(zones)
        assert len(results) == 0
