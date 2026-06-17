"""
Multi-view 3D landmark reconstruction.

Reconstructs a metric 3D point cloud of the 478 face landmarks by triangulating
their 2D positions across the frontal / oblique / profile views.

Why this works for our setup (the hard parts are free):
- CORRESPONDENCES: MediaPipe returns the same 478 semantic landmarks in every
  view, so point matches across views require no feature matching.
- ROTATION: each view's facial transformation matrix gives the head orientation
  R_v (3x3) relative to the camera.
- METRIC SCALE: the per-view iris calibration (px->mm) puts every view on a
  common millimetre scale, removing the scale ambiguity of structure-from-motion.

Model (orthographic / weak-perspective projection):
    For a 3D point P (mm, in the face frame), its centred 2D observation in
    view v (also in mm) is

        obs_v = Pi @ R_v @ P            with  Pi = [[1,0,0],[0,1,0]]

    Stacking >=2 views gives an over-determined linear system per point,
    solved by least squares:  P = pinv([Pi R_1; Pi R_2; ...]) @ [obs_1; obs_2; ...]

LIMITATION (honest): orthographic projection ignores perspective foreshortening,
so depth (Z) carries an approximation error that grows with face-depth / camera
distance. Synthetic round-trip tests prove exactness under the orthographic model;
perspective refinement (bundle adjustment) + clinical mm validation are Phase 2,
and require real captured photos. Until validated, depth measurements derived from
this stay flagged (see EXPERIMENTAL_MEASUREMENTS / estimated).

This module is pure geometry — deterministic and auditable (no ML black box).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Iris landmark indices (MediaPipe refine_landmarks); horizontal limbus points.
LEFT_IRIS = (469, 471)
RIGHT_IRIS = (474, 476)

# Orthographic projection: keep X, Y after rotation.
_PI = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

# Minimum angular spread (deg) between views to triangulate depth meaningfully.
MIN_VIEW_SPREAD_DEG = 10.0


@dataclass
class ViewObservation:
    """One view's input to reconstruction."""
    view: str                 # "frontal" | "oblique" | "profile"
    landmarks_px: np.ndarray  # (N, 2) landmark pixel coordinates
    rotation: np.ndarray      # (3, 3) head rotation from the transformation matrix
    px_per_mm: float          # per-view iris calibration scale


@dataclass
class Reconstruction3D:
    """Metric 3D reconstruction result."""
    points_mm: np.ndarray      # (N, 3) metric landmark coordinates in mm
    views_used: list[str]
    n_views: int
    angular_spread_deg: float  # spread of view orientations; higher = better depth
    reprojection_rms_mm: float # mean reprojection residual in mm (quality signal)

    def depth_between(self, idx_a: int, idx_b: int) -> float:
        """Signed Z-depth difference (mm) between two landmarks."""
        return float(self.points_mm[idx_a, 2] - self.points_mm[idx_b, 2])

    def distance(self, idx_a: int, idx_b: int) -> float:
        """Euclidean 3D distance (mm) between two landmarks."""
        return float(np.linalg.norm(self.points_mm[idx_a] - self.points_mm[idx_b]))


def _rotation_angle_between(Ra: np.ndarray, Rb: np.ndarray) -> float:
    """Geodesic angle (deg) between two rotations — convention-independent."""
    R_rel = Ra.T @ Rb
    cos_angle = (np.trace(R_rel) - 1.0) / 2.0
    return float(np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0))))


def _angular_spread(rotations: list[np.ndarray]) -> float:
    """Max pairwise rotation angle across views (deg)."""
    if len(rotations) < 2:
        return 0.0
    return max(
        _rotation_angle_between(rotations[i], rotations[j])
        for i in range(len(rotations))
        for j in range(i + 1, len(rotations))
    )


def reconstruct_3d(views: list[ViewObservation]) -> Reconstruction3D | None:
    """Reconstruct metric 3D landmarks from >=2 calibrated, posed views.

    Args:
        views: per-view observations (2D landmarks + rotation + px_per_mm).
               Need at least two views with a valid rotation and enough angular
               spread; otherwise returns None (caller falls back to 2D/estimated).

    Returns:
        Reconstruction3D, or None if reconstruction is not possible.
    """
    usable = [
        v for v in views
        if v.rotation is not None
        and v.landmarks_px is not None
        and v.px_per_mm > 0
    ]
    if len(usable) < 2:
        return None

    rotations = [v.rotation for v in usable]
    spread = _angular_spread(rotations)
    if spread < MIN_VIEW_SPREAD_DEG:
        # Views too similar (e.g. two near-frontal) — depth is ill-conditioned.
        return None

    n_points = usable[0].landmarks_px.shape[0]

    # Per view: centre landmarks and convert px -> mm (common metric scale).
    centred_mm: list[np.ndarray] = []
    for v in usable:
        lm = np.asarray(v.landmarks_px, dtype=np.float64)
        centred = (lm - lm.mean(axis=0)) / v.px_per_mm  # (N, 2) in mm
        centred_mm.append(centred)

    # Design matrix M = [Pi R_1; Pi R_2; ...]  (2V, 3)
    M = np.vstack([_PI @ R for R in rotations])
    M_pinv = np.linalg.pinv(M)  # (3, 2V)

    # Solve each landmark independently (vectorised): obs is (N, 2V).
    obs = np.hstack(centred_mm)        # (N, 2V)
    points = obs @ M_pinv.T            # (N, 3) metric mm in the face frame

    # Reprojection residual as a quality signal.
    reproj = points @ M.T              # (N, 2V)
    rms = float(np.sqrt(np.mean((reproj - obs) ** 2)))

    return Reconstruction3D(
        points_mm=points,
        views_used=[v.view for v in usable],
        n_views=len(usable),
        angular_spread_deg=round(spread, 1),
        reprojection_rms_mm=round(rms, 3),
    )
