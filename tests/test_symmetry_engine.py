"""Tests for symmetry analysis engine."""

import numpy as np
import pytest

from app.analysis.symmetry_engine import (
    analyze_static_symmetry,
    analyze_dynamic_asymmetry,
    compute_symmetry_index,
    analyze,
    SymmetryMeasurement,
    SIGNIFICANCE_THRESHOLD_MM,
)
from app.detection.face_landmarker import DetectionResult
from app.utils.pixel_calibration import CalibrationResult


def _make_symmetric_detection(image_size: int = 1000) -> DetectionResult:
    """Create a perfectly symmetric face for testing.

    Landmarks are placed symmetrically around x=0.5 midline.
    """
    lm = np.full((478, 3), 0.5, dtype=np.float32)

    # Midline landmarks (x = 0.5)
    lm[9] = [0.50, 0.25, 0.0]    # glabella
    lm[4] = [0.50, 0.40, 0.0]    # pronasale
    lm[2] = [0.50, 0.45, 0.0]    # subnasale
    lm[13] = [0.50, 0.55, 0.0]   # stomion
    lm[152] = [0.50, 0.80, 0.0]  # gnathion

    # Paired landmarks — symmetric
    offset = 0.15
    # brow_peak: 282 (L), 52 (R)
    lm[282] = [0.5 + offset, 0.22, 0.0]
    lm[52] = [0.5 - offset, 0.22, 0.0]

    # eye_inner: 362 (L), 133 (R)
    lm[362] = [0.5 + 0.06, 0.30, 0.0]
    lm[133] = [0.5 - 0.06, 0.30, 0.0]

    # eye_outer: 263 (L), 33 (R)
    lm[263] = [0.5 + 0.14, 0.30, 0.0]
    lm[33] = [0.5 - 0.14, 0.30, 0.0]

    # cheekbone: 330 (L), 101 (R)
    lm[330] = [0.5 + 0.18, 0.35, 0.0]
    lm[101] = [0.5 - 0.18, 0.35, 0.0]

    # alar: 309 (L), 79 (R)
    lm[309] = [0.5 + 0.05, 0.42, 0.0]
    lm[79] = [0.5 - 0.05, 0.42, 0.0]

    # mouth_corner: 291 (L), 61 (R)
    lm[291] = [0.5 + 0.10, 0.55, 0.0]
    lm[61] = [0.5 - 0.10, 0.55, 0.0]

    # gonion: 365 (L), 136 (R)
    lm[365] = [0.5 + 0.20, 0.65, 0.0]
    lm[136] = [0.5 - 0.20, 0.65, 0.0]

    # preauricular: 356 (L), 127 (R)
    lm[356] = [0.5 + 0.25, 0.35, 0.0]
    lm[127] = [0.5 - 0.25, 0.35, 0.0]

    return DetectionResult(
        landmarks=lm,
        blendshapes={},
        transformation_matrix=None,
        image_width=image_size,
        image_height=image_size,
    )


def _make_asymmetric_detection(asymmetry_px: float = 20.0) -> DetectionResult:
    """Create face with deliberate left-right asymmetry."""
    det = _make_symmetric_detection()
    lm = det.landmarks.copy()

    # Shift left brow down (higher y = lower on screen)
    shift = asymmetry_px / det.image_width
    lm[282][1] += shift  # left brow peak lower

    # Shift left mouth corner down
    lm[291][1] += shift * 0.5

    return DetectionResult(
        landmarks=lm,
        blendshapes={},
        transformation_matrix=None,
        image_width=det.image_width,
        image_height=det.image_height,
    )


def _make_calibration(px_per_mm: float = 3.0) -> CalibrationResult:
    return CalibrationResult(
        px_per_mm=px_per_mm,
        method="iris",
        confidence=0.9,
    )


class TestStaticSymmetry:
    def test_symmetric_face_has_zero_differences(self):
        det = _make_symmetric_detection()
        cal = _make_calibration()
        measurements = analyze_static_symmetry(det, cal)

        assert len(measurements) == 6
        for m in measurements:
            assert m.difference_mm < 0.5, f"{m.axis_name}: diff={m.difference_mm}mm"
            assert not m.is_clinically_significant

    def test_asymmetric_face_detected(self):
        det = _make_asymmetric_detection(asymmetry_px=30.0)
        cal = _make_calibration()
        measurements = analyze_static_symmetry(det, cal)

        brow = next(m for m in measurements if m.axis_name == "brow_height")
        assert brow.difference_mm > 1.0

    def test_all_six_axes_measured(self):
        det = _make_symmetric_detection()
        cal = _make_calibration()
        measurements = analyze_static_symmetry(det, cal)

        names = {m.axis_name for m in measurements}
        expected = {"brow_height", "eye_width", "cheekbone_height",
                    "nasolabial_region", "mouth_corner_height", "gonion_height"}
        assert names == expected


class TestDynamicAsymmetry:
    def test_symmetric_blendshapes_no_asymmetry(self):
        bs = {
            "browDownLeft": 0.1,
            "browDownRight": 0.1,
            "mouthSmileLeft": 0.05,
            "mouthSmileRight": 0.05,
        }
        result = analyze_dynamic_asymmetry(bs)
        assert len(result) == 0

    def test_asymmetric_smile_detected(self):
        bs = {
            "mouthSmileLeft": 0.30,
            "mouthSmileRight": 0.05,
        }
        result = analyze_dynamic_asymmetry(bs, threshold=0.10)
        assert len(result) == 1
        assert result[0].blendshape_name == "mouthSmile"
        assert result[0].difference > 0.20

    def test_empty_blendshapes(self):
        result = analyze_dynamic_asymmetry({})
        assert len(result) == 0

    def test_multiple_asymmetries(self):
        bs = {
            "browDownLeft": 0.30,
            "browDownRight": 0.05,
            "eyeSquintLeft": 0.40,
            "eyeSquintRight": 0.10,
        }
        result = analyze_dynamic_asymmetry(bs, threshold=0.10)
        assert len(result) == 2


class TestSymmetryIndex:
    def test_perfect_symmetry_is_100(self):
        measurements = [
            SymmetryMeasurement("brow_height", 20.0, 20.0, 0.0, 0.0, False),
            SymmetryMeasurement("eye_width", 28.0, 28.0, 0.0, 0.0, False),
        ]
        assert compute_symmetry_index(measurements) == 100.0

    def test_moderate_asymmetry_below_100(self):
        measurements = [
            SymmetryMeasurement("brow_height", 22.0, 20.0, 2.0, 9.5, True),
            SymmetryMeasurement("eye_width", 28.0, 27.0, 1.0, 3.6, False),
        ]
        index = compute_symmetry_index(measurements)
        assert 50 < index < 100

    def test_empty_measurements_is_100(self):
        assert compute_symmetry_index([]) == 100.0

    def test_severe_asymmetry_low_score(self):
        measurements = [
            SymmetryMeasurement("brow_height", 25.0, 15.0, 10.0, 50.0, True),
            SymmetryMeasurement("cheekbone_height", 40.0, 30.0, 10.0, 28.6, True),
        ]
        index = compute_symmetry_index(measurements)
        assert index < 50


class TestFullAnalysis:
    def test_full_analysis_returns_all_components(self):
        det = _make_symmetric_detection()
        cal = _make_calibration()
        result = analyze(det, cal, blendshapes={"mouthSmileLeft": 0.3, "mouthSmileRight": 0.05})

        assert len(result.measurements) == 6
        assert result.global_symmetry_index > 90
        assert len(result.dynamic_asymmetries) >= 1
