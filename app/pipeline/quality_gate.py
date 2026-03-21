"""
Quality gate for image and detection validation.

Checks:
1. Image quality (resolution, brightness, contrast, sharpness)
2. Face detection confidence
3. Head pose tolerance (is the angle correct for the requested view?)
4. Neutral expression validation (warns if patient is not relaxed)

All checks produce QualityWarning objects. Warnings are non-blocking —
analysis proceeds but warnings are included in the response.
"""

import cv2
import numpy as np
from dataclasses import dataclass

from app.detection.head_pose import HeadPose


@dataclass
class QualityWarning:
    code: str
    message: str
    severity: str = "medium"  # "low", "medium", "high"


# --- Expression thresholds for neutral-face validation ---
EXPRESSION_THRESHOLDS: dict[str, float] = {
    "mouthSmileLeft": 0.15,
    "mouthSmileRight": 0.15,
    "browDownLeft": 0.20,
    "browDownRight": 0.20,
    "jawOpen": 0.10,
    "mouthPucker": 0.15,
    "mouthFunnel": 0.15,
    "eyeSquintLeft": 0.25,
    "eyeSquintRight": 0.25,
}

# --- Head pose tolerances per expected view ---
# "soft" limits produce warnings; "hard" limits reject the image entirely
VIEW_POSE_TOLERANCES: dict[str, dict[str, float]] = {
    "frontal": {"max_yaw": 12.0, "max_pitch": 10.0, "max_roll": 8.0},
    "oblique": {"max_yaw": 60.0, "max_pitch": 10.0, "max_roll": 8.0},
    "profile": {"max_yaw": 100.0, "max_pitch": 10.0, "max_roll": 8.0},
}

# Hard rejection thresholds — beyond these, landmarks are too unreliable
# for any clinical measurement (Sprint 2 addition)
HARD_REJECTION_THRESHOLDS: dict[str, dict[str, float]] = {
    "frontal": {"max_yaw": 25.0, "max_pitch": 20.0, "max_roll": 15.0},
    "oblique": {"max_yaw": 75.0, "max_pitch": 20.0, "max_roll": 15.0},
    "profile": {"max_yaw": 110.0, "max_pitch": 20.0, "max_roll": 15.0},
}


def check_image_quality(image: np.ndarray) -> list[QualityWarning]:
    """Check image quality: resolution, brightness, contrast, sharpness."""
    warnings: list[QualityWarning] = []
    h, w = image.shape[:2]

    if w < 640 or h < 480:
        warnings.append(QualityWarning(
            code="LOW_RESOLUTION",
            message=f"Image resolution {w}x{h} is below recommended 640x480.",
            severity="medium",
        ))

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = float(gray.mean())

    if mean_brightness < 50:
        warnings.append(QualityWarning(
            code="UNDEREXPOSED",
            message=f"Image is too dark (brightness: {mean_brightness:.0f}/255).",
            severity="high",
        ))
    elif mean_brightness > 220:
        warnings.append(QualityWarning(
            code="OVEREXPOSED",
            message=f"Image is overexposed (brightness: {mean_brightness:.0f}/255).",
            severity="high",
        ))

    std_brightness = float(gray.std())
    if std_brightness < 30:
        warnings.append(QualityWarning(
            code="LOW_CONTRAST",
            message="Image has low contrast. Use even, diffused lighting.",
            severity="medium",
        ))

    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if laplacian_var < 50:
        warnings.append(QualityWarning(
            code="BLURRY",
            message=f"Image appears blurry (sharpness: {laplacian_var:.0f}).",
            severity="high",
        ))

    return warnings


def check_head_pose(
    pose: HeadPose | None,
    expected_view: str,
) -> list[QualityWarning]:
    """Check if head pose matches the expected view angle."""
    warnings: list[QualityWarning] = []

    if pose is None:
        warnings.append(QualityWarning(
            code="NO_HEAD_POSE",
            message="Could not determine head orientation.",
            severity="medium",
        ))
        return warnings

    tolerances = VIEW_POSE_TOLERANCES.get(expected_view, VIEW_POSE_TOLERANCES["frontal"])

    if expected_view == "frontal" and abs(pose.yaw) > tolerances["max_yaw"]:
        warnings.append(QualityWarning(
            code="HEAD_NOT_FRONTAL",
            message=f"Head is rotated {pose.yaw:.1f}° (max {tolerances['max_yaw']}° for frontal view).",
            severity="high",
        ))

    if expected_view == "oblique":
        abs_yaw = abs(pose.yaw)
        if abs_yaw < 25 or abs_yaw > 60:
            warnings.append(QualityWarning(
                code="HEAD_NOT_OBLIQUE",
                message=f"Head yaw {pose.yaw:.1f}° is outside oblique range (25°-60°).",
                severity="high",
            ))

    if expected_view == "profile":
        abs_yaw = abs(pose.yaw)
        if abs_yaw < 70:
            warnings.append(QualityWarning(
                code="HEAD_NOT_PROFILE",
                message=f"Head yaw {pose.yaw:.1f}° is not enough for profile view (need >70°).",
                severity="high",
            ))

    if abs(pose.roll) > tolerances["max_roll"]:
        warnings.append(QualityWarning(
            code="HEAD_TILTED",
            message=f"Head is tilted {pose.roll:.1f}° (max {tolerances['max_roll']}°).",
            severity="medium",
        ))

    if abs(pose.pitch) > tolerances["max_pitch"]:
        warnings.append(QualityWarning(
            code="HEAD_PITCH",
            message=f"Head is tilted {'up' if pose.pitch > 0 else 'down'} {abs(pose.pitch):.1f}°.",
            severity="medium",
        ))

    return warnings


def check_hard_pose_rejection(
    pose: HeadPose | None,
    expected_view: str,
) -> QualityWarning | None:
    """Check if head pose exceeds hard rejection thresholds.

    Returns a single high-severity warning if image should be rejected,
    or None if pose is acceptable (may still produce soft warnings).
    """
    if pose is None:
        return None

    limits = HARD_REJECTION_THRESHOLDS.get(expected_view, HARD_REJECTION_THRESHOLDS["frontal"])

    if expected_view == "frontal" and abs(pose.yaw) > limits["max_yaw"]:
        return QualityWarning(
            code="POSE_REJECTED",
            message=(
                f"Head rotation {pose.yaw:.1f}° exceeds maximum "
                f"{limits['max_yaw']}° for frontal view. Image rejected."
            ),
            severity="critical",
        )

    if expected_view == "oblique":
        abs_yaw = abs(pose.yaw)
        if abs_yaw < 15 or abs_yaw > limits["max_yaw"]:
            return QualityWarning(
                code="POSE_REJECTED",
                message=(
                    f"Head yaw {pose.yaw:.1f}° is outside acceptable oblique range "
                    f"(15°–{limits['max_yaw']}°). Image rejected."
                ),
                severity="critical",
            )

    if expected_view == "profile" and abs(pose.yaw) < 55:
        return QualityWarning(
            code="POSE_REJECTED",
            message=(
                f"Head yaw {pose.yaw:.1f}° is insufficient for profile view "
                "(need at least 55°). Image rejected."
            ),
            severity="critical",
        )

    if abs(pose.pitch) > limits["max_pitch"]:
        return QualityWarning(
            code="POSE_REJECTED",
            message=(
                f"Head pitch {abs(pose.pitch):.1f}° exceeds maximum "
                f"{limits['max_pitch']}°. Image rejected."
            ),
            severity="critical",
        )

    if abs(pose.roll) > limits["max_roll"]:
        return QualityWarning(
            code="POSE_REJECTED",
            message=(
                f"Head roll {abs(pose.roll):.1f}° exceeds maximum "
                f"{limits['max_roll']}°. Image rejected."
            ),
            severity="critical",
        )

    return None


def check_neutral_expression(blendshapes: dict[str, float]) -> list[QualityWarning]:
    """Warn if patient is not in neutral/relaxed expression."""
    warnings: list[QualityWarning] = []

    active_expressions = []
    for shape_name, threshold in EXPRESSION_THRESHOLDS.items():
        value = blendshapes.get(shape_name, 0.0)
        if value > threshold:
            active_expressions.append(f"{shape_name}: {value:.2f}")

    if active_expressions:
        warnings.append(QualityWarning(
            code="NON_NEUTRAL_EXPRESSION",
            message=(
                "Active facial expression detected. "
                "Results are most accurate with a neutral, relaxed face. "
                f"Detected: {', '.join(active_expressions[:3])}"
            ),
            severity="medium",
        ))

    return warnings


def compute_expression_deviation(blendshapes: dict[str, float]) -> float:
    """Compute how far from neutral the expression is (0.0 = neutral, 1.0 = extreme).

    Used by the zone analyzer to weight blendshape-based findings.
    Higher deviation means blendshape-based measurements (muscle tonus,
    dynamic asymmetry) are less reliable for clinical interpretation.
    """
    if not blendshapes:
        return 0.0

    deviations = []
    for shape_name, threshold in EXPRESSION_THRESHOLDS.items():
        value = blendshapes.get(shape_name, 0.0)
        if value > threshold:
            # How much over the threshold, normalized
            excess = (value - threshold) / max(1.0 - threshold, 0.01)
            deviations.append(min(1.0, excess))

    if not deviations:
        return 0.0

    return min(1.0, sum(deviations) / len(deviations))


def run_quality_gate(
    image: np.ndarray,
    detection_result,
    expected_view: str,
    head_pose: HeadPose | None,
) -> list[QualityWarning]:
    """Run all quality checks and return combined warnings.

    Args:
        image: Preprocessed BGR image
        detection_result: DetectionResult from face landmarker
        expected_view: "frontal", "oblique", or "profile"
        head_pose: Extracted head pose (or None)

    Returns:
        List of all quality warnings (may be empty if all checks pass).
    """
    warnings = check_image_quality(image)

    if not detection_result.face_detected:
        warnings.append(QualityWarning(
            code="NO_FACE_DETECTED",
            message="No face detected. Ensure the face is clearly visible and well-lit.",
            severity="high",
        ))
        return warnings

    # Hard rejection — if pose is too extreme, flag as critical
    rejection = check_hard_pose_rejection(head_pose, expected_view)
    if rejection is not None:
        warnings.append(rejection)
        return warnings  # Skip further checks — image is rejected

    # Soft warnings for suboptimal but usable pose
    warnings.extend(check_head_pose(head_pose, expected_view))
    warnings.extend(check_neutral_expression(detection_result.blendshapes))

    return warnings
