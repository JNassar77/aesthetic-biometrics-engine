"""Tests for frontend overlay data — injection points + heatmap (Task 12)."""

from types import SimpleNamespace

import pytest

from app.analysis.overlay import build_overlay, _severity_color
from app.models.zone_models import ZoneResult
from tests.fixtures.synthetic import make_symmetric_face


def _zone(zone_id, name, region, severity, view):
    return ZoneResult(
        zone_id=zone_id, zone_name=name, region=region,
        severity=severity, primary_view=view,
    )


def _report(*zones):
    return SimpleNamespace(zones=list(zones))


class TestSeverityColor:
    def test_bands(self):
        assert _severity_color(8.0) == "#dc2626"   # high
        assert _severity_color(4.0) == "#f59e0b"   # medium
        assert _severity_color(1.0) == "#22c55e"   # low


class TestBuildOverlay:
    def test_zone_with_landmarks_produces_points_and_centroid(self):
        det = make_symmetric_face()
        report = _report(_zone("Tt1", "Tear Trough", "midface", 6.5, "frontal"))
        ov = build_overlay(report, {"frontal": det})

        assert len(ov.zones) == 1
        z = ov.zones[0]
        assert z.zone_id == "Tt1"
        assert z.view == "frontal"
        assert z.color_code == "#dc2626"
        assert z.intensity == pytest.approx(0.65)
        assert len(z.injection_points) >= 1
        # coordinates normalized [0,1]
        for p in z.injection_points:
            assert 0.0 <= p.x <= 1.0 and 0.0 <= p.y <= 1.0
        assert 0.0 <= z.centroid_x <= 1.0 and 0.0 <= z.centroid_y <= 1.0

    def test_image_dimensions_recorded(self):
        det = make_symmetric_face(image_size=1234)
        report = _report(_zone("Ck2", "Zygomatic Eminence", "midface", 3.0, "oblique"))
        ov = build_overlay(report, {"oblique": det})
        assert ov.image_dimensions["oblique"] == {"width": 1234, "height": 1234}

    def test_zone_without_landmark_mapping_skipped(self):
        det = make_symmetric_face()
        # Fo1 (Forehead) has no entry in ZONE_LANDMARKS → no injection points.
        report = _report(_zone("Fo1", "Forehead", "upper_face", 4.0, "frontal"))
        ov = build_overlay(report, {"frontal": det})
        assert ov.zones == []

    def test_falls_back_to_frontal_when_primary_view_missing(self):
        det = make_symmetric_face()
        # Ck2 is oblique-primary, but only frontal was captured.
        report = _report(_zone("Ck2", "Zygomatic Eminence", "midface", 5.0, "oblique"))
        ov = build_overlay(report, {"frontal": det})
        assert len(ov.zones) == 1
        assert ov.zones[0].view == "frontal"

    def test_zone_skipped_when_no_detection_available(self):
        report = _report(_zone("Tt1", "Tear Trough", "midface", 6.5, "profile"))
        ov = build_overlay(report, {})  # no detections at all
        assert ov.zones == []

    def test_multiple_zones_ranked_preserved(self):
        det = make_symmetric_face()
        report = _report(
            _zone("Tt1", "Tear Trough", "midface", 6.5, "frontal"),
            _zone("Lp1", "Upper Lip", "lower_face", 2.0, "frontal"),
        )
        ov = build_overlay(report, {"frontal": det})
        ids = [z.zone_id for z in ov.zones]
        assert ids == ["Tt1", "Lp1"]
        assert ov.zones[0].color_code == "#dc2626"
        assert ov.zones[1].color_code == "#22c55e"
