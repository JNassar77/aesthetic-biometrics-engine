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

# Views excluded from triangulation by policy. The ~90deg profile is deliberately
# left out: at that angle the iris is too foreshortened to give a trustworthy
# px->mm scale and its far-side landmarks are largely occluded (MediaPipe guesses
# them), so including it corrupts the metric solve. Validated on real photos —
# adding the profile pushed reprojection RMS from ~2.7mm to ~17mm and the
# reconstructed interpupillary distance out of the anatomical norm. The profile
# view carries the 2D sagittal profile lines (E-line, nasolabial/chin angles)
# instead; the bilateral 45deg obliques carry the 3D depth.
RECONSTRUCTION_EXCLUDED_VIEWS = frozenset({"profile"})

# A view only contributes to triangulation if its iris calibration is reliable
# (a confident iris scale is what makes the reconstruction metric).
RECONSTRUCTION_MIN_CALIBRATION_CONFIDENCE = 0.7


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


def orthonormalize_rotation(matrix: np.ndarray) -> np.ndarray:
    """Nearest proper rotation (det=+1) to a possibly-scaled 3x3 matrix.

    MediaPipe's facial transformation matrix carries the head orientation but may
    include scale/shear; reconstruction needs a pure rotation (scale is handled
    separately by the per-view px->mm calibration). We take the closest orthonormal
    matrix via SVD and guard against an accidental reflection (det = -1).
    """
    m = np.asarray(matrix, dtype=np.float64)[:3, :3]
    U, _, Vt = np.linalg.svd(m)
    R = U @ Vt
    if np.linalg.det(R) < 0.0:
        U = U.copy()
        U[:, -1] *= -1.0
        R = U @ Vt
    return R


def view_observation_from(
    view: str,
    landmarks: np.ndarray,
    image_width: int,
    image_height: int,
    transformation_matrix: np.ndarray | None,
    px_per_mm: float,
) -> ViewObservation | None:
    """Build a ViewObservation from a detection's raw outputs.

    Centralises the (audited) convention so the orchestrator and the offline
    validation script construct observations identically:
    - landmarks_px = normalized (x, y) scaled to pixels (image space, y-down),
    - rotation     = orthonormalised head rotation from the transformation matrix,
    - px_per_mm    = the view's iris calibration scale.

    Returns None when the view lacks a transformation matrix or a usable scale
    (the caller then has one fewer view for triangulation).
    """
    if transformation_matrix is None or px_per_mm <= 0:
        return None
    lm = np.asarray(landmarks, dtype=np.float64)[:, :2] * np.array(
        [image_width, image_height], dtype=np.float64
    )
    R = orthonormalize_rotation(transformation_matrix)
    return ViewObservation(view=view, landmarks_px=lm, rotation=R, px_per_mm=px_per_mm)


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


def reconstruct_from_views(views) -> Reconstruction3D | None:
    """Build observations from posed, iris-calibrated views and triangulate.

    Args:
        views: iterable of (view_name, detection, calibration). Each detection
               must expose .landmarks, .image_width, .image_height and
               .transformation_matrix; each calibration .method, .confidence and
               .px_per_mm.

    Applies the reconstruction policy (skip excluded views, require a reliable
    iris calibration) and then runs reconstruct_3d. Returns None if fewer than
    two qualifying views remain or the geometry is ill-conditioned — the caller
    then falls back to the per-view relative-z (estimated) depth.
    """
    observations: list[ViewObservation] = []
    for view_name, detection, calibration in views:
        if view_name in RECONSTRUCTION_EXCLUDED_VIEWS:
            continue
        if detection is None or calibration is None:
            continue
        if (
            calibration.method != "iris"
            or calibration.confidence < RECONSTRUCTION_MIN_CALIBRATION_CONFIDENCE
        ):
            continue
        obs = view_observation_from(
            view_name,
            detection.landmarks,
            detection.image_width,
            detection.image_height,
            detection.transformation_matrix,
            calibration.px_per_mm,
        )
        if obs is not None:
            observations.append(obs)

    return reconstruct_3d(observations)
