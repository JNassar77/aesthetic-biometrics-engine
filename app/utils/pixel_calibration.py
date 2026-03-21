"""
Pixel-to-millimeter calibration using iris diameter as biological reference.

The human iris has a nearly constant horizontal diameter of 11.7mm (± 0.5mm),
independent of sex, age, or ethnicity (Hashemi et al., 2012).

MediaPipe Face Landmarker provides iris contour landmarks (468-477) with
refine_landmarks=True, enabling precise measurement of iris width in pixels.

Calibration pipeline:
1. Measure left + right iris width in pixels
2. Average both for robustness
3. Compute px_per_mm = iris_width_px / IRIS_WIDTH_MM
4. If iris confidence is low → fallback to face-width estimation (V1 method)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Biological constant — horizontal iris diameter (corneal limbus-to-limbus)
IRIS_WIDTH_MM = 11.7

# Minimum acceptable iris width in pixels (below this → likely misdetection)
MIN_IRIS_PX = 15.0

# Maximum ratio between left/right iris widths (above this → one eye occluded)
MAX_IRIS_ASYMMETRY_RATIO = 1.5

# Default face width assumption for fallback (bizygomatic breadth, adult average)
DEFAULT_FACE_WIDTH_MM = 140.0

# Iris landmark indices (MediaPipe)
LEFT_IRIS_RIGHT = 469     # leftmost horizontal point
LEFT_IRIS_LEFT = 471      # rightmost horizontal point
RIGHT_IRIS_RIGHT = 474
RIGHT_IRIS_LEFT = 476


@dataclass
class CalibrationResult:
    """Result of pixel-to-mm calibration."""
    px_per_mm: float
    method: str               # "iris" or "face_width_estimate"
    confidence: float         # 0.0–1.0
    iris_width_px: float | None = None
    face_width_px: float | None = None
    warnings: list[str] | None = None

    def to_mm(self, px: float) -> float:
        """Convert a pixel measurement to millimeters."""
        return px / self.px_per_mm if self.px_per_mm > 0 else 0.0

    def to_px(self, mm: float) -> float:
        """Convert a millimeter measurement to pixels."""
        return mm * self.px_per_mm


def _iris_width_from_landmarks(
    landmarks: np.ndarray,
    image_width: int,
) -> tuple[float, float]:
    """Measure left and right iris horizontal diameters in pixels.

    Args:
        landmarks: (478, 3) normalized landmark array
        image_width: Image width for denormalization

    Returns:
        (left_iris_px, right_iris_px) — horizontal iris diameters
    """
    left_px = abs(
        landmarks[LEFT_IRIS_RIGHT][0] - landmarks[LEFT_IRIS_LEFT][0]
    ) * image_width
    right_px = abs(
        landmarks[RIGHT_IRIS_RIGHT][0] - landmarks[RIGHT_IRIS_LEFT][0]
    ) * image_width
    return left_px, right_px


def _face_width_from_landmarks(
    landmarks: np.ndarray,
    image_width: int,
) -> float:
    """Measure face width (bizygomatic) in pixels using cheekbone landmarks.

    Uses outer eye corners (33, 263) as proxy for bizygomatic width —
    these are more reliably detected than actual zygomatic points.
    """
    # Outer eye corners
    left_x = landmarks[263][0] * image_width
    right_x = landmarks[33][0] * image_width
    return abs(left_x - right_x)


def calibrate(
    landmarks: np.ndarray,
    image_width: int,
    image_height: int,
    min_iris_px: float = MIN_IRIS_PX,
) -> CalibrationResult:
    """Compute px→mm conversion factor from iris landmarks with face-width fallback.

    Args:
        landmarks: (478, 3) normalized landmarks from FaceLandmarkerV2
        image_width: Image width in pixels
        image_height: Image height in pixels
        min_iris_px: Minimum iris width in pixels to accept

    Returns:
        CalibrationResult with px_per_mm and metadata
    """
    warnings: list[str] = []

    # --- Attempt iris-based calibration ---
    if len(landmarks) >= 478:
        left_px, right_px = _iris_width_from_landmarks(landmarks, image_width)

        # Validate both irises
        both_valid = left_px >= min_iris_px and right_px >= min_iris_px

        # Check asymmetry (one eye might be partially occluded in oblique view)
        if both_valid:
            ratio = max(left_px, right_px) / max(min(left_px, right_px), 0.1)
            if ratio > MAX_IRIS_ASYMMETRY_RATIO:
                # Use only the larger (more visible) iris
                iris_px = max(left_px, right_px)
                warnings.append(
                    f"Iris asymmetry detected (ratio {ratio:.2f}). "
                    "Using the more visible iris only."
                )
                confidence = 0.75
            else:
                # Average both irises for robustness
                iris_px = (left_px + right_px) / 2.0
                confidence = min(0.95, 0.6 + iris_px / (image_width * 0.1))
        elif left_px >= min_iris_px or right_px >= min_iris_px:
            # Only one iris visible (common in oblique views)
            iris_px = max(left_px, right_px)
            warnings.append("Only one iris visible. Calibration from single iris.")
            confidence = 0.70
        else:
            iris_px = 0.0
            confidence = 0.0

        if iris_px >= min_iris_px:
            px_per_mm = iris_px / IRIS_WIDTH_MM
            return CalibrationResult(
                px_per_mm=px_per_mm,
                method="iris",
                confidence=round(confidence, 2),
                iris_width_px=round(iris_px, 2),
                warnings=warnings or None,
            )
        else:
            warnings.append(
                f"Iris too small ({max(left_px, right_px):.1f}px < {min_iris_px}px). "
                "Falling back to face-width estimation."
            )

    # --- Fallback: face-width estimation (V1 method) ---
    face_width_px = _face_width_from_landmarks(landmarks, image_width)

    if face_width_px < 50:
        # Extremely small face detection — return minimal estimate
        warnings.append("Face width very small. Calibration unreliable.")
        return CalibrationResult(
            px_per_mm=1.0,
            method="face_width_estimate",
            confidence=0.1,
            face_width_px=round(face_width_px, 2),
            warnings=warnings,
        )

    # Outer eye distance ≈ 90mm average → scale to full face width
    # Bizygomatic ≈ 140mm, interocular outer ≈ 90mm
    OUTER_EYE_TO_BIZYGOMATIC = DEFAULT_FACE_WIDTH_MM / 90.0
    estimated_bizygomatic_px = face_width_px * OUTER_EYE_TO_BIZYGOMATIC
    px_per_mm = estimated_bizygomatic_px / DEFAULT_FACE_WIDTH_MM

    warnings.append("IRIS_CALIBRATION_FALLBACK")

    return CalibrationResult(
        px_per_mm=round(px_per_mm, 4),
        method="face_width_estimate",
        confidence=0.45,
        face_width_px=round(face_width_px, 2),
        warnings=warnings,
    )
