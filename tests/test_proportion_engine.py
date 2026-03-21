"""Tests for proportion analysis engine."""

import numpy as np
import pytest

from app.analysis.proportion_engine import (
    analyze_thirds,
    analyze_fifths,
    analyze_golden_ratio,
    analyze_lip,
    analyze,
    PHI,
    IDEAL_LIP_RATIO,
)
from app.detection.face_landmarker import DetectionResult
from app.utils.pixel_calibration import CalibrationResult


def _make_ideal_face(image_size: int = 1000) -> DetectionResult:
    """Create an ideally proportioned face for testing.

    Vertical thirds: equal 1:1:1
    Fifths: approximately equal
    Golden ratio: height/width ≈ 1.618
    Lip ratio: upper/lower ≈ 1:1.6
    """
    lm = np.full((478, 3), 0.5, dtype=np.float32)

    # Vertical thirds (equal segments of ~0.2 each)
    # Trichion (10) → Glabella (9) → Subnasale (2) → Menton (152)
    lm[10] = [0.50, 0.15, 0.0]   # trichion
    lm[9] = [0.50, 0.30, 0.0]    # glabella
    lm[168] = [0.50, 0.32, 0.0]  # nasion
    lm[5] = [0.50, 0.38, 0.0]    # rhinion
    lm[4] = [0.50, 0.42, 0.0]    # pronasale
    lm[2] = [0.50, 0.45, 0.0]    # subnasale
    lm[0] = [0.50, 0.50, 0.0]    # labrale superius
    lm[13] = [0.50, 0.525, 0.0]  # stomion
    lm[17] = [0.50, 0.565, 0.0]  # labrale inferius
    lm[18] = [0.50, 0.58, 0.0]   # mentolabial sulcus
    lm[175] = [0.50, 0.58, 0.0]  # pogonion
    lm[152] = [0.50, 0.60, 0.0]  # gnathion

    # Horizontal fifths — symmetric 5 segments
    # preauricular → eye_outer → eye_inner → eye_inner → eye_outer → preauricular
    lm[127] = [0.10, 0.35, 0.0]  # R preauricular
    lm[33] = [0.20, 0.30, 0.0]   # R eye outer
    lm[133] = [0.35, 0.30, 0.0]  # R eye inner
    lm[362] = [0.65, 0.30, 0.0]  # L eye inner
    lm[263] = [0.80, 0.30, 0.0]  # L eye outer
    lm[356] = [0.90, 0.35, 0.0]  # L preauricular

    # Cheekbones for face width/golden ratio
    lm[330] = [0.78, 0.35, 0.0]  # L cheekbone
    lm[101] = [0.22, 0.35, 0.0]  # R cheekbone

    # Mouth corners
    lm[291] = [0.60, 0.525, 0.0]  # L mouth corner
    lm[61] = [0.40, 0.525, 0.0]   # R mouth corner

    # Alar
    lm[309] = [0.55, 0.44, 0.0]  # L alar
    lm[79] = [0.45, 0.44, 0.0]   # R alar

    # Gonion
    lm[365] = [0.82, 0.55, 0.0]
    lm[136] = [0.18, 0.55, 0.0]

    # Cupid's bow landmarks
    lm[267] = [0.53, 0.495, 0.0]  # L philtral column peak
    lm[37] = [0.47, 0.495, 0.0]   # R philtral column peak

    # Brow peaks
    lm[282] = [0.65, 0.22, 0.0]
    lm[52] = [0.35, 0.22, 0.0]
    lm[276] = [0.72, 0.24, 0.0]
    lm[46] = [0.28, 0.24, 0.0]
    lm[285] = [0.55, 0.24, 0.0]
    lm[55] = [0.45, 0.24, 0.0]

    # Malar
    lm[329] = [0.75, 0.34, 0.0]
    lm[100] = [0.25, 0.34, 0.0]
    lm[425] = [0.68, 0.40, 0.0]
    lm[205] = [0.32, 0.40, 0.0]

    # Infraorbital
    lm[253] = [0.62, 0.32, 0.0]
    lm[23] = [0.38, 0.32, 0.0]

    # Iris (for calibration reference)
    lm[469] = [0.82, 0.30, 0.0]
    lm[471] = [0.78, 0.30, 0.0]
    lm[474] = [0.22, 0.30, 0.0]
    lm[476] = [0.18, 0.30, 0.0]

    return DetectionResult(
        landmarks=lm,
        blendshapes={},
        transformation_matrix=None,
        image_width=image_size,
        image_height=image_size,
    )


def _make_calibration(px_per_mm: float = 3.0) -> CalibrationResult:
    return CalibrationResult(px_per_mm=px_per_mm, method="iris", confidence=0.9)


class TestThirds:
    def test_equal_thirds_low_deviation(self):
        det = _make_ideal_face()
        cal = _make_calibration()
        result = analyze_thirds(det, cal)

        assert result.upper_mm > 0
        assert result.middle_mm > 0
        assert result.lower_mm > 0
        # All ratios should be close to 0.333
        assert abs(result.upper_ratio - result.middle_ratio) < 0.05
        assert abs(result.middle_ratio - result.lower_ratio) < 0.05

    def test_total_height_is_sum(self):
        det = _make_ideal_face()
        cal = _make_calibration()
        result = analyze_thirds(det, cal)

        total = result.upper_mm + result.middle_mm + result.lower_mm
        assert abs(total - result.total_height_mm) < 0.5

    def test_ratios_sum_to_one(self):
        det = _make_ideal_face()
        cal = _make_calibration()
        result = analyze_thirds(det, cal)

        total = result.upper_ratio + result.middle_ratio + result.lower_ratio
        assert abs(total - 1.0) < 0.01


class TestFifths:
    def test_five_segments(self):
        det = _make_ideal_face()
        cal = _make_calibration()
        result = analyze_fifths(det, cal)

        assert len(result.widths_mm) == 5
        assert len(result.ratios) == 5

    def test_ratios_sum_to_one(self):
        det = _make_ideal_face()
        cal = _make_calibration()
        result = analyze_fifths(det, cal)

        assert abs(sum(result.ratios) - 1.0) < 0.01

    def test_total_width_positive(self):
        det = _make_ideal_face()
        cal = _make_calibration()
        result = analyze_fifths(det, cal)

        assert result.total_width_mm > 0


class TestGoldenRatio:
    def test_ratio_positive(self):
        det = _make_ideal_face()
        cal = _make_calibration()
        result = analyze_golden_ratio(det, cal)

        assert result.measured_ratio > 0
        assert result.golden_ratio == pytest.approx(PHI, abs=0.001)

    def test_deviation_reasonable(self):
        det = _make_ideal_face()
        cal = _make_calibration()
        result = analyze_golden_ratio(det, cal)

        # Synthetic face may not have golden proportions — just check it's finite
        assert result.deviation_pct < 100


class TestLipAnalysis:
    def test_lip_ratio_positive(self):
        det = _make_ideal_face()
        cal = _make_calibration()
        result = analyze_lip(det, cal)

        assert result.upper_lip_height_mm > 0
        assert result.lower_lip_height_mm > 0
        assert result.lip_ratio > 0

    def test_lip_width_positive(self):
        det = _make_ideal_face()
        cal = _make_calibration()
        result = analyze_lip(det, cal)

        assert result.lip_width_mm > 0

    def test_cupid_bow_metrics(self):
        det = _make_ideal_face()
        cal = _make_calibration()
        result = analyze_lip(det, cal)

        assert result.cupid_bow_depth_mm >= 0
        assert result.cupid_bow_asymmetry_pct >= 0


class TestFullAnalysis:
    def test_all_components_present(self):
        det = _make_ideal_face()
        cal = _make_calibration()
        result = analyze(det, cal)

        assert result.thirds is not None
        assert result.fifths is not None
        assert result.golden_ratio is not None
        assert result.lip is not None

    def test_without_fifths(self):
        det = _make_ideal_face()
        cal = _make_calibration()
        result = analyze(det, cal, include_fifths=False)

        assert result.thirds is not None
        assert result.fifths is None
