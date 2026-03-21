"""Tests for iris-based pixel-to-mm calibration."""

import numpy as np
import pytest

from app.utils.pixel_calibration import (
    CalibrationResult,
    IRIS_WIDTH_MM,
    MIN_IRIS_PX,
    calibrate,
    _iris_width_from_landmarks,
    _face_width_from_landmarks,
)


def _make_landmarks(
    iris_left_width_norm: float = 0.03,
    iris_right_width_norm: float = 0.03,
    eye_left_x: float = 0.65,
    eye_right_x: float = 0.35,
) -> np.ndarray:
    """Create minimal 478-landmark array with controllable iris and eye positions.

    Iris landmarks:
        469 (left iris right) / 471 (left iris left) → horizontal extent
        474 (right iris right) / 476 (right iris left) → horizontal extent
    Eye outer corners:
        263 (left) / 33 (right)
    """
    landmarks = np.zeros((478, 3), dtype=np.float32)

    # Left iris horizontal (landmarks 469, 471)
    center_left = eye_left_x
    landmarks[469] = [center_left + iris_left_width_norm / 2, 0.4, 0.0]
    landmarks[471] = [center_left - iris_left_width_norm / 2, 0.4, 0.0]
    landmarks[468] = [center_left, 0.4, 0.0]  # center
    landmarks[470] = [center_left, 0.38, 0.0]  # top
    landmarks[472] = [center_left, 0.42, 0.0]  # bottom

    # Right iris horizontal (landmarks 474, 476)
    center_right = eye_right_x
    landmarks[474] = [center_right + iris_right_width_norm / 2, 0.4, 0.0]
    landmarks[476] = [center_right - iris_right_width_norm / 2, 0.4, 0.0]
    landmarks[473] = [center_right, 0.4, 0.0]
    landmarks[475] = [center_right, 0.38, 0.0]
    landmarks[477] = [center_right, 0.42, 0.0]

    # Eye outer corners for face-width fallback
    landmarks[263] = [eye_left_x, 0.4, 0.0]
    landmarks[33] = [eye_right_x, 0.4, 0.0]

    return landmarks


class TestIrisCalibration:
    """Tests for iris-based px→mm calibration."""

    def test_basic_calibration(self):
        """Both irises visible → iris method, good confidence."""
        landmarks = _make_landmarks(iris_left_width_norm=0.03, iris_right_width_norm=0.03)
        result = calibrate(landmarks, image_width=1000, image_height=1000)

        assert result.method == "iris"
        assert result.iris_width_px is not None
        assert result.iris_width_px == pytest.approx(30.0, abs=0.5)
        assert result.px_per_mm == pytest.approx(30.0 / IRIS_WIDTH_MM, abs=0.1)
        assert result.confidence >= 0.6

    def test_to_mm_conversion(self):
        """Conversion from pixels to mm is correct."""
        landmarks = _make_landmarks(iris_left_width_norm=0.03, iris_right_width_norm=0.03)
        result = calibrate(landmarks, image_width=1000, image_height=1000)

        # 30px iris → px_per_mm ≈ 2.564
        expected_px_per_mm = 30.0 / IRIS_WIDTH_MM
        assert result.to_mm(expected_px_per_mm) == pytest.approx(1.0, abs=0.01)

    def test_to_px_conversion(self):
        """Conversion from mm to pixels is correct."""
        landmarks = _make_landmarks(iris_left_width_norm=0.03, iris_right_width_norm=0.03)
        result = calibrate(landmarks, image_width=1000, image_height=1000)

        one_mm_in_px = result.to_px(1.0)
        assert one_mm_in_px == pytest.approx(result.px_per_mm, abs=0.01)

    def test_symmetric_irises_averaged(self):
        """Symmetric irises are averaged for robustness."""
        landmarks = _make_landmarks(iris_left_width_norm=0.028, iris_right_width_norm=0.032)
        result = calibrate(landmarks, image_width=1000, image_height=1000)

        assert result.method == "iris"
        assert result.iris_width_px == pytest.approx(30.0, abs=0.5)  # average of 28 and 32

    def test_asymmetric_irises_uses_larger(self):
        """When irises differ too much, use the larger (more visible) one."""
        # Both above MIN_IRIS_PX but ratio > 1.5 → asymmetry path
        landmarks = _make_landmarks(iris_left_width_norm=0.05, iris_right_width_norm=0.02)
        result = calibrate(landmarks, image_width=1000, image_height=1000)

        assert result.method == "iris"
        # Should use the larger iris (50px)
        assert result.iris_width_px == pytest.approx(50.0, abs=1.0)
        assert result.warnings is not None
        assert any("asymmetry" in w.lower() for w in result.warnings)

    def test_single_iris_visible(self):
        """Only one iris visible → still uses iris method with lower confidence."""
        landmarks = _make_landmarks(iris_left_width_norm=0.03, iris_right_width_norm=0.001)
        result = calibrate(landmarks, image_width=1000, image_height=1000)

        assert result.method == "iris"
        assert result.confidence < 0.8
        assert result.warnings is not None
        assert any("one iris" in w.lower() for w in result.warnings)


class TestFaceWidthFallback:
    """Tests for fallback to face-width estimation."""

    def test_fallback_when_iris_too_small(self):
        """Tiny iris detection → fallback to face-width."""
        landmarks = _make_landmarks(iris_left_width_norm=0.001, iris_right_width_norm=0.001)
        result = calibrate(landmarks, image_width=1000, image_height=1000)

        assert result.method == "face_width_estimate"
        assert result.face_width_px is not None
        assert result.confidence < 0.5
        assert result.warnings is not None
        assert any("IRIS_CALIBRATION_FALLBACK" in w for w in result.warnings)

    def test_fallback_with_landmarks_below_478(self):
        """Fewer than 478 landmarks (no iris) → fallback."""
        landmarks = np.zeros((467, 3), dtype=np.float32)
        # Set eye corners for face-width
        landmarks[263] = [0.65, 0.4, 0.0]
        landmarks[33] = [0.35, 0.4, 0.0]

        result = calibrate(landmarks, image_width=1000, image_height=1000)
        assert result.method == "face_width_estimate"

    def test_face_width_uses_eye_corners(self):
        """Face-width is measured from outer eye corners."""
        landmarks = _make_landmarks(
            iris_left_width_norm=0.001,
            iris_right_width_norm=0.001,
            eye_left_x=0.7,
            eye_right_x=0.3,
        )
        result = calibrate(landmarks, image_width=1000, image_height=1000)

        assert result.method == "face_width_estimate"
        assert result.face_width_px == pytest.approx(400.0, abs=1.0)


class TestCalibrationResult:
    """Tests for CalibrationResult dataclass."""

    def test_to_mm_zero_px(self):
        r = CalibrationResult(px_per_mm=2.5, method="iris", confidence=0.9)
        assert r.to_mm(0.0) == 0.0

    def test_to_mm_with_measurement(self):
        r = CalibrationResult(px_per_mm=2.5, method="iris", confidence=0.9)
        assert r.to_mm(25.0) == pytest.approx(10.0)

    def test_to_px_roundtrip(self):
        r = CalibrationResult(px_per_mm=3.0, method="iris", confidence=0.9)
        mm = r.to_mm(30.0)
        px = r.to_px(mm)
        assert px == pytest.approx(30.0)

    def test_zero_px_per_mm_safe(self):
        r = CalibrationResult(px_per_mm=0.0, method="iris", confidence=0.0)
        assert r.to_mm(100.0) == 0.0
