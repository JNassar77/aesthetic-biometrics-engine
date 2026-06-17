"""Tests for wiring the analysis engines to the metric 3D reconstruction (Task 10).

Focus: the depth-sign convention (the reconstruction uses +z = forward, the engine
logic expects negative = forward, so the wiring NEGATES the reconstructed depth),
the depth_source flag, graceful fallback to relative z, and that the zone analyzer
accepts bilateral obliques + a reconstruction without disturbing the fusion.
"""

import numpy as np
import pytest

from app.analysis import volume_engine, zone_analyzer
from app.analysis.multiview_reconstruction import Reconstruction3D
from app.analysis.zone_analyzer import ViewInput
from app.detection.landmark_index import PAIRED, MIDLINE
from tests.fixtures.synthetic import (
    make_symmetric_face, make_calibration,
)


def _reconstruction_with(depths: dict[int, float], n_points: int = 478) -> Reconstruction3D:
    """Build a Reconstruction3D whose z-coordinates are set for given landmarks.

    +z = forward (anterior), matching the validated real-photo convention
    (nose tip ~+47mm). All other coordinates are zero.
    """
    pts = np.zeros((n_points, 3), dtype=np.float64)
    for idx, z in depths.items():
        pts[idx, 2] = z
    return Reconstruction3D(
        points_mm=pts,
        views_used=["frontal", "oblique_left", "oblique_right"],
        n_views=3,
        angular_spread_deg=65.0,
        reprojection_rms_mm=2.5,
    )


class TestDepthSignConvention:
    def test_temporal_hollow_sign_matches_engine_convention(self):
        """A temporal region set 5mm POSTERIOR to the brow (smaller +z) must read
        as a positive 'depth' (recessed) after the negate, and trip is_hollowed."""
        t_l, t_r = PAIRED["temporal"]
        b_l, b_r = PAIRED["brow_outer"]
        rec = _reconstruction_with({
            t_l: -5.0, t_r: -5.0,   # temporal 5mm behind brow (brow at z=0)
            b_l: 0.0, b_r: 0.0,
        })
        det = make_symmetric_face()
        cal = make_calibration()
        result = volume_engine.analyze_temporal(det, cal, rec)
        # depth = -(z_temporal - z_brow) = -(-5 - 0) = +5  → recessed
        assert result.left_depth_mm == pytest.approx(5.0, abs=1e-6)
        assert result.right_depth_mm == pytest.approx(5.0, abs=1e-6)
        assert result.is_hollowed is True

    def test_flat_temporal_not_hollow(self):
        t_l, t_r = PAIRED["temporal"]
        b_l, b_r = PAIRED["brow_outer"]
        rec = _reconstruction_with({t_l: 0.0, t_r: 0.0, b_l: 0.0, b_r: 0.0})
        result = volume_engine.analyze_temporal(make_symmetric_face(), make_calibration(), rec)
        assert result.is_hollowed is False

    def test_tear_trough_depth_uses_reconstruction(self):
        inf_l, inf_r = PAIRED["infraorbital"]
        ck_l, ck_r = PAIRED["cheekbone"]
        # Infraorbital 3mm behind cheekbone → tear-trough hollow.
        rec = _reconstruction_with({inf_l: -3.0, inf_r: -3.0, ck_l: 0.0, ck_r: 0.0})
        result = volume_engine.analyze_tear_trough(make_symmetric_face(), make_calibration(), rec)
        assert result.left_depth_mm == pytest.approx(3.0, abs=1e-6)
        assert result.severity > 0


class TestDepthSource:
    def test_depth_source_3d_when_reconstruction_present(self):
        rec = _reconstruction_with({})
        result = volume_engine.analyze(make_symmetric_face(), make_calibration(), rec)
        assert result.depth_source == "multi_view_3d"

    def test_depth_source_relative_z_fallback(self):
        result = volume_engine.analyze(make_symmetric_face(), make_calibration())
        assert result.depth_source == "relative_z"

    def test_fallback_still_produces_values(self):
        """Without a reconstruction the engine must still work (relative z)."""
        result = volume_engine.analyze(make_symmetric_face(), make_calibration())
        assert result.ogee is not None
        assert isinstance(result.temporal.is_hollowed, bool)


class TestZoneAnalyzerBilateralObliques:
    def test_bilateral_obliques_accepted(self):
        frontal = ViewInput(make_symmetric_face(), make_calibration(),
                            make_symmetric_face().blendshapes)
        ol = ViewInput(make_symmetric_face(), make_calibration(), {})
        orr = ViewInput(make_symmetric_face(), make_calibration(), {})
        rec = _reconstruction_with({})
        report = zone_analyzer.analyze(
            frontal=frontal, oblique_left=ol, oblique_right=orr, reconstruction=rec,
        )
        # Canonical oblique is derived → volume zones present, "oblique" view used.
        assert "oblique" in report.views_analyzed
        assert report.aesthetic_score >= 0

    def test_canonical_oblique_prefers_higher_confidence(self):
        chosen = zone_analyzer._pick_canonical_oblique(
            oblique_left=ViewInput(make_symmetric_face(), make_calibration(confidence=0.80), {}),
            oblique_right=ViewInput(make_symmetric_face(), make_calibration(confidence=0.95), {}),
            oblique=None,
        )
        assert chosen.calibration.confidence == 0.95

    def test_generic_oblique_still_works(self):
        """Back-compat: a single generic oblique still drives the volume engine."""
        frontal = ViewInput(make_symmetric_face(), make_calibration(),
                            make_symmetric_face().blendshapes)
        obl = ViewInput(make_symmetric_face(), make_calibration(), {})
        report = zone_analyzer.analyze(frontal=frontal, oblique=obl)
        assert "oblique" in report.views_analyzed
