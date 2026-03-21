"""
Profile analysis engine.

Measures profile-specific metrics from lateral (90°) view:
- Ricketts E-line (lip position relative to nose-chin line)
- Nasolabial angle
- Chin projection (pogonion position)
- Nasal dorsum analysis (hump/saddle detection)
- Lip projection relative to Steiner line
- Cervicomental angle (chin-neck junction)

All measurements in mm via iris calibration (Sprint 2).
Uses 3D geometry where z-depth adds value (Sprint 2).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.detection.face_landmarker import DetectionResult
from app.detection.landmark_index import MIDLINE
from app.utils.pixel_calibration import CalibrationResult
from app.utils.geometry import (
    euclidean_2d,
    angle_between_points,
    point_to_line_distance,
)


@dataclass
class ELineAnalysis:
    """Ricketts E-line (Esthetic line) measurement.

    E-line runs from nose tip (pronasale) to chin (pogonion).
    Ideally, upper lip is 4mm behind and lower lip 2mm behind.
    """
    upper_lip_to_eline_mm: float  # Negative = behind line (ideal)
    lower_lip_to_eline_mm: float
    upper_lip_ideal: bool
    lower_lip_ideal: bool


@dataclass
class NasalProfile:
    """Nasal profile measurements."""
    nasolabial_angle_deg: float          # Ideal: 90-105°
    nasofrontal_angle_deg: float         # Ideal: 115-135°
    nasal_projection_ratio: float        # Goode ratio: projection / length
    dorsum_deviation_mm: float           # 0 = straight, positive = hump, negative = saddle


@dataclass
class ChinAnalysis:
    """Chin position and projection."""
    chin_projection_mm: float      # Distance from subnasale vertical to pogonion
    mentolabial_depth_mm: float    # Depth of mentolabial sulcus
    chin_height_mm: float          # Stomion to gnathion


@dataclass
class CervicoMentalAnalysis:
    """Chin-neck angle assessment."""
    cervicomental_angle_deg: float  # Ideal: 105-120°
    is_obtuse: bool                 # True if angle > 130° (indicates laxity)


@dataclass
class ProfileAnalysis:
    """Complete profile analysis result."""
    e_line: ELineAnalysis
    nasal: NasalProfile
    chin: ChinAnalysis
    cervicomental: CervicoMentalAnalysis | None
    steiner_upper_lip_mm: float | None  # Lip projection relative to Steiner line


def analyze_e_line(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> ELineAnalysis:
    """Measure lip position relative to Ricketts E-line.

    E-line: pronasale (nose tip) → pogonion (chin).
    Lips should sit behind (negative distance).
    """
    nose_tip = detection.px(MIDLINE["pronasale"])
    pogonion = detection.px(MIDLINE["pogonion"])
    upper_lip = detection.px(MIDLINE["labrale_superius"])
    lower_lip = detection.px(MIDLINE["labrale_inferius"])

    upper_dist_px = point_to_line_distance(upper_lip, nose_tip, pogonion)
    lower_dist_px = point_to_line_distance(lower_lip, nose_tip, pogonion)

    upper_mm = calibration.to_mm(upper_dist_px)
    lower_mm = calibration.to_mm(lower_dist_px)

    return ELineAnalysis(
        upper_lip_to_eline_mm=round(upper_mm, 1),
        lower_lip_to_eline_mm=round(lower_mm, 1),
        upper_lip_ideal=(-6.0 <= upper_mm <= -1.0),
        lower_lip_ideal=(-4.0 <= lower_mm <= 0.0),
    )


def analyze_nasal_profile(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> NasalProfile:
    """Analyze nasal profile metrics."""
    glabella = detection.px(MIDLINE["glabella"])
    nasion = detection.px(MIDLINE["nasion"])
    rhinion = detection.px(MIDLINE["rhinion"])
    pronasale = detection.px(MIDLINE["pronasale"])
    subnasale = detection.px(MIDLINE["subnasale"])
    upper_lip = detection.px(MIDLINE["labrale_superius"])

    # Nasolabial angle: columella (subnasale→pronasale) ↔ upper lip line
    nasolabial = angle_between_points(subnasale, pronasale, upper_lip)

    # Nasofrontal angle: glabella-nasion-dorsum
    nasofrontal = angle_between_points(nasion, glabella, rhinion)

    # Nasal projection ratio (Goode): projection / nasal length
    # Projection = horizontal distance from alar base to tip
    projection_px = abs(pronasale[0] - subnasale[0])
    nasal_length_px = euclidean_2d(nasion, pronasale)
    goode_ratio = projection_px / max(nasal_length_px, 1.0)

    # Dorsum deviation: distance of rhinion from nasion-pronasale line
    # Positive = dorsal hump, negative = saddle
    dorsum_dev_px = point_to_line_distance(rhinion, nasion, pronasale)
    dorsum_dev_mm = calibration.to_mm(dorsum_dev_px)

    return NasalProfile(
        nasolabial_angle_deg=round(nasolabial, 1),
        nasofrontal_angle_deg=round(nasofrontal, 1),
        nasal_projection_ratio=round(goode_ratio, 3),
        dorsum_deviation_mm=round(dorsum_dev_mm, 1),
    )


def analyze_chin(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> ChinAnalysis:
    """Analyze chin projection and shape."""
    subnasale = detection.px(MIDLINE["subnasale"])
    pogonion = detection.px(MIDLINE["pogonion"])
    gnathion = detection.px(MIDLINE["gnathion"])
    stomion = detection.px(MIDLINE["stomion"])
    mentolabial = detection.px(MIDLINE["mentolabial_sulcus"])

    # Chin projection: horizontal distance of pogonion from subnasale vertical
    chin_proj_px = pogonion[0] - subnasale[0]
    chin_proj_mm = calibration.to_mm(chin_proj_px)

    # Mentolabial depth: perpendicular distance of mentolabial sulcus
    # from the line between lower lip and pogonion
    lower_lip = detection.px(MIDLINE["labrale_inferius"])
    mento_depth_px = abs(point_to_line_distance(mentolabial, lower_lip, pogonion))
    mento_depth_mm = calibration.to_mm(mento_depth_px)

    # Chin height: stomion to gnathion
    chin_height_px = abs(gnathion[1] - stomion[1])
    chin_height_mm = calibration.to_mm(chin_height_px)

    return ChinAnalysis(
        chin_projection_mm=round(chin_proj_mm, 1),
        mentolabial_depth_mm=round(mento_depth_mm, 1),
        chin_height_mm=round(chin_height_mm, 1),
    )


def analyze_cervicomental(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> CervicoMentalAnalysis | None:
    """Analyze cervicomental angle (chin-neck junction).

    Note: This requires landmarks near the neck/submental area.
    MediaPipe doesn't provide neck landmarks directly — we approximate
    using the lowest jaw landmarks and gnathion.
    Returns None if insufficient landmarks are visible.
    """
    gnathion = detection.px(MIDLINE["gnathion"])
    pogonion = detection.px(MIDLINE["pogonion"])
    mentolabial = detection.px(MIDLINE["mentolabial_sulcus"])

    # Approximate neck point as a point below and behind gnathion
    # In profile view, this is a rough estimate
    neck_approx = (gnathion[0] - 20, gnathion[1] + 40)

    angle = angle_between_points(gnathion, pogonion, neck_approx)

    return CervicoMentalAnalysis(
        cervicomental_angle_deg=round(angle, 1),
        is_obtuse=angle > 130.0,
    )


def analyze_steiner_line(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> float | None:
    """Measure upper lip projection relative to Steiner (S-line).

    Steiner line: subnasale → pogonion.
    Upper lip should touch or be slightly in front of this line.
    """
    subnasale = detection.px(MIDLINE["subnasale"])
    pogonion = detection.px(MIDLINE["pogonion"])
    upper_lip = detection.px(MIDLINE["labrale_superius"])

    dist_px = point_to_line_distance(upper_lip, subnasale, pogonion)
    return round(calibration.to_mm(dist_px), 1)


def analyze(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> ProfileAnalysis:
    """Run complete profile analysis.

    Should be called with profile (90°) view detection results.
    """
    return ProfileAnalysis(
        e_line=analyze_e_line(detection, calibration),
        nasal=analyze_nasal_profile(detection, calibration),
        chin=analyze_chin(detection, calibration),
        cervicomental=analyze_cervicomental(detection, calibration),
        steiner_upper_lip_mm=analyze_steiner_line(detection, calibration),
    )
