"""
Symmetry analysis engine.

Measures bilateral symmetry across 6 axes for paired facial structures.
Uses calibrated mm measurements (Sprint 2) for clinically meaningful values.

Axes of symmetry:
1. Brow height (Bw1 left vs right)
2. Eye aperture (palpebral fissure)
3. Cheekbone prominence (Ck1/Ck2)
4. Nasolabial fold depth (Ns1)
5. Lip corner position (Lp3)
6. Jawline contour (Jl1)

Also provides:
- Per-zone asymmetry scores
- Dynamic asymmetry from blendshapes (Sprint 3.4)
- Global symmetry index (0-100)
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass

from app.detection.face_landmarker import DetectionResult
from app.detection.landmark_index import PAIRED, MIDLINE
from app.utils.pixel_calibration import CalibrationResult
from app.utils.geometry import euclidean_2d


@dataclass
class SymmetryMeasurement:
    """Single bilateral symmetry measurement."""
    axis_name: str
    left_value_mm: float
    right_value_mm: float
    difference_mm: float
    difference_pct: float
    is_clinically_significant: bool


@dataclass
class DynamicAsymmetry:
    """Blendshape-based asymmetry (expression/muscle tone differences)."""
    blendshape_name: str
    left_value: float
    right_value: float
    difference: float


@dataclass
class SymmetryAnalysis:
    """Complete symmetry analysis result."""
    measurements: list[SymmetryMeasurement]
    dynamic_asymmetries: list[DynamicAsymmetry]
    global_symmetry_index: float  # 0-100 (100 = perfect symmetry)


# Clinical significance thresholds (mm)
SIGNIFICANCE_THRESHOLD_MM = 2.0  # >2mm difference is clinically noticeable
SIGNIFICANCE_THRESHOLD_PCT = 8.0  # >8% difference is clinically noticeable

# Blendshape pairs for dynamic asymmetry (Sprint 3.4)
BLENDSHAPE_PAIRS = [
    ("browDownLeft", "browDownRight"),
    ("browOuterUpLeft", "browOuterUpRight"),
    ("cheekSquintLeft", "cheekSquintRight"),
    ("eyeBlinkLeft", "eyeBlinkRight"),
    ("eyeSquintLeft", "eyeSquintRight"),
    ("mouthSmileLeft", "mouthSmileRight"),
    ("mouthFrownLeft", "mouthFrownRight"),
    ("noseSneerLeft", "noseSneerRight"),
]

# Symmetry axes: each defines a bilateral landmark pair and what to measure
SYMMETRY_AXES = [
    {
        "name": "brow_height",
        "landmark_left": PAIRED["brow_peak"][0],    # 282
        "landmark_right": PAIRED["brow_peak"][1],    # 52
        "reference": MIDLINE["glabella"],             # midline reference
        "description": "Brow peak height relative to glabella",
    },
    {
        "name": "eye_width",
        "left_pair": (PAIRED["eye_inner"][0], PAIRED["eye_outer"][0]),   # left eye
        "right_pair": (PAIRED["eye_inner"][1], PAIRED["eye_outer"][1]),  # right eye
        "description": "Palpebral fissure width",
    },
    {
        "name": "cheekbone_height",
        "landmark_left": PAIRED["cheekbone"][0],
        "landmark_right": PAIRED["cheekbone"][1],
        "reference": MIDLINE["pronasale"],
        "description": "Cheekbone height relative to nose tip",
    },
    {
        "name": "nasolabial_region",
        "left_pair": (PAIRED["alar"][0], PAIRED["mouth_corner"][0]),
        "right_pair": (PAIRED["alar"][1], PAIRED["mouth_corner"][1]),
        "description": "Alar to mouth corner distance (nasolabial region)",
    },
    {
        "name": "mouth_corner_height",
        "landmark_left": PAIRED["mouth_corner"][0],
        "landmark_right": PAIRED["mouth_corner"][1],
        "reference": MIDLINE["stomion"],
        "description": "Mouth corner vertical position",
    },
    {
        "name": "gonion_height",
        "landmark_left": PAIRED["gonion"][0],
        "landmark_right": PAIRED["gonion"][1],
        "reference": MIDLINE["gnathion"],
        "description": "Mandibular angle height relative to chin",
    },
]


def _measure_distance_to_reference(
    detection: DetectionResult,
    landmark_idx: int,
    reference_idx: int,
    calibration: CalibrationResult,
) -> float:
    """Measure vertical distance from landmark to reference point in mm."""
    pt = detection.px(landmark_idx)
    ref = detection.px(reference_idx)
    distance_px = abs(pt[1] - ref[1])
    return calibration.to_mm(distance_px)


def _measure_pair_distance(
    detection: DetectionResult,
    idx_a: int,
    idx_b: int,
    calibration: CalibrationResult,
) -> float:
    """Measure distance between two landmarks in mm."""
    pa = detection.px(idx_a)
    pb = detection.px(idx_b)
    return calibration.to_mm(euclidean_2d(pa, pb))


def analyze_static_symmetry(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> list[SymmetryMeasurement]:
    """Analyze bilateral symmetry across 6 axes.

    Args:
        detection: Face landmark detection result
        calibration: Pixel-to-mm calibration

    Returns:
        List of symmetry measurements per axis
    """
    measurements = []

    for axis in SYMMETRY_AXES:
        if "left_pair" in axis:
            # Distance-based measurement (e.g., eye width, nasolabial)
            left_mm = _measure_pair_distance(
                detection, axis["left_pair"][0], axis["left_pair"][1], calibration
            )
            right_mm = _measure_pair_distance(
                detection, axis["right_pair"][0], axis["right_pair"][1], calibration
            )
        else:
            # Height-based measurement relative to midline reference
            left_mm = _measure_distance_to_reference(
                detection, axis["landmark_left"], axis["reference"], calibration
            )
            right_mm = _measure_distance_to_reference(
                detection, axis["landmark_right"], axis["reference"], calibration
            )

        diff_mm = abs(left_mm - right_mm)
        avg = (left_mm + right_mm) / 2 if (left_mm + right_mm) > 0 else 1.0
        diff_pct = (diff_mm / avg) * 100

        measurements.append(SymmetryMeasurement(
            axis_name=axis["name"],
            left_value_mm=round(left_mm, 2),
            right_value_mm=round(right_mm, 2),
            difference_mm=round(diff_mm, 2),
            difference_pct=round(diff_pct, 1),
            is_clinically_significant=(
                diff_mm > SIGNIFICANCE_THRESHOLD_MM
                or diff_pct > SIGNIFICANCE_THRESHOLD_PCT
            ),
        ))

    return measurements


def analyze_dynamic_asymmetry(
    blendshapes: dict[str, float],
    threshold: float = 0.10,
) -> list[DynamicAsymmetry]:
    """Analyze asymmetry in muscle activation from blendshapes.

    Note: Blendshapes are view-bound — this should only be called
    with blendshapes from a single view (typically frontal).

    Args:
        blendshapes: 52 blendshape coefficients from one view
        threshold: Minimum difference to report

    Returns:
        List of dynamic asymmetries above threshold
    """
    asymmetries = []

    for left_name, right_name in BLENDSHAPE_PAIRS:
        left_val = blendshapes.get(left_name, 0.0)
        right_val = blendshapes.get(right_name, 0.0)
        diff = abs(left_val - right_val)

        if diff > threshold:
            asymmetries.append(DynamicAsymmetry(
                blendshape_name=left_name.replace("Left", ""),
                left_value=round(left_val, 3),
                right_value=round(right_val, 3),
                difference=round(diff, 3),
            ))

    return asymmetries


def compute_symmetry_index(measurements: list[SymmetryMeasurement]) -> float:
    """Compute global symmetry index from individual axis measurements.

    Returns 0-100 where 100 = perfect bilateral symmetry.
    """
    if not measurements:
        return 100.0

    # Each axis contributes proportionally, weighted by clinical impact
    AXIS_WEIGHTS = {
        "brow_height": 1.0,
        "eye_width": 1.2,
        "cheekbone_height": 1.3,
        "nasolabial_region": 1.1,
        "mouth_corner_height": 1.0,
        "gonion_height": 0.8,
    }

    weighted_deviations = 0.0
    total_weight = 0.0

    for m in measurements:
        weight = AXIS_WEIGHTS.get(m.axis_name, 1.0)
        # Normalize: 0% deviation = 0, 15%+ deviation = max penalty
        normalized = min(m.difference_pct / 15.0, 1.0)
        weighted_deviations += normalized * weight
        total_weight += weight

    if total_weight == 0:
        return 100.0

    avg_deviation = weighted_deviations / total_weight
    return round(max(0.0, (1.0 - avg_deviation) * 100), 1)


def analyze(
    detection: DetectionResult,
    calibration: CalibrationResult,
    blendshapes: dict[str, float] | None = None,
) -> SymmetryAnalysis:
    """Run complete symmetry analysis.

    Args:
        detection: Face landmarks from one view
        calibration: px→mm calibration
        blendshapes: Optional blendshapes for dynamic asymmetry (frontal only)

    Returns:
        Complete symmetry analysis
    """
    static = analyze_static_symmetry(detection, calibration)
    dynamic = analyze_dynamic_asymmetry(blendshapes or {})
    index = compute_symmetry_index(static)

    return SymmetryAnalysis(
        measurements=static,
        dynamic_asymmetries=dynamic,
        global_symmetry_index=index,
    )
