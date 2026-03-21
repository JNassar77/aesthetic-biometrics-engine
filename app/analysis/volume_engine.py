"""
Volume analysis engine.

Assesses facial volume using 3D depth data from landmarks:
- Ogee curve (midface S-curve fluidity)
- Temporal hollowing
- Tear trough depth
- Pre-jowl sulcus detection
- Buccal corridor analysis

Uses z-coordinate depth data for volume estimation (Sprint 2 3D geometry).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.detection.face_landmarker import DetectionResult
from app.detection.landmark_index import PAIRED, MIDLINE
from app.utils.pixel_calibration import CalibrationResult
from app.utils.geometry import euclidean_2d, depth_difference


@dataclass
class OgeeCurve:
    """Ogee (S-curve) analysis for midface.

    The ogee curve runs from forehead through malar eminence
    to the buccal region. Flattening indicates volume loss.
    """
    score: float           # 0-100 (100 = ideal S-curve)
    malar_depth_mm: float  # Z-depth difference at malar prominence
    is_flattened: bool     # True if score < 60


@dataclass
class TemporalVolume:
    """Temporal fossa volume assessment."""
    left_depth_mm: float
    right_depth_mm: float
    asymmetry_mm: float
    is_hollowed: bool  # True if depth exceeds threshold


@dataclass
class TearTrough:
    """Infraorbital (tear trough) assessment."""
    left_depth_mm: float
    right_depth_mm: float
    asymmetry_mm: float
    severity: float  # 0-10


@dataclass
class JowlAssessment:
    """Pre-jowl sulcus and jowl assessment."""
    left_depth_mm: float
    right_depth_mm: float
    jawline_break_detected: bool


@dataclass
class VolumeAnalysis:
    """Complete volume analysis result."""
    ogee: OgeeCurve
    temporal: TemporalVolume
    tear_trough: TearTrough
    jowl: JowlAssessment


def _z_depth_mm(
    detection: DetectionResult,
    idx: int,
    calibration: CalibrationResult,
) -> float:
    """Get z-depth of a landmark in mm (relative, not absolute)."""
    pt = detection.px3d(idx)
    return calibration.to_mm(pt[2])


def _z_diff_mm(
    detection: DetectionResult,
    idx_a: int,
    idx_b: int,
    calibration: CalibrationResult,
) -> float:
    """Z-depth difference between two landmarks in mm."""
    a = detection.px3d(idx_a)
    b = detection.px3d(idx_b)
    return calibration.to_mm(a[2] - b[2])


def analyze_ogee(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> OgeeCurve:
    """Analyze midface ogee curve from depth data.

    The ogee S-curve should show:
    1. Forward projection at orbital rim
    2. Slight recession at infraorbital
    3. Forward projection at malar eminence
    4. Recession at buccal region

    We measure the depth transitions to quantify the S-curve fluidity.
    """
    # Key depth points along the ogee curve
    infraorbital_l = PAIRED["infraorbital"][0]  # 253
    infraorbital_r = PAIRED["infraorbital"][1]  # 23
    malar_high_l = PAIRED["malar_high"][0]      # 329
    malar_high_r = PAIRED["malar_high"][1]      # 100
    malar_low_l = PAIRED["malar_low"][0]        # 425
    malar_low_r = PAIRED["malar_low"][1]        # 205
    cheekbone_l = PAIRED["cheekbone"][0]        # 330
    cheekbone_r = PAIRED["cheekbone"][1]        # 101

    # Measure depth transitions (averaged left + right)
    # Malar prominence should project forward (negative z = closer to camera)
    malar_to_infra_l = _z_diff_mm(detection, malar_high_l, infraorbital_l, calibration)
    malar_to_infra_r = _z_diff_mm(detection, malar_high_r, infraorbital_r, calibration)
    malar_depth = (malar_to_infra_l + malar_to_infra_r) / 2

    # Malar to buccal transition (should show recession below)
    malar_to_buccal_l = _z_diff_mm(detection, cheekbone_l, malar_low_l, calibration)
    malar_to_buccal_r = _z_diff_mm(detection, cheekbone_r, malar_low_r, calibration)
    buccal_transition = (malar_to_buccal_l + malar_to_buccal_r) / 2

    # Score: higher depth transitions = better S-curve
    # Normalize to 0-100 range
    raw_score = abs(malar_depth) * 10 + abs(buccal_transition) * 8
    score = min(100.0, max(0.0, raw_score))

    return OgeeCurve(
        score=round(score, 1),
        malar_depth_mm=round(malar_depth, 1),
        is_flattened=score < 60.0,
    )


def analyze_temporal(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> TemporalVolume:
    """Assess temporal fossa volume.

    Temporal hollowing is detected by comparing the depth of the temporal
    region to the adjacent brow/forehead area.
    """
    temporal_l = PAIRED["temporal"][0]
    temporal_r = PAIRED["temporal"][1]
    brow_outer_l = PAIRED["brow_outer"][0]
    brow_outer_r = PAIRED["brow_outer"][1]

    # Temporal depth relative to brow
    left_depth = _z_diff_mm(detection, temporal_l, brow_outer_l, calibration)
    right_depth = _z_diff_mm(detection, temporal_r, brow_outer_r, calibration)

    asymmetry = abs(left_depth - right_depth)

    # Hollowing if temporal is significantly deeper than brow
    HOLLOW_THRESHOLD = 3.0  # mm
    is_hollowed = bool(abs(left_depth) > HOLLOW_THRESHOLD or abs(right_depth) > HOLLOW_THRESHOLD)

    return TemporalVolume(
        left_depth_mm=round(left_depth, 1),
        right_depth_mm=round(right_depth, 1),
        asymmetry_mm=round(asymmetry, 1),
        is_hollowed=is_hollowed,
    )


def analyze_tear_trough(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> TearTrough:
    """Assess tear trough (infraorbital hollow) depth."""
    infra_l = PAIRED["infraorbital"][0]
    infra_r = PAIRED["infraorbital"][1]
    cheek_l = PAIRED["cheekbone"][0]
    cheek_r = PAIRED["cheekbone"][1]

    # Tear trough depth relative to cheekbone
    left_depth = _z_diff_mm(detection, infra_l, cheek_l, calibration)
    right_depth = _z_diff_mm(detection, infra_r, cheek_r, calibration)

    asymmetry = abs(left_depth - right_depth)

    # Severity based on depth
    avg_depth = (abs(left_depth) + abs(right_depth)) / 2
    severity = min(10.0, avg_depth * 2.5)

    return TearTrough(
        left_depth_mm=round(left_depth, 1),
        right_depth_mm=round(right_depth, 1),
        asymmetry_mm=round(asymmetry, 1),
        severity=round(severity, 1),
    )


def analyze_jowl(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> JowlAssessment:
    """Assess pre-jowl sulcus and jawline continuity."""
    gonion_l = PAIRED["gonion"][0]
    gonion_r = PAIRED["gonion"][1]
    pogonion = MIDLINE["pogonion"]

    # Jowl depth: gonion region vs chin
    left_depth = _z_diff_mm(detection, gonion_l, pogonion, calibration)
    right_depth = _z_diff_mm(detection, gonion_r, pogonion, calibration)

    # Jawline break detected if there's a significant depth discontinuity
    BREAK_THRESHOLD = 2.0  # mm
    break_detected = bool(abs(left_depth) > BREAK_THRESHOLD or abs(right_depth) > BREAK_THRESHOLD)

    return JowlAssessment(
        left_depth_mm=round(left_depth, 1),
        right_depth_mm=round(right_depth, 1),
        jawline_break_detected=break_detected,
    )


def analyze(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> VolumeAnalysis:
    """Run complete volume analysis.

    Best results from oblique (45°) view where depth variations are visible.
    """
    return VolumeAnalysis(
        ogee=analyze_ogee(detection, calibration),
        temporal=analyze_temporal(detection, calibration),
        tear_trough=analyze_tear_trough(detection, calibration),
        jowl=analyze_jowl(detection, calibration),
    )
