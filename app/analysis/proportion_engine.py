"""
Proportion analysis engine.

Measures facial proportions using calibrated mm measurements:
- Vertical thirds (upper, middle, lower face)
- Horizontal fifths (5 equal segments)
- Golden ratio deviation
- Lip ratio with Cupid's bow analysis

All measurements in mm via Sprint 2 iris calibration.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.detection.face_landmarker import DetectionResult
from app.detection.landmark_index import (
    MIDLINE, PAIRED, LIP_UPPER_OUTER, LIP_UPPER_INNER,
)
from app.utils.pixel_calibration import CalibrationResult
from app.utils.geometry import euclidean_2d


# Golden ratio constant
PHI = 1.618033988749895

# Ideal lip ratio (upper:lower ≈ 1:1.6)
IDEAL_LIP_RATIO = 1 / 1.6  # ≈ 0.625


@dataclass
class ThirdsAnalysis:
    """Vertical facial thirds measurement."""
    upper_mm: float       # Trichion → Glabella
    middle_mm: float      # Glabella → Subnasale
    lower_mm: float       # Subnasale → Menton
    upper_ratio: float    # Each as proportion of total
    middle_ratio: float
    lower_ratio: float
    total_height_mm: float
    deviation_from_ideal: float  # % deviation from 1:1:1


@dataclass
class FifthsAnalysis:
    """Horizontal facial fifths measurement."""
    widths_mm: list[float]  # 5 segment widths
    total_width_mm: float
    ratios: list[float]     # Each as proportion of total
    deviation_from_ideal: float  # % deviation from 1:1:1:1:1


@dataclass
class GoldenRatioAnalysis:
    """Golden ratio measurements."""
    face_height_mm: float
    face_width_mm: float
    measured_ratio: float
    golden_ratio: float
    deviation_pct: float


@dataclass
class LipAnalysis:
    """Lip proportion and Cupid's bow analysis."""
    upper_lip_height_mm: float
    lower_lip_height_mm: float
    lip_ratio: float              # upper / lower (ideal ≈ 0.625)
    lip_ratio_deviation_pct: float
    lip_width_mm: float
    cupid_bow_depth_mm: float
    cupid_bow_asymmetry_pct: float
    vermilion_to_cutaneous_ratio: float | None = None


@dataclass
class ProportionAnalysis:
    """Complete proportion analysis result."""
    thirds: ThirdsAnalysis
    fifths: FifthsAnalysis | None
    golden_ratio: GoldenRatioAnalysis
    lip: LipAnalysis


def _px_dist(detection: DetectionResult, idx_a: int, idx_b: int) -> float:
    """Pixel distance between two landmarks."""
    return euclidean_2d(detection.px(idx_a), detection.px(idx_b))


def _vertical_distance(detection: DetectionResult, idx_a: int, idx_b: int) -> float:
    """Vertical pixel distance (y-axis only) between landmarks."""
    ya = detection.px(idx_a)[1]
    yb = detection.px(idx_b)[1]
    return abs(ya - yb)


def analyze_thirds(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> ThirdsAnalysis:
    """Analyze vertical facial thirds.

    Upper:  Trichion (hairline approx) → Glabella
    Middle: Glabella → Subnasale
    Lower:  Subnasale → Menton (gnathion)
    """
    # Trichion = landmark 10 (highest reliable forehead point)
    trichion = MIDLINE["trichion_approx"]
    glabella = MIDLINE["glabella"]
    subnasale = MIDLINE["subnasale"]
    menton = MIDLINE["gnathion"]

    upper_px = _vertical_distance(detection, trichion, glabella)
    middle_px = _vertical_distance(detection, glabella, subnasale)
    lower_px = _vertical_distance(detection, subnasale, menton)

    upper_mm = calibration.to_mm(upper_px)
    middle_mm = calibration.to_mm(middle_px)
    lower_mm = calibration.to_mm(lower_px)

    total = upper_mm + middle_mm + lower_mm
    if total < 1.0:
        total = 1.0

    upper_r = upper_mm / total
    middle_r = middle_mm / total
    lower_r = lower_mm / total

    # Deviation from ideal 1:1:1 (each = 0.333)
    ideal = 1.0 / 3.0
    deviation = (
        abs(upper_r - ideal) + abs(middle_r - ideal) + abs(lower_r - ideal)
    ) / 3.0 * 100

    return ThirdsAnalysis(
        upper_mm=round(upper_mm, 1),
        middle_mm=round(middle_mm, 1),
        lower_mm=round(lower_mm, 1),
        upper_ratio=round(upper_r, 3),
        middle_ratio=round(middle_r, 3),
        lower_ratio=round(lower_r, 3),
        total_height_mm=round(total, 1),
        deviation_from_ideal=round(deviation, 1),
    )


def analyze_fifths(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> FifthsAnalysis:
    """Analyze horizontal facial fifths.

    Five segments from right ear to left ear:
    1. Right preauricular → Right eye outer
    2. Right eye outer → Right eye inner
    3. Right eye inner → Left eye inner (intercanthal)
    4. Left eye inner → Left eye outer
    5. Left eye outer → Left preauricular
    """
    # Using available landmarks (preauricular = near ear)
    r_pre = PAIRED["preauricular"][1]   # right
    r_eye_o = PAIRED["eye_outer"][1]
    r_eye_i = PAIRED["eye_inner"][1]
    l_eye_i = PAIRED["eye_inner"][0]
    l_eye_o = PAIRED["eye_outer"][0]
    l_pre = PAIRED["preauricular"][0]   # left

    segments_px = [
        abs(detection.px(r_pre)[0] - detection.px(r_eye_o)[0]),
        abs(detection.px(r_eye_o)[0] - detection.px(r_eye_i)[0]),
        abs(detection.px(r_eye_i)[0] - detection.px(l_eye_i)[0]),
        abs(detection.px(l_eye_i)[0] - detection.px(l_eye_o)[0]),
        abs(detection.px(l_eye_o)[0] - detection.px(l_pre)[0]),
    ]

    widths_mm = [calibration.to_mm(s) for s in segments_px]
    total = sum(widths_mm)
    if total < 1.0:
        total = 1.0

    ratios = [w / total for w in widths_mm]

    ideal = 0.2  # each segment = 20%
    deviation = sum(abs(r - ideal) for r in ratios) / 5.0 * 100

    return FifthsAnalysis(
        widths_mm=[round(w, 1) for w in widths_mm],
        total_width_mm=round(total, 1),
        ratios=[round(r, 3) for r in ratios],
        deviation_from_ideal=round(deviation, 1),
    )


def analyze_golden_ratio(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> GoldenRatioAnalysis:
    """Analyze face height-to-width golden ratio.

    Ideal: face_height / face_width ≈ 1.618 (phi)
    """
    # Face height: trichion to menton
    height_px = _vertical_distance(
        detection, MIDLINE["trichion_approx"], MIDLINE["gnathion"]
    )
    # Face width: bizygomatic (cheekbone to cheekbone)
    width_px = abs(
        detection.px(PAIRED["cheekbone"][0])[0]
        - detection.px(PAIRED["cheekbone"][1])[0]
    )

    height_mm = calibration.to_mm(height_px)
    width_mm = calibration.to_mm(width_px)

    if width_mm < 1.0:
        width_mm = 1.0

    ratio = height_mm / width_mm
    deviation = abs(ratio - PHI) / PHI * 100

    return GoldenRatioAnalysis(
        face_height_mm=round(height_mm, 1),
        face_width_mm=round(width_mm, 1),
        measured_ratio=round(ratio, 3),
        golden_ratio=round(PHI, 3),
        deviation_pct=round(deviation, 1),
    )


def analyze_lip(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> LipAnalysis:
    """Analyze lip proportions and Cupid's bow.

    Measurements:
    - Upper lip: stomion to labrale superius (vermilion height)
    - Lower lip: stomion to labrale inferius
    - Lip width: corner to corner
    - Cupid's bow: depth and asymmetry of the philtral columns
    """
    stomion = MIDLINE["stomion"]
    upper_lip = MIDLINE["labrale_superius"]
    lower_lip = MIDLINE["labrale_inferius"]
    l_corner = PAIRED["mouth_corner"][0]
    r_corner = PAIRED["mouth_corner"][1]

    upper_px = _vertical_distance(detection, upper_lip, stomion)
    lower_px = _vertical_distance(detection, stomion, lower_lip)
    width_px = abs(detection.px(l_corner)[0] - detection.px(r_corner)[0])

    upper_mm = calibration.to_mm(upper_px)
    lower_mm = calibration.to_mm(lower_px)
    width_mm = calibration.to_mm(width_px)

    if lower_mm < 0.1:
        lower_mm = 0.1
    lip_ratio = upper_mm / lower_mm
    ratio_dev = abs(lip_ratio - IDEAL_LIP_RATIO) / IDEAL_LIP_RATIO * 100

    # Cupid's bow analysis
    # Upper lip has peaks at the philtral columns — landmarks 37 (R) and 267 (L)
    # and a dip at the midline (landmark 0)
    cupid_mid_y = detection.px(0)[1]
    cupid_left_y = detection.px(267)[1]
    cupid_right_y = detection.px(37)[1]

    # Bow depth = how much higher the peaks are than the midline dip
    bow_depth_px = (
        (cupid_mid_y - cupid_left_y) + (cupid_mid_y - cupid_right_y)
    ) / 2.0
    bow_depth_mm = calibration.to_mm(max(0, bow_depth_px))

    # Asymmetry: difference between left and right peak heights
    peak_diff = abs(cupid_left_y - cupid_right_y)
    avg_peak_height = abs((cupid_mid_y - cupid_left_y) + (cupid_mid_y - cupid_right_y)) / 2
    if avg_peak_height < 0.5:
        avg_peak_height = 0.5
    bow_asymmetry_pct = (peak_diff / avg_peak_height) * 100

    return LipAnalysis(
        upper_lip_height_mm=round(upper_mm, 1),
        lower_lip_height_mm=round(lower_mm, 1),
        lip_ratio=round(lip_ratio, 3),
        lip_ratio_deviation_pct=round(ratio_dev, 1),
        lip_width_mm=round(width_mm, 1),
        cupid_bow_depth_mm=round(bow_depth_mm, 1),
        cupid_bow_asymmetry_pct=round(bow_asymmetry_pct, 1),
    )


def analyze(
    detection: DetectionResult,
    calibration: CalibrationResult,
    include_fifths: bool = True,
) -> ProportionAnalysis:
    """Run complete proportion analysis.

    Args:
        detection: Face landmarks (typically frontal view)
        calibration: px→mm calibration
        include_fifths: Whether to compute horizontal fifths (frontal only)

    Returns:
        Complete proportion analysis
    """
    thirds = analyze_thirds(detection, calibration)
    fifths = analyze_fifths(detection, calibration) if include_fifths else None
    golden = analyze_golden_ratio(detection, calibration)
    lip = analyze_lip(detection, calibration)

    return ProportionAnalysis(
        thirds=thirds,
        fifths=fifths,
        golden_ratio=golden,
        lip=lip,
    )
