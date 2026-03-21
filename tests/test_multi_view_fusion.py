"""Tests for multi-view fusion engine."""

import pytest

from app.analysis.multi_view_fusion import (
    ViewMeasurement,
    FusedMeasurement,
    ViewContradiction,
    ZoneFusionResult,
    FusionResult,
    fuse_zone_measurements,
    fuse_all_zones,
    _fuse_values,
    _detect_contradiction,
    VIEW_CONFIDENCE,
    CONTRADICTION_THRESHOLDS,
)
from app.treatment.zone_definitions import ZONES, ZoneDefinition, ViewPriority, Region


# ──────────────── Helpers ────────────────


def _make_measurement(
    name: str = "test_metric",
    value: float = 10.0,
    unit: str = "mm",
    view: str = "frontal",
    confidence: float = 1.0,
) -> ViewMeasurement:
    return ViewMeasurement(
        metric_name=name,
        value=value,
        unit=unit,
        view=view,
        confidence=confidence,
    )


# ──────────────── _fuse_values ────────────────


class TestFuseValues:
    def test_primary_only(self):
        val, conf = _fuse_values(10.0, [])
        assert val == 10.0
        assert conf == 1.0

    def test_primary_with_one_secondary(self):
        val, conf = _fuse_values(10.0, [(9.0, 1.0)])
        # Weighted avg: 10*1.0 + 9*0.7 = 16.3 / 1.7 ≈ 9.59
        assert 9.0 < val < 10.0
        assert conf == 0.9

    def test_primary_with_two_secondaries(self):
        val, conf = _fuse_values(10.0, [(10.0, 1.0), (10.0, 1.0)])
        assert val == pytest.approx(10.0, abs=0.1)
        assert conf == 1.0

    def test_secondary_pulls_value(self):
        """Secondary views should pull the fused value toward them."""
        val_match, _ = _fuse_values(10.0, [(10.0, 1.0)])
        val_low, _ = _fuse_values(10.0, [(5.0, 1.0)])
        assert val_low < val_match

    def test_low_confidence_secondary_has_less_effect(self):
        val_high_conf, _ = _fuse_values(10.0, [(5.0, 1.0)])
        val_low_conf, _ = _fuse_values(10.0, [(5.0, 0.3)])
        # Low confidence secondary should pull less
        assert val_low_conf > val_high_conf


# ──────────────── _detect_contradiction ────────────────


class TestDetectContradiction:
    def test_no_contradiction_within_threshold(self):
        result = _detect_contradiction(
            "test", "mm", "frontal", 10.0, "profile", 11.0, "Ck1"
        )
        assert result is None

    def test_contradiction_exceeds_threshold(self):
        result = _detect_contradiction(
            "test", "mm", "frontal", 10.0, "profile", 15.0, "Ck1"
        )
        assert result is not None
        assert result.difference == 5.0
        assert result.zone_id == "Ck1"

    def test_angle_contradiction(self):
        result = _detect_contradiction(
            "nasolabial_angle", "deg", "frontal", 95.0, "oblique", 108.0, "Pf1"
        )
        assert result is not None
        assert result.difference > 10.0

    def test_ratio_contradiction(self):
        result = _detect_contradiction(
            "lip_ratio", "ratio", "frontal", 0.625, "profile", 0.8, "Lp1"
        )
        assert result is not None

    def test_exact_match_no_contradiction(self):
        result = _detect_contradiction(
            "test", "mm", "frontal", 10.0, "profile", 10.0, "Ck1"
        )
        assert result is None


# ──────────────── fuse_zone_measurements ────────────────


class TestFuseZoneMeasurements:
    def test_single_view_no_fusion_needed(self):
        """Zone with only primary view — no fusion, just pass-through."""
        zone_def = ZONES["T1"]  # oblique-only zone
        view_data = {
            "oblique": [
                _make_measurement("temporal_depth_mm", 1.5, "mm", "oblique"),
            ],
        }
        result = fuse_zone_measurements(zone_def, view_data)
        assert result.zone_id == "T1"
        assert len(result.measurements) == 1
        assert result.measurements[0].fused_value == 1.5
        assert result.contradictions == []

    def test_two_views_fusioned(self):
        """Zone with primary + secondary — measurements fused."""
        zone_def = ZONES["Ck1"]  # oblique primary, frontal secondary
        view_data = {
            "oblique": [
                _make_measurement("bizygomatic_width_mm", 135.0, "mm", "oblique"),
            ],
            "frontal": [
                _make_measurement("bizygomatic_width_mm", 133.0, "mm", "frontal"),
            ],
        }
        result = fuse_zone_measurements(zone_def, view_data)
        assert result.zone_id == "Ck1"
        assert len(result.measurements) == 1
        m = result.measurements[0]
        # Fused value should be between primary and secondary
        assert 133.0 <= m.fused_value <= 135.0
        assert len(m.contributing_views) == 2

    def test_contradiction_detected(self):
        """Large discrepancy between views flags a contradiction."""
        zone_def = ZONES["Lp1"]  # frontal primary, profile secondary
        view_data = {
            "frontal": [
                _make_measurement("upper_lip_height_mm", 7.0, "mm", "frontal"),
            ],
            "profile": [
                _make_measurement("upper_lip_height_mm", 12.0, "mm", "profile"),
            ],
        }
        result = fuse_zone_measurements(zone_def, view_data)
        assert len(result.contradictions) >= 1
        assert result.contradictions[0].metric_name == "upper_lip_height_mm"
        # Confidence should be reduced
        assert result.fusion_confidence < 1.0

    def test_missing_primary_view_uses_secondary(self):
        """If primary view is missing, use best available secondary."""
        zone_def = ZONES["Ch1"]  # profile primary, frontal secondary
        view_data = {
            "frontal": [
                _make_measurement("chin_projection_mm", -2.0, "mm", "frontal", 0.8),
            ],
        }
        result = fuse_zone_measurements(zone_def, view_data)
        assert len(result.measurements) == 1
        # Reduced confidence because primary missing
        assert result.measurements[0].confidence < 1.0

    def test_no_data_empty_result(self):
        zone_def = ZONES["T1"]
        result = fuse_zone_measurements(zone_def, {})
        assert len(result.measurements) == 0
        assert result.fusion_confidence == 0.0


# ──────────────── fuse_all_zones ────────────────


class TestFuseAllZones:
    def test_empty_input(self):
        result = fuse_all_zones({}, ["frontal"])
        assert result.zones == []
        assert result.views_used == ["frontal"]

    def test_single_zone(self):
        zone_data = {
            "T1": {
                "oblique": [_make_measurement("temporal_depth_mm", 1.0, "mm", "oblique")],
            },
        }
        result = fuse_all_zones(zone_data)
        assert len(result.zones) == 1
        assert result.zones[0].zone_id == "T1"

    def test_multiple_zones(self):
        zone_data = {
            "T1": {
                "oblique": [_make_measurement("temporal_depth_mm", 1.0, "mm", "oblique")],
            },
            "Lp1": {
                "frontal": [_make_measurement("upper_lip_height_mm", 7.0, "mm", "frontal")],
            },
            "Pf1": {
                "profile": [_make_measurement("nasolabial_angle", 95.0, "deg", "profile")],
            },
        }
        result = fuse_all_zones(zone_data)
        assert len(result.zones) == 3
        zone_ids = {z.zone_id for z in result.zones}
        assert zone_ids == {"T1", "Lp1", "Pf1"}

    def test_contradictions_aggregated(self):
        zone_data = {
            "Lp1": {
                "frontal": [_make_measurement("upper_lip_height_mm", 7.0, "mm", "frontal")],
                "profile": [_make_measurement("upper_lip_height_mm", 14.0, "mm", "profile")],
            },
        }
        result = fuse_all_zones(zone_data)
        assert len(result.contradictions) >= 1

    def test_infers_views_from_data(self):
        zone_data = {
            "T1": {
                "oblique": [_make_measurement("test", 1.0, "mm", "oblique")],
            },
            "Lp1": {
                "frontal": [_make_measurement("test", 1.0, "mm", "frontal")],
            },
        }
        result = fuse_all_zones(zone_data)
        assert set(result.views_used) == {"frontal", "oblique"}


# ──────────────── Blendshape isolation rule ────────────────


class TestBlendshapeIsolation:
    """Verify that blendshapes are NEVER passed through the fusion engine.

    The fusion engine only handles landmark geometry (ViewMeasurement).
    Blendshapes must remain view-bound in the zone_analyzer layer.
    """

    def test_fusion_has_no_blendshape_concept(self):
        """ViewMeasurement has no blendshape field — only metric+value."""
        m = _make_measurement("some_metric", 5.0)
        assert not hasattr(m, "blendshape")
        assert not hasattr(m, "blendshapes")

    def test_fusion_result_has_no_blendshapes(self):
        """FusionResult doesn't carry blendshapes anywhere."""
        result = fuse_all_zones({}, [])
        assert not hasattr(result, "blendshapes")


# ──────────────── Zone coverage ────────────────


class TestZoneCoverage:
    """Verify that all defined zones can be processed by the fusion engine."""

    def test_all_zones_have_valid_primary_view(self):
        for zone_id, zone_def in ZONES.items():
            assert zone_def.primary_view in ViewPriority, (
                f"Zone {zone_id} has invalid primary_view: {zone_def.primary_view}"
            )

    def test_fusion_zones_have_secondary_views(self):
        for zone_id, zone_def in ZONES.items():
            if zone_def.needs_fusion:
                assert len(zone_def.secondary_views) > 0, (
                    f"Zone {zone_id} needs_fusion but has no secondary_views"
                )
