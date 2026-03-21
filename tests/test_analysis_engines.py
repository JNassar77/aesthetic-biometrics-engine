"""Tests for Sprint 4 analysis engines (profile, volume, aging)."""

import numpy as np
import pytest

from app.detection.face_landmarker import DetectionResult
from app.utils.pixel_calibration import CalibrationResult
from app.analysis import profile_engine, volume_engine, aging_engine


def _make_detection(image_size: int = 1000) -> DetectionResult:
    """Create a face with realistic landmark positions for engine testing."""
    lm = np.full((478, 3), 0.5, dtype=np.float32)

    # Midline landmarks
    lm[10] = [0.50, 0.12, -0.02]   # trichion
    lm[9] = [0.50, 0.25, 0.01]     # glabella
    lm[168] = [0.50, 0.28, 0.00]   # nasion
    lm[5] = [0.50, 0.35, 0.02]     # rhinion
    lm[4] = [0.50, 0.40, 0.05]     # pronasale (nose tip projects forward)
    lm[2] = [0.50, 0.44, 0.02]     # subnasale
    lm[0] = [0.50, 0.49, 0.03]     # labrale superius
    lm[13] = [0.50, 0.52, 0.02]    # stomion
    lm[17] = [0.50, 0.56, 0.02]    # labrale inferius
    lm[18] = [0.50, 0.60, 0.00]    # mentolabial sulcus
    lm[175] = [0.50, 0.62, 0.01]   # pogonion
    lm[152] = [0.50, 0.68, -0.01]  # gnathion

    # Paired landmarks with z-depth variation
    # Eyes
    lm[263] = [0.65, 0.30, -0.01]  # L eye outer
    lm[33] = [0.35, 0.30, -0.01]   # R eye outer
    lm[362] = [0.57, 0.30, 0.00]   # L eye inner
    lm[133] = [0.43, 0.30, 0.00]   # R eye inner

    # Brows
    lm[282] = [0.62, 0.23, -0.01]  # L brow peak
    lm[52] = [0.38, 0.23, -0.01]   # R brow peak
    lm[276] = [0.70, 0.25, -0.02]  # L brow outer
    lm[46] = [0.30, 0.25, -0.02]   # R brow outer
    lm[285] = [0.55, 0.24, 0.00]   # L brow inner
    lm[55] = [0.45, 0.24, 0.00]    # R brow inner

    # Cheekbones / malar (important for volume)
    lm[330] = [0.72, 0.35, 0.03]   # L cheekbone
    lm[101] = [0.28, 0.35, 0.03]   # R cheekbone
    lm[329] = [0.70, 0.33, 0.04]   # L malar high
    lm[100] = [0.30, 0.33, 0.04]   # R malar high
    lm[425] = [0.65, 0.42, 0.01]   # L malar low
    lm[205] = [0.35, 0.42, 0.01]   # R malar low

    # Infraorbital / tear trough
    lm[253] = [0.60, 0.32, -0.02]  # L infraorbital (recessed)
    lm[23] = [0.40, 0.32, -0.02]   # R infraorbital

    # Alar
    lm[309] = [0.55, 0.43, 0.02]
    lm[79] = [0.45, 0.43, 0.02]

    # Mouth corners
    lm[291] = [0.60, 0.52, 0.01]
    lm[61] = [0.40, 0.52, 0.01]

    # Gonion (jaw angle)
    lm[365] = [0.78, 0.58, -0.03]
    lm[136] = [0.22, 0.58, -0.03]

    # Temporal
    lm[251] = [0.80, 0.20, -0.05]  # L temporal
    lm[21] = [0.20, 0.20, -0.05]   # R temporal

    # Preauricular
    lm[356] = [0.85, 0.35, -0.06]
    lm[127] = [0.15, 0.35, -0.06]

    # Cupid's bow
    lm[267] = [0.53, 0.485, 0.03]
    lm[37] = [0.47, 0.485, 0.03]

    # Iris
    lm[469] = [0.67, 0.30, 0.00]
    lm[471] = [0.63, 0.30, 0.00]
    lm[474] = [0.37, 0.30, 0.00]
    lm[476] = [0.33, 0.30, 0.00]

    return DetectionResult(
        landmarks=lm,
        blendshapes={
            "browInnerUp": 0.05,
            "browDownLeft": 0.08,
            "browDownRight": 0.06,
            "browOuterUpLeft": 0.03,
            "browOuterUpRight": 0.04,
            "mouthSmileLeft": 0.04,
            "mouthSmileRight": 0.03,
            "eyeSquintLeft": 0.12,
            "eyeSquintRight": 0.10,
            "jawOpen": 0.02,
            "mouthPucker": 0.01,
        },
        transformation_matrix=None,
        image_width=image_size,
        image_height=image_size,
    )


def _make_calibration() -> CalibrationResult:
    return CalibrationResult(px_per_mm=3.0, method="iris", confidence=0.9)


# ───────── Profile Engine Tests ─────────

class TestProfileEngine:
    def test_e_line_analysis(self):
        det = _make_detection()
        cal = _make_calibration()
        result = profile_engine.analyze_e_line(det, cal)

        assert isinstance(result.upper_lip_to_eline_mm, float)
        assert isinstance(result.lower_lip_to_eline_mm, float)

    def test_nasal_profile(self):
        det = _make_detection()
        cal = _make_calibration()
        result = profile_engine.analyze_nasal_profile(det, cal)

        assert result.nasolabial_angle_deg > 0
        assert result.nasofrontal_angle_deg > 0
        assert result.nasal_projection_ratio >= 0

    def test_chin_analysis(self):
        det = _make_detection()
        cal = _make_calibration()
        result = profile_engine.analyze_chin(det, cal)

        assert result.chin_height_mm > 0

    def test_cervicomental(self):
        det = _make_detection()
        cal = _make_calibration()
        result = profile_engine.analyze_cervicomental(det, cal)

        assert result is not None
        assert result.cervicomental_angle_deg > 0

    def test_steiner_line(self):
        det = _make_detection()
        cal = _make_calibration()
        result = profile_engine.analyze_steiner_line(det, cal)

        assert result is not None

    def test_full_analysis(self):
        det = _make_detection()
        cal = _make_calibration()
        result = profile_engine.analyze(det, cal)

        assert result.e_line is not None
        assert result.nasal is not None
        assert result.chin is not None


# ───────── Volume Engine Tests ─────────

class TestVolumeEngine:
    def test_ogee_curve(self):
        det = _make_detection()
        cal = _make_calibration()
        result = volume_engine.analyze_ogee(det, cal)

        assert result.score >= 0
        assert isinstance(result.is_flattened, bool)

    def test_temporal_volume(self):
        det = _make_detection()
        cal = _make_calibration()
        result = volume_engine.analyze_temporal(det, cal)

        assert result.asymmetry_mm >= 0
        assert isinstance(result.is_hollowed, bool)

    def test_tear_trough(self):
        det = _make_detection()
        cal = _make_calibration()
        result = volume_engine.analyze_tear_trough(det, cal)

        assert 0 <= result.severity <= 10
        assert result.asymmetry_mm >= 0

    def test_jowl_assessment(self):
        det = _make_detection()
        cal = _make_calibration()
        result = volume_engine.analyze_jowl(det, cal)

        assert result.jawline_break_detected in (True, False)

    def test_full_analysis(self):
        det = _make_detection()
        cal = _make_calibration()
        result = volume_engine.analyze(det, cal)

        assert result.ogee is not None
        assert result.temporal is not None
        assert result.tear_trough is not None
        assert result.jowl is not None


# ───────── Aging Engine Tests ─────────

class TestAgingEngine:
    def test_muscle_tonus(self):
        bs = {"browInnerUp": 0.15, "browDownLeft": 0.2, "browDownRight": 0.18}
        result = aging_engine.analyze_muscle_tonus(bs)

        assert 0 <= result.frontalis_compensation <= 1
        assert 0 <= result.corrugator_activity <= 1
        assert 0 <= result.overall_muscle_age_indicator <= 10

    def test_muscle_tonus_empty_blendshapes(self):
        result = aging_engine.analyze_muscle_tonus({})
        assert result.overall_muscle_age_indicator >= 0

    def test_gravitational_drift(self):
        det = _make_detection()
        cal = _make_calibration()
        result = aging_engine.analyze_gravitational_drift(det, cal)

        assert result.brow_descent_mm >= 0
        assert result.malar_descent_mm >= 0
        assert 0 <= result.overall_drift_score <= 10

    def test_periorbital(self):
        det = _make_detection()
        cal = _make_calibration()
        bs = {"eyeSquintLeft": 0.15, "eyeSquintRight": 0.12}
        result = aging_engine.analyze_periorbital(det, bs, cal)

        assert 0 <= result.crow_feet_potential <= 1
        assert 0 <= result.under_lid_laxity <= 1

    def test_age_bracket_estimation(self):
        assert "25-30" in aging_engine.estimate_age_bracket(1.0)
        assert "40-45" in aging_engine.estimate_age_bracket(5.0)
        assert "55+" in aging_engine.estimate_age_bracket(8.0)

    def test_full_analysis(self):
        det = _make_detection()
        cal = _make_calibration()
        bs = det.blendshapes
        result = aging_engine.analyze(det, cal, blendshapes=bs)

        assert result.muscle_tonus is not None
        assert result.gravitational_drift is not None
        assert result.periorbital is not None
        assert 0 <= result.overall_aging_severity <= 10
        assert result.estimated_biological_age_bracket != ""

    def test_analysis_without_blendshapes(self):
        det = _make_detection()
        cal = _make_calibration()
        result = aging_engine.analyze(det, cal)

        assert result is not None
        assert result.overall_aging_severity >= 0
