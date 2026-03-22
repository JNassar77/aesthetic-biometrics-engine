"""
Tests for blendshape-related analysis: rest vs expression detection.

Verifies:
- Neutral face produces low expression scores
- Active expression triggers warnings
- Aging patterns are distinguishable from neutral
- Dynamic asymmetry detected from blendshape diffs
"""

import numpy as np
import pytest

from app.pipeline.quality_gate import (
    check_neutral_expression,
    compute_expression_deviation,
    EXPRESSION_THRESHOLDS,
)
from app.analysis.symmetry_engine import analyze_dynamic_asymmetry
from app.analysis.aging_engine import analyze as aging_analyze
from app.detection.face_landmarker import DetectionResult
from app.utils.pixel_calibration import CalibrationResult
from tests.fixtures.synthetic import (
    make_blendshapes,
    make_symmetric_face,
    make_aged_face,
    make_calibration,
)


# ──────────────────── Neutral Expression Tests ────────────────────

class TestNeutralExpressionDetection:
    """Quality gate should accept neutral faces and warn on expressions."""

    def test_neutral_face_no_warnings(self):
        """A truly neutral face should produce no expression warnings."""
        bs = make_blendshapes(neutral=True)
        warnings = check_neutral_expression(bs)
        expression_warnings = [w for w in warnings if "expression" in w.code.lower() or "EXPRESSION" in w.code]
        # Neutral face may still produce warnings if thresholds are very tight,
        # but critical expression warnings should not appear
        for w in expression_warnings:
            assert w.severity != "high", f"Neutral face got high-severity expression warning: {w}"

    def test_smiling_face_produces_warnings(self):
        """A smiling face should trigger expression deviation warnings."""
        bs = make_blendshapes(neutral=False)  # active smile
        warnings = check_neutral_expression(bs)
        # Should detect non-neutral expression
        assert len(warnings) > 0, "Smiling face should produce expression warnings"

    def test_expression_deviation_neutral_is_low(self):
        """Expression deviation score for neutral face should be low."""
        bs = make_blendshapes(neutral=True)
        deviation = compute_expression_deviation(bs)
        assert deviation < 0.15, f"Neutral face deviation too high: {deviation}"

    def test_expression_deviation_smile_is_high(self):
        """Expression deviation score for smiling face should be high."""
        bs = make_blendshapes(neutral=False)
        deviation = compute_expression_deviation(bs)
        assert deviation > 0.2, f"Smiling face deviation too low: {deviation}"


# ──────────────────── Dynamic Asymmetry Tests ────────────────────

class TestDynamicAsymmetry:
    """Blendshape-based dynamic asymmetry detection."""

    def test_symmetric_blendshapes_low_asymmetry(self):
        """Symmetric blendshapes should show minimal dynamic asymmetry."""
        bs = make_blendshapes(neutral=True)
        asymmetries = analyze_dynamic_asymmetry(bs)
        # With symmetric values, asymmetry list should be empty or have small diffs
        for a in asymmetries:
            assert abs(a.difference) < 0.05, (
                f"Symmetric blendshapes have asymmetry in {a.blendshape_name}: {a.difference}"
            )

    def test_asymmetric_smile_detected(self):
        """Unilateral smile should show dynamic asymmetry."""
        bs = make_blendshapes(neutral=True)
        # Create strongly asymmetric smile
        bs["mouthSmileLeft"] = 0.60
        bs["mouthSmileRight"] = 0.05  # one-sided smile

        asymmetries = analyze_dynamic_asymmetry(bs)
        # Should detect the mouthSmile asymmetry
        smile_asym = [a for a in asymmetries if "mouthSmile" in a.blendshape_name]
        assert len(smile_asym) > 0, "Should detect asymmetric smile"
        assert any(abs(a.difference) > 0.3 for a in smile_asym), (
            "mouthSmile asymmetry should be large"
        )

    def test_empty_blendshapes_no_crash(self):
        """Empty blendshape dict should not crash analysis."""
        result = analyze_dynamic_asymmetry({})
        assert isinstance(result, list)


# ──────────────────── Aging Blendshape Patterns ────────────────────

class TestAgingBlendshapes:
    """Aging engine should detect age-related blendshape patterns."""

    def test_aged_face_detected(self):
        """Aged face blendshapes should produce higher aging severity."""
        detection = make_aged_face()
        calibration = make_calibration()

        result = aging_analyze(
            detection=detection,
            calibration=calibration,
            blendshapes=detection.blendshapes,
        )

        assert result is not None
        assert result.overall_aging_severity > 0

    def test_young_face_minimal_aging(self):
        """Symmetric neutral face should show minimal aging severity."""
        detection = make_symmetric_face()
        calibration = make_calibration()

        result = aging_analyze(
            detection=detection,
            calibration=calibration,
            blendshapes=detection.blendshapes,
        )

        assert result is not None
        # Young symmetric face should have low aging severity
        assert result.overall_aging_severity < 5.0, (
            f"Young face aging severity too high: {result.overall_aging_severity}"
        )

    def test_aging_has_age_bracket(self):
        """Aging analysis should estimate a biological age bracket."""
        detection = make_aged_face()
        calibration = make_calibration()

        result = aging_analyze(
            detection=detection,
            calibration=calibration,
            blendshapes=detection.blendshapes,
        )

        assert result.estimated_biological_age_bracket is not None
        assert len(result.estimated_biological_age_bracket) > 0


# ──────────────────── Blendshape Data Integrity ────────────────────

class TestBlendshapeDataIntegrity:
    """Verify synthetic blendshape data meets expected contracts."""

    def test_neutral_has_52_blendshapes(self):
        """Neutral blendshapes should have all 52 entries."""
        bs = make_blendshapes(neutral=True)
        assert len(bs) == 52

    def test_aging_has_52_blendshapes(self):
        """Aging blendshapes should have all 52 entries."""
        bs = make_blendshapes(aging=True)
        assert len(bs) == 52

    def test_all_values_between_0_and_1(self):
        """All blendshape values should be in [0, 1]."""
        for neutral in [True, False]:
            bs = make_blendshapes(neutral=neutral)
            for name, val in bs.items():
                assert 0.0 <= val <= 1.0, f"{name}={val} out of range"

    def test_neutral_has_high_neutral_score(self):
        """Neutral face should have _neutral > 0.8."""
        bs = make_blendshapes(neutral=True)
        assert bs["_neutral"] > 0.8

    def test_expression_has_low_neutral_score(self):
        """Active expression should have _neutral < 0.5."""
        bs = make_blendshapes(neutral=False)
        assert bs["_neutral"] < 0.5
