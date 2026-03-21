"""
Aging pattern analysis engine.

Detects aging indicators from:
1. Blendshape patterns → muscle tonus profile
2. Gravitational drift → landmark displacement downward
3. Periorbital analysis → crow's feet potential, under-lid laxity

Blendshapes are view-bound (NOT fused) — this engine processes
one view at a time, typically the frontal view.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.detection.face_landmarker import DetectionResult
from app.detection.landmark_index import PAIRED, MIDLINE
from app.utils.pixel_calibration import CalibrationResult
from app.utils.geometry import euclidean_2d


@dataclass
class MuscleTonus:
    """Muscle tonus profile from blendshapes.

    Maps blendshape activation patterns to aging indicators:
    - Hyperactive frontalis → compensating for brow ptosis
    - Hyperactive corrugator → glabellar lines
    - Low orbicularis tone → perioral aging
    """
    frontalis_compensation: float  # 0-1: higher = more brow compensation
    corrugator_activity: float     # 0-1: glabellar line indicator
    orbicularis_tone: float        # 0-1: perioral muscle tone
    masseter_activity: float       # 0-1: jaw clenching indicator
    overall_muscle_age_indicator: float  # 0-10 severity


@dataclass
class GravitationalDrift:
    """Landmark displacement analysis for gravitational aging.

    Compares actual landmark positions to ideal (youthful) ratios
    to detect downward migration of facial structures.
    """
    brow_descent_mm: float      # How much brows have dropped
    malar_descent_mm: float     # Midface ptosis indicator
    jowl_descent_mm: float      # Lower face laxity
    overall_drift_score: float  # 0-10 severity


@dataclass
class PeriorbitalAging:
    """Periorbital aging assessment."""
    crow_feet_potential: float      # 0-1 from eye squint blendshapes
    under_lid_laxity: float         # Estimated from lid position
    orbital_hollowing_indicator: float  # Depth-based assessment


@dataclass
class AgingAnalysis:
    """Complete aging pattern analysis."""
    muscle_tonus: MuscleTonus
    gravitational_drift: GravitationalDrift
    periorbital: PeriorbitalAging
    estimated_biological_age_bracket: str  # e.g., "35-40", "45-50"
    overall_aging_severity: float          # 0-10


# Blendshape to aging indicator mapping
FRONTALIS_SHAPES = ["browInnerUp", "browOuterUpLeft", "browOuterUpRight"]
CORRUGATOR_SHAPES = ["browDownLeft", "browDownRight"]
ORBICULARIS_SHAPES = ["mouthPucker", "mouthFunnel", "mouthPressLeft", "mouthPressRight"]
MASSETER_SHAPES = ["jawOpen", "jawForward", "jawLeft", "jawRight"]
SQUINT_SHAPES = ["eyeSquintLeft", "eyeSquintRight"]


def _avg_blendshape(blendshapes: dict[str, float], names: list[str]) -> float:
    """Average blendshape value for a group."""
    values = [blendshapes.get(n, 0.0) for n in names]
    return sum(values) / max(len(values), 1)


def analyze_muscle_tonus(blendshapes: dict[str, float]) -> MuscleTonus:
    """Analyze muscle tonus from blendshape patterns.

    At rest (neutral expression), elevated blendshapes indicate
    chronic muscle activity patterns associated with aging.
    """
    frontalis = _avg_blendshape(blendshapes, FRONTALIS_SHAPES)
    corrugator = _avg_blendshape(blendshapes, CORRUGATOR_SHAPES)
    orbicularis = _avg_blendshape(blendshapes, ORBICULARIS_SHAPES)
    masseter = _avg_blendshape(blendshapes, MASSETER_SHAPES)

    # Overall: higher resting muscle activity = more aging indicators
    severity = (frontalis * 3.0 + corrugator * 3.0 + (1 - orbicularis) * 2.0 + masseter * 2.0)
    severity = min(10.0, severity)

    return MuscleTonus(
        frontalis_compensation=round(frontalis, 3),
        corrugator_activity=round(corrugator, 3),
        orbicularis_tone=round(orbicularis, 3),
        masseter_activity=round(masseter, 3),
        overall_muscle_age_indicator=round(severity, 1),
    )


def analyze_gravitational_drift(
    detection: DetectionResult,
    calibration: CalibrationResult,
) -> GravitationalDrift:
    """Analyze downward displacement of facial landmarks.

    Compares ratios of upper vs lower facial segments to detect
    gravitational ptosis of soft tissue.
    """
    # Brow descent: compare brow height to ideal ratio
    # Ideal: brow peak should be at ~1/3 height of glabella-to-eye distance
    brow_l = detection.px(PAIRED["brow_peak"][0])
    brow_r = detection.px(PAIRED["brow_peak"][1])
    glabella = detection.px(MIDLINE["glabella"])
    eye_l = detection.px(PAIRED["eye_outer"][0])
    eye_r = detection.px(PAIRED["eye_outer"][1])

    # Brow should sit above the eye — if close, it's descended
    brow_to_eye_l = abs(brow_l[1] - eye_l[1])
    brow_to_eye_r = abs(brow_r[1] - eye_r[1])
    avg_brow_gap = (brow_to_eye_l + brow_to_eye_r) / 2
    brow_descent_px = max(0, 40 - avg_brow_gap)  # 40px is approximate ideal gap
    brow_descent_mm = calibration.to_mm(brow_descent_px)

    # Malar descent: cheekbone relative to eye level
    cheek_l = detection.px(PAIRED["cheekbone"][0])
    cheek_r = detection.px(PAIRED["cheekbone"][1])
    avg_cheek_y = (cheek_l[1] + cheek_r[1]) / 2
    avg_eye_y = (eye_l[1] + eye_r[1]) / 2
    malar_drop = avg_cheek_y - avg_eye_y
    malar_descent_mm = calibration.to_mm(max(0, malar_drop - 50))

    # Jowl: mouth corner to jawline distance
    mouth_l = detection.px(PAIRED["mouth_corner"][0])
    mouth_r = detection.px(PAIRED["mouth_corner"][1])
    gonion_l = detection.px(PAIRED["gonion"][0])
    gonion_r = detection.px(PAIRED["gonion"][1])
    jowl_l = abs(mouth_l[1] - gonion_l[1])
    jowl_r = abs(mouth_r[1] - gonion_r[1])
    avg_jowl = (jowl_l + jowl_r) / 2
    jowl_descent_mm = calibration.to_mm(max(0, 80 - avg_jowl))

    # Overall drift score
    drift_score = min(10.0, (brow_descent_mm + malar_descent_mm + jowl_descent_mm) / 3)

    return GravitationalDrift(
        brow_descent_mm=round(brow_descent_mm, 1),
        malar_descent_mm=round(malar_descent_mm, 1),
        jowl_descent_mm=round(jowl_descent_mm, 1),
        overall_drift_score=round(drift_score, 1),
    )


def analyze_periorbital(
    detection: DetectionResult,
    blendshapes: dict[str, float],
    calibration: CalibrationResult,
) -> PeriorbitalAging:
    """Analyze periorbital aging indicators."""
    # Crow's feet potential from squint blendshapes
    crow_feet = _avg_blendshape(blendshapes, SQUINT_SHAPES)

    # Under-lid laxity: lower eyelid distance from eye center
    # MediaPipe provides eye contour landmarks
    eye_inner_l = detection.px(PAIRED["eye_inner"][0])
    eye_outer_l = detection.px(PAIRED["eye_outer"][0])
    infra_l = detection.px(PAIRED["infraorbital"][0])

    eye_center_y = (eye_inner_l[1] + eye_outer_l[1]) / 2
    lid_gap = abs(infra_l[1] - eye_center_y)
    lid_laxity = min(1.0, calibration.to_mm(lid_gap) / 15.0)

    # Orbital hollowing from z-depth
    eye_depth = abs(detection.px3d(PAIRED["infraorbital"][0])[2])
    cheek_depth = abs(detection.px3d(PAIRED["cheekbone"][0])[2])
    hollowing = calibration.to_mm(abs(eye_depth - cheek_depth)) / 5.0
    hollowing = min(1.0, hollowing)

    return PeriorbitalAging(
        crow_feet_potential=round(crow_feet, 3),
        under_lid_laxity=round(lid_laxity, 3),
        orbital_hollowing_indicator=round(hollowing, 3),
    )


def estimate_age_bracket(severity: float) -> str:
    """Map overall aging severity to estimated biological age bracket."""
    if severity < 1.5:
        return "25-30"
    elif severity < 3.0:
        return "30-35"
    elif severity < 4.5:
        return "35-40"
    elif severity < 6.0:
        return "40-45"
    elif severity < 7.5:
        return "45-55"
    else:
        return "55+"


def analyze(
    detection: DetectionResult,
    calibration: CalibrationResult,
    blendshapes: dict[str, float] | None = None,
) -> AgingAnalysis:
    """Run complete aging analysis.

    Args:
        detection: Face landmarks (typically frontal view)
        calibration: px→mm calibration
        blendshapes: Blendshapes from the SAME view (not fused!)
    """
    bs = blendshapes or {}

    muscle = analyze_muscle_tonus(bs)
    drift = analyze_gravitational_drift(detection, calibration)
    periorbital = analyze_periorbital(detection, bs, calibration)

    # Composite aging severity
    severity = (
        muscle.overall_muscle_age_indicator * 0.3
        + drift.overall_drift_score * 0.5
        + (periorbital.crow_feet_potential + periorbital.under_lid_laxity) * 5 * 0.2
    )
    severity = round(min(10.0, severity), 1)

    return AgingAnalysis(
        muscle_tonus=muscle,
        gravitational_drift=drift,
        periorbital=periorbital,
        estimated_biological_age_bracket=estimate_age_bracket(severity),
        overall_aging_severity=severity,
    )
