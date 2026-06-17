"""Tests for multi-view 3D landmark reconstruction.

Strategy: synthetic round-trip. Take known 3D points, project them
orthographically through known rotations, then reconstruct and check we recover
the originals. Under the orthographic model the recovery is exact.
"""

import numpy as np
import pytest

from app.analysis.multiview_reconstruction import (
    reconstruct_3d,
    reconstruct_from_views,
    orthonormalize_rotation,
    view_observation_from,
    ViewObservation,
    Reconstruction3D,
    MIN_VIEW_SPREAD_DEG,
)
from app.detection.face_landmarker import DetectionResult
from app.utils.pixel_calibration import CalibrationResult


def _rot_y(deg: float) -> np.ndarray:
    """Rotation about the vertical (Y) axis — the dominant head-turn axis."""
    t = np.radians(deg)
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])


def _project(points_mm: np.ndarray, R: np.ndarray, px_per_mm: float,
             centroid_px=(500.0, 400.0)) -> np.ndarray:
    """Orthographic projection of 3D mm points to 2D pixel landmarks."""
    proj_mm = (R @ points_mm.T).T[:, :2]          # Pi @ R @ P
    return proj_mm * px_per_mm + np.asarray(centroid_px)


def _make_points(n=60, seed=42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    P = rng.normal(0.0, 30.0, size=(n, 3))
    return P - P.mean(axis=0)  # centred


class TestReconstruction:
    def test_exact_under_orthographic_model(self):
        P = _make_points()
        px_per_mm = 5.0
        views = [
            ViewObservation("frontal", _project(P, _rot_y(0), px_per_mm), _rot_y(0), px_per_mm),
            ViewObservation("oblique", _project(P, _rot_y(35), px_per_mm), _rot_y(35), px_per_mm),
            ViewObservation("profile", _project(P, _rot_y(80), px_per_mm), _rot_y(80), px_per_mm),
        ]
        rec = reconstruct_3d(views)
        assert rec is not None
        assert rec.n_views == 3
        err = np.linalg.norm(rec.points_mm - P, axis=1)
        assert err.max() < 1e-6           # exact recovery
        assert rec.reprojection_rms_mm < 1e-6

    def test_two_views_sufficient(self):
        P = _make_points(n=40)
        ppm = 6.0
        views = [
            ViewObservation("frontal", _project(P, _rot_y(0), ppm), _rot_y(0), ppm),
            ViewObservation("profile", _project(P, _rot_y(70), ppm), _rot_y(70), ppm),
        ]
        rec = reconstruct_3d(views)
        assert rec is not None
        assert np.linalg.norm(rec.points_mm - P, axis=1).max() < 1e-6

    def test_single_view_returns_none(self):
        P = _make_points(n=10)
        views = [ViewObservation("frontal", _project(P, _rot_y(0), 5.0), _rot_y(0), 5.0)]
        assert reconstruct_3d(views) is None

    def test_insufficient_angular_spread_returns_none(self):
        P = _make_points(n=10)
        ppm = 5.0
        # Two nearly-frontal views — depth is ill-conditioned.
        views = [
            ViewObservation("a", _project(P, _rot_y(0), ppm), _rot_y(0), ppm),
            ViewObservation("b", _project(P, _rot_y(3), ppm), _rot_y(3), ppm),
        ]
        assert reconstruct_3d(views) is None

    def test_missing_rotation_skipped(self):
        P = _make_points(n=10)
        ppm = 5.0
        views = [
            ViewObservation("frontal", _project(P, _rot_y(0), ppm), _rot_y(0), ppm),
            ViewObservation("oblique", _project(P, _rot_y(40), ppm), _rot_y(40), ppm),
            ViewObservation("bad", _project(P, _rot_y(40), ppm), None, ppm),  # no rotation
        ]
        rec = reconstruct_3d(views)
        assert rec is not None
        assert "bad" not in rec.views_used

    def test_noise_gives_bounded_error(self):
        P = _make_points(n=80)
        ppm = 5.0
        rng = np.random.default_rng(7)
        views = []
        for name, yaw in [("frontal", 0), ("oblique", 40), ("profile", 80)]:
            px = _project(P, _rot_y(yaw), ppm)
            px = px + rng.normal(0.0, 1.0, size=px.shape)  # 1px noise
            views.append(ViewObservation(name, px, _rot_y(yaw), ppm))
        rec = reconstruct_3d(views)
        assert rec is not None
        # 1px noise at 5px/mm ~ 0.2mm input noise → sub-mm reconstruction error
        assert np.linalg.norm(rec.points_mm - P, axis=1).mean() < 1.0
        assert rec.reprojection_rms_mm > 0.0

    def test_metric_scale_preserved(self):
        # Two points exactly 11.7mm apart in 3D should reconstruct ~11.7mm apart.
        P = np.array([[-5.85, 0.0, 2.0], [5.85, 0.0, -2.0]])  # 11.7mm in X, plus depth
        P = np.vstack([P, np.zeros((8, 3))])  # padding points for a stable solve
        P = P - P.mean(axis=0)
        ppm = 8.0
        views = [
            ViewObservation("frontal", _project(P, _rot_y(0), ppm), _rot_y(0), ppm),
            ViewObservation("profile", _project(P, _rot_y(75), ppm), _rot_y(75), ppm),
        ]
        rec = reconstruct_3d(views)
        assert rec is not None
        assert abs(rec.distance(0, 1) - np.linalg.norm(P[0] - P[1])) < 1e-4

    def test_depth_helper(self):
        P = _make_points(n=20)
        ppm = 5.0
        views = [
            ViewObservation("frontal", _project(P, _rot_y(0), ppm), _rot_y(0), ppm),
            ViewObservation("profile", _project(P, _rot_y(70), ppm), _rot_y(70), ppm),
        ]
        rec = reconstruct_3d(views)
        assert rec is not None
        expected = P[3, 2] - P[7, 2]
        assert abs(rec.depth_between(3, 7) - expected) < 1e-4


# ──────────────────────── Convention helpers ────────────────────────

class TestOrthonormalize:
    def test_recovers_pure_rotation_from_scaled(self):
        R = _rot_y(37)
        scaled = R * 2.5  # uniform scale should be removed
        out = orthonormalize_rotation(scaled)
        assert np.allclose(out, R, atol=1e-9)
        assert abs(np.linalg.det(out) - 1.0) < 1e-9

    def test_guards_against_reflection(self):
        # A matrix with negative determinant must still yield a proper rotation.
        m = np.diag([1.0, 1.0, -1.0]) @ _rot_y(20)
        out = orthonormalize_rotation(m)
        assert np.linalg.det(out) > 0.0  # proper rotation, not a reflection


class TestViewObservationFrom:
    def test_scales_normalized_landmarks_to_pixels(self):
        norm = np.array([[0.5, 0.25, 0.0], [0.1, 0.9, 0.0]])
        obs = view_observation_from("frontal", norm, 1000, 800, np.eye(4), 5.0)
        assert obs is not None
        assert np.allclose(obs.landmarks_px, [[500, 200], [100, 720]])
        assert obs.px_per_mm == 5.0
        assert np.allclose(obs.rotation, np.eye(3))

    def test_none_without_matrix(self):
        norm = np.zeros((10, 3))
        assert view_observation_from("frontal", norm, 1000, 800, None, 5.0) is None

    def test_none_without_scale(self):
        norm = np.zeros((10, 3))
        assert view_observation_from("frontal", norm, 1000, 800, np.eye(4), 0.0) is None


# ──────────────────────── reconstruct_from_views policy ────────────────────────

def _synthetic_detection(P, R, ppm, w=1000, h=1000, centroid=(500.0, 500.0)):
    """Build a DetectionResult whose normalized landmarks orthographically
    project P through R at scale ppm (z is irrelevant to the 2D solve)."""
    proj_px = (R @ P.T).T[:, :2] * ppm + np.asarray(centroid)
    norm = np.zeros((P.shape[0], 3))
    norm[:, 0] = proj_px[:, 0] / w
    norm[:, 1] = proj_px[:, 1] / h
    mat = np.eye(4)
    mat[:3, :3] = R
    return DetectionResult(
        landmarks=norm, blendshapes={}, transformation_matrix=mat,
        image_width=w, image_height=h,
    )


def _cal(method="iris", confidence=0.9, ppm=5.0):
    return CalibrationResult(px_per_mm=ppm, method=method, confidence=confidence)


class TestReconstructFromViews:
    def test_builds_and_recovers(self):
        P = _make_points(n=50)
        ppm = 5.0
        views = [
            ("frontal", _synthetic_detection(P, _rot_y(0), ppm), _cal()),
            ("oblique_left", _synthetic_detection(P, _rot_y(35), ppm), _cal()),
            ("oblique_right", _synthetic_detection(P, _rot_y(-30), ppm), _cal()),
        ]
        rec = reconstruct_from_views(views)
        assert rec is not None
        assert rec.n_views == 3
        assert set(rec.views_used) == {"frontal", "oblique_left", "oblique_right"}

    def test_profile_excluded_by_policy(self):
        P = _make_points(n=50)
        ppm = 5.0
        views = [
            ("frontal", _synthetic_detection(P, _rot_y(0), ppm), _cal()),
            ("oblique_left", _synthetic_detection(P, _rot_y(35), ppm), _cal()),
            # A perfectly valid profile observation must still be skipped.
            ("profile", _synthetic_detection(P, _rot_y(80), ppm), _cal()),
        ]
        rec = reconstruct_from_views(views)
        assert rec is not None
        assert "profile" not in rec.views_used

    def test_non_iris_calibration_skipped(self):
        P = _make_points(n=40)
        ppm = 5.0
        views = [
            ("frontal", _synthetic_detection(P, _rot_y(0), ppm), _cal()),
            ("oblique_left", _synthetic_detection(P, _rot_y(35), ppm), _cal()),
            ("oblique_right", _synthetic_detection(P, _rot_y(-30), ppm),
             _cal(method="face_width_estimate", confidence=0.95)),
        ]
        rec = reconstruct_from_views(views)
        assert rec is not None
        assert "oblique_right" not in rec.views_used

    def test_low_confidence_calibration_skipped(self):
        P = _make_points(n=40)
        ppm = 5.0
        views = [
            ("frontal", _synthetic_detection(P, _rot_y(0), ppm), _cal()),
            ("oblique_left", _synthetic_detection(P, _rot_y(35), ppm), _cal()),
            ("oblique_right", _synthetic_detection(P, _rot_y(-30), ppm),
             _cal(confidence=0.5)),
        ]
        rec = reconstruct_from_views(views)
        assert rec is not None
        assert "oblique_right" not in rec.views_used

    def test_returns_none_when_only_profile(self):
        P = _make_points(n=40)
        views = [("profile", _synthetic_detection(P, _rot_y(80), 5.0), _cal())]
        assert reconstruct_from_views(views) is None
