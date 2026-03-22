"""
Synthetic landmark data for testing.

Provides factory functions that produce consistent, deterministic
landmark arrays and blendshape dicts for unit tests. All landmarks
are 478-point arrays in MediaPipe normalized [0-1] coordinate space.
"""

import numpy as np

from app.detection.face_landmarker import DetectionResult
from app.detection.landmark_index import (
    MIDLINE, PAIRED, IRIS,
    LIP_UPPER_OUTER, LIP_LOWER_OUTER,
    FACE_OVAL,
)
from app.utils.pixel_calibration import CalibrationResult


# ──────────────────── Blendshape Constants ────────────────────────

ALL_BLENDSHAPES = [
    "_neutral", "browDownLeft", "browDownRight", "browInnerUp",
    "browOuterUpLeft", "browOuterUpRight", "cheekPuff", "cheekSquintLeft",
    "cheekSquintRight", "eyeBlinkLeft", "eyeBlinkRight", "eyeLookDownLeft",
    "eyeLookDownRight", "eyeLookInLeft", "eyeLookInRight", "eyeLookOutLeft",
    "eyeLookOutRight", "eyeLookUpLeft", "eyeLookUpRight", "eyeSquintLeft",
    "eyeSquintRight", "eyeWideLeft", "eyeWideRight", "jawForward",
    "jawLeft", "jawOpen", "jawRight", "mouthClose", "mouthDimpleLeft",
    "mouthDimpleRight", "mouthFrownLeft", "mouthFrownRight", "mouthFunnel",
    "mouthLeft", "mouthLowerDownLeft", "mouthLowerDownRight", "mouthPressLeft",
    "mouthPressRight", "mouthPucker", "mouthRight", "mouthRollLower",
    "mouthRollUpper", "mouthShrugLower", "mouthShrugUpper", "mouthSmileLeft",
    "mouthSmileRight", "mouthStretchLeft", "mouthStretchRight", "mouthUpperUpLeft",
    "mouthUpperUpRight", "noseSneerLeft", "noseSneerRight",
]


# ──────────────────── Landmark Helpers ────────────────────────

def _base_landmarks() -> np.ndarray:
    """Create a base 478-landmark array with anatomically plausible positions."""
    lm = np.full((478, 3), 0.5, dtype=np.float32)

    # ── Midline landmarks (x=0.5) ──
    lm[MIDLINE["trichion_approx"]] = [0.50, 0.10, 0.0]
    lm[MIDLINE["glabella"]] = [0.50, 0.25, 0.0]
    lm[MIDLINE["nasion"]] = [0.50, 0.30, 0.0]
    lm[MIDLINE["rhinion"]] = [0.50, 0.36, 0.0]
    lm[MIDLINE["pronasale"]] = [0.50, 0.40, -0.05]
    lm[MIDLINE["subnasale"]] = [0.50, 0.44, 0.0]
    lm[MIDLINE["labrale_superius"]] = [0.50, 0.50, 0.0]
    lm[MIDLINE["stomion"]] = [0.50, 0.53, 0.0]
    lm[MIDLINE["labrale_inferius"]] = [0.50, 0.56, 0.0]
    lm[MIDLINE["mentolabial_sulcus"]] = [0.50, 0.60, 0.0]
    lm[MIDLINE["pogonion"]] = [0.50, 0.70, 0.0]
    lm[MIDLINE["gnathion"]] = [0.50, 0.80, 0.0]

    # ── Paired landmarks — symmetric around x=0.5 ──
    _set_paired(lm, "brow_outer", 0.20, 0.20, 0.0)
    _set_paired(lm, "brow_inner", 0.08, 0.22, 0.0)
    _set_paired(lm, "brow_peak", 0.15, 0.20, 0.0)
    _set_paired(lm, "eye_inner", 0.06, 0.30, 0.0)
    _set_paired(lm, "eye_outer", 0.14, 0.30, 0.0)
    _set_paired(lm, "cheekbone", 0.18, 0.35, 0.0)
    _set_paired(lm, "malar_high", 0.17, 0.34, 0.0)
    _set_paired(lm, "malar_low", 0.16, 0.42, 0.0)
    _set_paired(lm, "alar", 0.05, 0.43, 0.0)
    _set_paired(lm, "mouth_corner", 0.10, 0.53, 0.0)
    _set_paired(lm, "gonion", 0.22, 0.65, 0.0)
    _set_paired(lm, "infraorbital", 0.08, 0.33, 0.0)
    _set_paired(lm, "preauricular", 0.25, 0.40, 0.0)
    _set_paired(lm, "temporal", 0.22, 0.18, 0.0)

    # ── Iris landmarks (symmetric) ──
    lm[IRIS["left_iris_center"]] = [0.60, 0.30, 0.0]
    lm[IRIS["left_iris_right"]] = [0.61, 0.30, 0.0]
    lm[IRIS["left_iris_top"]] = [0.60, 0.29, 0.0]
    lm[IRIS["left_iris_left"]] = [0.59, 0.30, 0.0]
    lm[IRIS["left_iris_bottom"]] = [0.60, 0.31, 0.0]

    lm[IRIS["right_iris_center"]] = [0.40, 0.30, 0.0]
    lm[IRIS["right_iris_right"]] = [0.41, 0.30, 0.0]
    lm[IRIS["right_iris_top"]] = [0.40, 0.29, 0.0]
    lm[IRIS["right_iris_left"]] = [0.39, 0.30, 0.0]
    lm[IRIS["right_iris_bottom"]] = [0.40, 0.31, 0.0]

    # ── Lip contour points ──
    for i, idx in enumerate(LIP_UPPER_OUTER):
        t = i / max(len(LIP_UPPER_OUTER) - 1, 1)
        x = 0.40 + 0.20 * t
        lm[idx] = [x, 0.50, 0.0]
    for i, idx in enumerate(LIP_LOWER_OUTER):
        t = i / max(len(LIP_LOWER_OUTER) - 1, 1)
        x = 0.60 - 0.20 * t
        lm[idx] = [x, 0.56, 0.0]

    # ── Face oval ──
    for i, idx in enumerate(FACE_OVAL):
        t = i / max(len(FACE_OVAL) - 1, 1)
        angle = 2 * np.pi * t
        lm[idx] = [0.5 + 0.28 * np.cos(angle), 0.45 + 0.35 * np.sin(angle), 0.0]

    return lm


def _set_paired(lm: np.ndarray, name: str, offset_x: float, y: float, z: float):
    """Set a paired landmark symmetrically around x=0.5."""
    left_idx, right_idx = PAIRED[name]
    lm[left_idx] = [0.5 + offset_x, y, z]
    lm[right_idx] = [0.5 - offset_x, y, z]


# ──────────────────── Factory Functions ────────────────────────

def make_symmetric_face(
    image_size: int = 1000,
) -> DetectionResult:
    """Create a perfectly symmetric face detection result.

    All paired landmarks are exactly mirrored around x=0.5.
    Iris landmarks are positioned to produce valid calibration.
    """
    return DetectionResult(
        landmarks=_base_landmarks(),
        blendshapes=make_blendshapes(neutral=True),
        transformation_matrix=np.eye(4, dtype=np.float32),
        image_width=image_size,
        image_height=image_size,
        face_detected=True,
    )


def make_asymmetric_face(
    image_size: int = 1000,
    asymmetry_mm: float = 3.0,
) -> DetectionResult:
    """Create a face with deliberate asymmetry.

    Shifts left brow (Bw1) and left cheekbone (Ck2) laterally
    to simulate clinical asymmetry.

    Args:
        asymmetry_mm: Approximate mm of shift (converted to normalized coords).
    """
    lm = _base_landmarks()

    # Convert mm to normalized shift (~1mm ≈ 0.001 in normalized coords at 1000px)
    shift = asymmetry_mm * 0.003

    # Shift left brow peak outward
    lm[PAIRED["brow_peak"][0]][0] += shift
    # Shift left cheekbone outward and down
    lm[PAIRED["cheekbone"][0]][0] += shift
    lm[PAIRED["cheekbone"][0]][1] += shift * 0.5
    # Shift left mouth corner
    lm[PAIRED["mouth_corner"][0]][0] += shift * 0.7

    return DetectionResult(
        landmarks=lm,
        blendshapes=make_blendshapes(neutral=True),
        transformation_matrix=np.eye(4, dtype=np.float32),
        image_width=image_size,
        image_height=image_size,
        face_detected=True,
    )


def make_aged_face(
    image_size: int = 1000,
) -> DetectionResult:
    """Create a face with aging characteristics.

    - Landmarks shifted downward (gravitational drift)
    - Deeper nasolabial folds (malar_low displaced)
    - Elevated blendshapes for aging muscle patterns
    """
    lm = _base_landmarks()

    # Gravitational drift: shift lower face landmarks down
    drift = 0.015
    for name in ["mouth_corner", "malar_low", "gonion"]:
        l_idx, r_idx = PAIRED[name]
        lm[l_idx][1] += drift
        lm[r_idx][1] += drift

    # Chin sags
    lm[MIDLINE["pogonion"]][1] += drift * 1.5
    lm[MIDLINE["gnathion"]][1] += drift * 2.0

    # Tear trough deepens (z moves backward)
    l_inf, r_inf = PAIRED["infraorbital"]
    lm[l_inf][2] += 0.02
    lm[r_inf][2] += 0.02

    # Temporal hollowing (z moves backward)
    l_temp, r_temp = PAIRED["temporal"]
    lm[l_temp][2] += 0.015
    lm[r_temp][2] += 0.015

    return DetectionResult(
        landmarks=lm,
        blendshapes=make_blendshapes(neutral=False, aging=True),
        transformation_matrix=np.eye(4, dtype=np.float32),
        image_width=image_size,
        image_height=image_size,
        face_detected=True,
    )


def make_blendshapes(
    neutral: bool = True,
    aging: bool = False,
) -> dict[str, float]:
    """Create blendshape coefficient dict.

    Args:
        neutral: If True, all expression values near zero (resting face).
        aging: If True, simulate aging muscle patterns (crow's feet, brow ptosis).
    """
    if neutral:
        # All near zero — relaxed face
        bs = {name: 0.01 for name in ALL_BLENDSHAPES}
        bs["_neutral"] = 0.95
        return bs

    if aging:
        # Aging pattern: reduced muscle tonus, slight asymmetry
        bs = {name: 0.03 for name in ALL_BLENDSHAPES}
        bs["_neutral"] = 0.70
        bs["browDownLeft"] = 0.12
        bs["browDownRight"] = 0.08  # slight asymmetry
        bs["eyeSquintLeft"] = 0.18
        bs["eyeSquintRight"] = 0.15
        bs["mouthFrownLeft"] = 0.10
        bs["mouthFrownRight"] = 0.12
        bs["cheekSquintLeft"] = 0.08
        bs["cheekSquintRight"] = 0.06
        return bs

    # Active expression (smiling)
    bs = {name: 0.02 for name in ALL_BLENDSHAPES}
    bs["_neutral"] = 0.30
    bs["mouthSmileLeft"] = 0.65
    bs["mouthSmileRight"] = 0.70
    bs["cheekSquintLeft"] = 0.40
    bs["cheekSquintRight"] = 0.45
    bs["eyeSquintLeft"] = 0.30
    bs["eyeSquintRight"] = 0.35
    bs["jawOpen"] = 0.15
    return bs


def make_calibration(
    px_per_mm: float = 3.5,
    confidence: float = 0.90,
    method: str = "iris",
) -> CalibrationResult:
    """Create a standard calibration result for testing."""
    return CalibrationResult(
        px_per_mm=px_per_mm,
        confidence=confidence,
        method=method,
        iris_width_px=3.5 * 11.7,     # 11.7mm * px_per_mm
        face_width_px=3.5 * 140.0,    # ~140mm face width
        warnings=[],
    )


def make_detection_with_calibration(
    symmetric: bool = True,
    image_size: int = 1000,
) -> tuple[DetectionResult, CalibrationResult]:
    """Convenience: returns both detection and matching calibration."""
    detection = make_symmetric_face(image_size) if symmetric else make_asymmetric_face(image_size)
    calibration = make_calibration()
    return detection, calibration
