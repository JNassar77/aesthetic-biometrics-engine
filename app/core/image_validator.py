import cv2
import numpy as np
from app.models.schemas import QualityWarning


def validate_image(image: np.ndarray) -> list[QualityWarning]:
    """Check image quality and return warnings."""
    warnings: list[QualityWarning] = []
    h, w = image.shape[:2]

    # Resolution check
    if w < 640 or h < 480:
        warnings.append(QualityWarning(
            code="LOW_RESOLUTION",
            message=f"Image resolution {w}x{h} is below recommended 640x480. Accuracy may be reduced.",
        ))

    # Brightness check
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = gray.mean()
    if mean_brightness < 50:
        warnings.append(QualityWarning(
            code="UNDEREXPOSED",
            message=f"Image is too dark (brightness: {mean_brightness:.0f}/255). Use better lighting.",
        ))
    elif mean_brightness > 220:
        warnings.append(QualityWarning(
            code="OVEREXPOSED",
            message=f"Image is overexposed (brightness: {mean_brightness:.0f}/255). Reduce lighting.",
        ))

    # Contrast check
    std_brightness = gray.std()
    if std_brightness < 30:
        warnings.append(QualityWarning(
            code="LOW_CONTRAST",
            message="Image has low contrast. Ensure even, diffused lighting.",
        ))

    # Blur detection (Laplacian variance)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < 50:
        warnings.append(QualityWarning(
            code="BLURRY",
            message=f"Image appears blurry (sharpness: {laplacian_var:.0f}). Use a stable camera position.",
        ))

    return warnings
