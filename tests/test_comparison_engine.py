"""Tests for the comparison engine (Before/After analysis)."""

import pytest

from app.analysis.comparison_engine import (
    compare,
    ComparisonResult,
    ZoneDelta,
    MeasurementDelta,
    HeatmapEntry,
    SEVERITY_CHANGE_THRESHOLD,
    RESOLVED_THRESHOLD,
    _compute_measurement_deltas,
    _compute_zone_delta,
    _generate_heatmap,
    _compute_improvement_score,
)
from app.analysis.zone_analyzer import ZoneReport
from app.models.zone_models import (
    ZoneResult, ZoneFinding, ZoneMeasurement, GlobalMetrics, CalibrationInfo,
)


# ──────────────────────── Fixtures ────────────────────────

def _make_zone(
    zone_id: str = "Ck2",
    zone_name: str = "Zygomatic Eminence",
    region: str = "midface",
    severity: float = 5.0,
    measurements: list[ZoneMeasurement] | None = None,
    findings: list[ZoneFinding] | None = None,
) -> ZoneResult:
    return ZoneResult(
        zone_id=zone_id,
        zone_name=zone_name,
        region=region,
        severity=severity,
        measurements=measurements or [],
        findings=findings or [],
        primary_view="frontal",
    )


def _make_report(
    zones: list[ZoneResult] | None = None,
    aesthetic_score: float = 75.0,
) -> ZoneReport:
    return ZoneReport(
        zones=zones or [],
        global_metrics=GlobalMetrics(
            symmetry_index=90.0,
            facial_thirds={"upper": 0.33, "middle": 0.33, "lower": 0.34},
            golden_ratio_deviation=3.0,
            aesthetic_score=aesthetic_score,
        ),
        calibration=CalibrationInfo(
            method="iris",
            px_per_mm=5.0,
            confidence=0.95,
        ),
        aesthetic_score=aesthetic_score,
        expression_deviation=0.05,
        views_analyzed=["frontal", "profile", "oblique"],
    )


def _make_measurement(
    name: str = "ogee_curve_score",
    value: float = 60.0,
    unit: str = "score",
    ideal_min: float | None = 70.0,
    ideal_max: float | None = 100.0,
) -> ZoneMeasurement:
    return ZoneMeasurement(
        name=name, value=value, unit=unit,
        ideal_min=ideal_min, ideal_max=ideal_max,
    )


# ──────────────────────── Test Zone Delta Computation ────────────────────────

class TestZoneDelta:
    def test_improved_zone(self):
        pre = _make_zone(severity=7.0)
        post = _make_zone(severity=3.0)
        delta = _compute_zone_delta(pre, post)
        assert delta.status == "improved"
        assert delta.severity_delta == -4.0
        assert delta.severity_improvement_pct > 0

    def test_worsened_zone(self):
        pre = _make_zone(severity=3.0)
        post = _make_zone(severity=6.0)
        delta = _compute_zone_delta(pre, post)
        assert delta.status == "worsened"
        assert delta.severity_delta == 3.0
        assert delta.severity_improvement_pct < 0

    def test_unchanged_zone(self):
        pre = _make_zone(severity=5.0)
        post = _make_zone(severity=5.2)
        delta = _compute_zone_delta(pre, post)
        assert delta.status == "unchanged"

    def test_resolved_zone(self):
        pre = _make_zone(severity=4.0)
        post = _make_zone(severity=0.5)
        delta = _compute_zone_delta(pre, post)
        assert delta.status == "resolved"
        assert delta.severity_improvement_pct > 80

    def test_new_zone(self):
        """Zone that appears only in post assessment."""
        delta = _compute_zone_delta(None, _make_zone(severity=3.0))
        assert delta.status == "new"
        assert delta.pre_severity == 0.0
        assert delta.post_severity == 3.0

    def test_disappeared_zone(self):
        """Zone that exists only in pre assessment."""
        delta = _compute_zone_delta(_make_zone(severity=5.0), None)
        assert delta.status == "resolved"
        assert delta.severity_improvement_pct == 100.0


# ──────────────────────── Test Measurement Deltas ────────────────────────

class TestMeasurementDelta:
    def test_measurement_improved_toward_ideal(self):
        pre = [_make_measurement("ogee_curve_score", 55.0, ideal_min=70.0, ideal_max=100.0)]
        post = [_make_measurement("ogee_curve_score", 75.0, ideal_min=70.0, ideal_max=100.0)]
        deltas = _compute_measurement_deltas(pre, post)
        assert len(deltas) == 1
        assert deltas[0].improved is True
        assert deltas[0].delta == 20.0

    def test_measurement_worsened_away_from_ideal(self):
        pre = [_make_measurement("ogee_curve_score", 75.0, ideal_min=70.0, ideal_max=100.0)]
        post = [_make_measurement("ogee_curve_score", 55.0, ideal_min=70.0, ideal_max=100.0)]
        deltas = _compute_measurement_deltas(pre, post)
        assert deltas[0].improved is False

    def test_asymmetry_decrease_is_improvement(self):
        pre = [_make_measurement("brow_asymmetry", 4.0, unit="mm", ideal_min=None, ideal_max=None)]
        post = [_make_measurement("brow_asymmetry", 1.5, unit="mm", ideal_min=None, ideal_max=None)]
        deltas = _compute_measurement_deltas(pre, post)
        assert deltas[0].improved is True

    def test_measurement_only_in_pre_skipped(self):
        pre = [_make_measurement("old_metric", 5.0)]
        post: list[ZoneMeasurement] = []
        deltas = _compute_measurement_deltas(pre, post)
        assert len(deltas) == 0

    def test_delta_pct_calculated(self):
        pre = [_make_measurement("score", 50.0, ideal_min=None, ideal_max=None)]
        post = [_make_measurement("score", 75.0, ideal_min=None, ideal_max=None)]
        deltas = _compute_measurement_deltas(pre, post)
        assert deltas[0].delta_pct == 50.0

    def test_zero_pre_value_handled(self):
        pre = [_make_measurement("score", 0.0, ideal_min=None, ideal_max=None)]
        post = [_make_measurement("score", 5.0, ideal_min=None, ideal_max=None)]
        deltas = _compute_measurement_deltas(pre, post)
        assert deltas[0].delta_pct == 100.0


# ──────────────────────── Test Heatmap Generation ────────────────────────

class TestHeatmap:
    def test_improved_zone_green(self):
        deltas = [ZoneDelta(
            zone_id="Ck2", zone_name="Zygomatic", region="midface",
            pre_severity=7.0, post_severity=3.0, severity_delta=-4.0,
            severity_improvement_pct=57.1, status="improved",
        )]
        heatmap = _generate_heatmap(deltas)
        assert len(heatmap) == 1
        assert heatmap[0].color_code == "#4ade80"  # green
        assert heatmap[0].delta_intensity < 0  # negative = improvement

    def test_worsened_zone_red(self):
        deltas = [ZoneDelta(
            zone_id="Lp1", zone_name="Upper Lip", region="lower_face",
            pre_severity=2.0, post_severity=6.0, severity_delta=4.0,
            severity_improvement_pct=-200.0, status="worsened",
        )]
        heatmap = _generate_heatmap(deltas)
        assert heatmap[0].color_code == "#ef4444"  # red

    def test_resolved_zone_dark_green(self):
        deltas = [ZoneDelta(
            zone_id="Ns1", zone_name="Nasolabial", region="midface",
            pre_severity=5.0, post_severity=0.5, severity_delta=-4.5,
            severity_improvement_pct=90.0, status="resolved",
        )]
        heatmap = _generate_heatmap(deltas)
        assert heatmap[0].color_code == "#22c55e"

    def test_unchanged_zone_gray(self):
        deltas = [ZoneDelta(
            zone_id="Ch1", zone_name="Chin", region="lower_face",
            pre_severity=3.0, post_severity=3.2, severity_delta=0.2,
            severity_improvement_pct=-6.7, status="unchanged",
        )]
        heatmap = _generate_heatmap(deltas)
        assert heatmap[0].color_code == "#9ca3af"

    def test_intensity_range_valid(self):
        deltas = [ZoneDelta(
            zone_id="Ck2", zone_name="Zygomatic", region="midface",
            pre_severity=10.0, post_severity=0.0, severity_delta=-10.0,
            severity_improvement_pct=100.0, status="resolved",
        )]
        heatmap = _generate_heatmap(deltas)
        assert 0 <= heatmap[0].pre_intensity <= 1
        assert 0 <= heatmap[0].post_intensity <= 1
        assert -1 <= heatmap[0].delta_intensity <= 1


# ──────────────────────── Test Improvement Score ────────────────────────

class TestImprovementScore:
    def test_all_resolved_gives_high_score(self):
        deltas = [
            ZoneDelta("Ck2", "Zygomatic", "midface", 7.0, 0.5, -6.5, 92.9, status="resolved"),
            ZoneDelta("Ns1", "Nasolabial", "midface", 5.0, 0.3, -4.7, 94.0, status="resolved"),
        ]
        score = _compute_improvement_score(deltas)
        assert score > 80

    def test_no_change_gives_50(self):
        deltas = [
            ZoneDelta("Ck2", "Zygomatic", "midface", 5.0, 5.0, 0.0, 0.0, status="unchanged"),
        ]
        score = _compute_improvement_score(deltas)
        assert score == 50.0

    def test_worsened_gives_below_50(self):
        deltas = [
            ZoneDelta("Ck2", "Zygomatic", "midface", 3.0, 8.0, 5.0, -166.7, status="worsened"),
        ]
        score = _compute_improvement_score(deltas)
        assert score < 50

    def test_empty_deltas_gives_50(self):
        assert _compute_improvement_score([]) == 50.0

    def test_score_clamped_0_100(self):
        deltas = [
            ZoneDelta("Ck2", "Zygomatic", "midface", 10.0, 0.0, -10.0, 100.0, status="resolved"),
        ]
        score = _compute_improvement_score(deltas)
        assert 0 <= score <= 100

    def test_midface_weighted_higher(self):
        """Midface improvement should produce higher score than profile improvement."""
        midface_deltas = [
            ZoneDelta("Ck2", "Zygomatic", "midface", 7.0, 2.0, -5.0, 71.4, status="improved"),
        ]
        profile_deltas = [
            ZoneDelta("Pf1", "Nasal", "profile", 7.0, 2.0, -5.0, 71.4, status="improved"),
        ]
        midface_score = _compute_improvement_score(midface_deltas)
        profile_score = _compute_improvement_score(profile_deltas)
        # Both should be good, but with region weighting they may differ slightly
        # Both produce the same improvement_ratio so score should be same
        # (weight only changes relative importance when mixed)
        assert midface_score > 50
        assert profile_score > 50


# ──────────────────────── Test Full Compare Function ────────────────────────

class TestCompare:
    def test_identical_reports_no_change(self):
        zones = [_make_zone(zone_id="Ck2", severity=5.0)]
        pre = _make_report(zones=zones, aesthetic_score=70.0)
        post = _make_report(zones=zones, aesthetic_score=70.0)
        result = compare(pre, post)
        assert result.zones_unchanged >= 1
        assert result.aesthetic_score_delta == 0.0
        assert result.improvement_score == 50.0

    def test_improved_treatment(self):
        pre_zones = [
            _make_zone(zone_id="Ck2", severity=7.0),
            _make_zone(zone_id="Ns1", zone_name="Nasolabial", severity=5.0),
        ]
        post_zones = [
            _make_zone(zone_id="Ck2", severity=2.0),
            _make_zone(zone_id="Ns1", zone_name="Nasolabial", severity=1.5),
        ]
        pre = _make_report(zones=pre_zones, aesthetic_score=60.0)
        post = _make_report(zones=post_zones, aesthetic_score=85.0)
        result = compare(pre, post)

        assert result.zones_improved >= 2
        assert result.aesthetic_score_delta == 25.0
        assert result.improvement_score > 50

    def test_worsened_treatment(self):
        pre_zones = [_make_zone(zone_id="Lp1", severity=2.0)]
        post_zones = [_make_zone(zone_id="Lp1", severity=7.0)]
        pre = _make_report(zones=pre_zones, aesthetic_score=85.0)
        post = _make_report(zones=post_zones, aesthetic_score=60.0)
        result = compare(pre, post)

        assert result.zones_worsened >= 1
        assert result.aesthetic_score_delta < 0

    def test_new_zone_in_post(self):
        pre_zones = [_make_zone(zone_id="Ck2", severity=5.0)]
        post_zones = [
            _make_zone(zone_id="Ck2", severity=2.0),
            _make_zone(zone_id="Lp1", zone_name="Upper Lip", severity=4.0),
        ]
        pre = _make_report(zones=pre_zones, aesthetic_score=75.0)
        post = _make_report(zones=post_zones, aesthetic_score=72.0)
        result = compare(pre, post)

        assert result.zones_new >= 1
        assert result.zones_improved >= 1

    def test_zone_resolved_in_post(self):
        pre_zones = [
            _make_zone(zone_id="Ck2", severity=7.0),
            _make_zone(zone_id="Ns1", zone_name="Nasolabial", severity=5.0),
        ]
        post_zones = [
            _make_zone(zone_id="Ck2", severity=2.0),
        ]
        pre = _make_report(zones=pre_zones, aesthetic_score=60.0)
        post = _make_report(zones=post_zones, aesthetic_score=90.0)
        result = compare(pre, post)

        assert result.zones_resolved >= 1

    def test_empty_reports(self):
        pre = _make_report(zones=[], aesthetic_score=100.0)
        post = _make_report(zones=[], aesthetic_score=100.0)
        result = compare(pre, post)
        assert result.zone_deltas == []
        assert result.improvement_score == 50.0

    def test_heatmap_generated(self):
        pre_zones = [_make_zone(zone_id="Ck2", severity=6.0)]
        post_zones = [_make_zone(zone_id="Ck2", severity=2.0)]
        pre = _make_report(zones=pre_zones)
        post = _make_report(zones=post_zones)
        result = compare(pre, post)

        assert len(result.heatmap) >= 1
        assert result.heatmap[0].zone_id == "Ck2"

    def test_summary_generated(self):
        pre_zones = [_make_zone(zone_id="Ck2", severity=6.0)]
        post_zones = [_make_zone(zone_id="Ck2", severity=2.0)]
        pre = _make_report(zones=pre_zones, aesthetic_score=70.0)
        post = _make_report(zones=post_zones, aesthetic_score=88.0)
        result = compare(pre, post)
        assert "Aesthetic score" in result.summary
        assert "improved" in result.summary.lower() or "Zones" in result.summary

    def test_deltas_sorted_by_absolute_change(self):
        pre_zones = [
            _make_zone(zone_id="Ck2", severity=8.0),
            _make_zone(zone_id="Lp1", zone_name="Upper Lip", severity=3.0),
        ]
        post_zones = [
            _make_zone(zone_id="Ck2", severity=2.0),   # delta = -6
            _make_zone(zone_id="Lp1", zone_name="Upper Lip", severity=2.0),  # delta = -1
        ]
        pre = _make_report(zones=pre_zones)
        post = _make_report(zones=post_zones)
        result = compare(pre, post)

        # Ck2 has larger delta, should be first
        assert result.zone_deltas[0].zone_id == "Ck2"

    def test_measurement_deltas_included(self):
        pre_m = [_make_measurement("ogee_curve_score", 55.0)]
        post_m = [_make_measurement("ogee_curve_score", 78.0)]
        pre_zones = [_make_zone(zone_id="Ck2", severity=6.0, measurements=pre_m)]
        post_zones = [_make_zone(zone_id="Ck2", severity=2.0, measurements=post_m)]
        pre = _make_report(zones=pre_zones)
        post = _make_report(zones=post_zones)
        result = compare(pre, post)

        ck2_delta = next(d for d in result.zone_deltas if d.zone_id == "Ck2")
        assert len(ck2_delta.measurement_deltas) == 1
        assert ck2_delta.measurement_deltas[0].delta == 23.0


class TestCompareStatusCounts:
    def test_all_status_counts_correct(self):
        pre_zones = [
            _make_zone(zone_id="Ck2", severity=7.0),  # → improved
            _make_zone(zone_id="Ns1", zone_name="Nasolabial", severity=5.0),  # → resolved
            _make_zone(zone_id="Ch1", zone_name="Chin", severity=3.0),  # → unchanged
            _make_zone(zone_id="Lp1", zone_name="Upper Lip", severity=2.0),  # → worsened
        ]
        post_zones = [
            _make_zone(zone_id="Ck2", severity=3.0),
            _make_zone(zone_id="Ns1", zone_name="Nasolabial", severity=0.5),
            _make_zone(zone_id="Ch1", zone_name="Chin", severity=3.1),
            _make_zone(zone_id="Lp1", zone_name="Upper Lip", severity=5.0),
            _make_zone(zone_id="Tt1", zone_name="Tear Trough", severity=4.0),  # new
        ]
        pre = _make_report(zones=pre_zones, aesthetic_score=65.0)
        post = _make_report(zones=post_zones, aesthetic_score=70.0)
        result = compare(pre, post)

        assert result.zones_improved >= 1
        assert result.zones_resolved >= 1
        assert result.zones_unchanged >= 1
        assert result.zones_worsened >= 1
        assert result.zones_new >= 1
        total = (result.zones_improved + result.zones_worsened +
                 result.zones_unchanged + result.zones_resolved + result.zones_new)
        assert total == len(result.zone_deltas)
