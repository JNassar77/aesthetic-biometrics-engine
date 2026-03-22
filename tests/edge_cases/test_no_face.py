"""
Edge case tests: no face detected, corrupt images, partial views.

These tests verify that the pipeline degrades gracefully — producing
errors/warnings instead of exceptions.
"""

import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from app.detection.face_landmarker import DetectionResult, NoFaceResult
from app.pipeline.orchestrator import run_pipeline, _process_single_view, PipelineResult, ViewResult
from app.pipeline.quality_gate import QualityWarning


# ──────────────────── Corrupt / Empty Images ────────────────────

class TestCorruptImage:
    """Images that cannot be decoded should produce IMAGE_DECODE_FAILED."""

    def test_empty_bytes_returns_decode_failed(self):
        """Empty bytes should fail gracefully."""
        with patch("app.pipeline.orchestrator.FaceLandmarkerV2"):
            mock_landmarker = MagicMock()
            result = _process_single_view(b"", "frontal", mock_landmarker)

        assert not result.accepted
        assert result.rejection_reason == "IMAGE_DECODE_FAILED"
        codes = [w.code for w in result.quality_warnings]
        assert "IMAGE_DECODE_FAILED" in codes

    def test_random_bytes_returns_decode_failed(self):
        """Random non-image bytes should fail gracefully."""
        with patch("app.pipeline.orchestrator.FaceLandmarkerV2"):
            mock_landmarker = MagicMock()
            result = _process_single_view(b"\x00\xff\xfe\x01" * 100, "frontal", mock_landmarker)

        assert not result.accepted
        assert result.rejection_reason == "IMAGE_DECODE_FAILED"

    def test_truncated_jpeg_returns_decode_failed(self):
        """A truncated JPEG header should fail gracefully."""
        # JPEG magic bytes but truncated
        truncated = b"\xff\xd8\xff\xe0\x00\x10JFIF"
        with patch("app.pipeline.orchestrator.FaceLandmarkerV2"):
            mock_landmarker = MagicMock()
            result = _process_single_view(truncated, "frontal", mock_landmarker)

        assert not result.accepted


# ──────────────────── No Face in Valid Image ────────────────────

class TestNoFaceDetected:
    """Valid images with no face should produce NO_FACE_DETECTED."""

    def _make_blank_image_bytes(self, width: int = 640, height: int = 480) -> bytes:
        """Create a valid PNG image with no face (solid gray)."""
        import cv2
        img = np.full((height, width, 3), 180, dtype=np.uint8)
        _, buf = cv2.imencode(".png", img)
        return buf.tobytes()

    def test_blank_image_no_face(self):
        """A blank image should return NO_FACE_DETECTED."""
        mock_landmarker = MagicMock()
        mock_landmarker.detect.return_value = NoFaceResult()

        result = _process_single_view(
            self._make_blank_image_bytes(), "frontal", mock_landmarker
        )

        assert not result.accepted
        assert result.rejection_reason == "NO_FACE_DETECTED"
        codes = [w.code for w in result.quality_warnings]
        assert "NO_FACE_DETECTED" in codes

    def test_no_face_includes_view_name_in_message(self):
        """Warning message should mention the view name."""
        mock_landmarker = MagicMock()
        mock_landmarker.detect.return_value = NoFaceResult()

        result = _process_single_view(
            self._make_blank_image_bytes(), "profile", mock_landmarker
        )

        no_face_warnings = [w for w in result.quality_warnings if w.code == "NO_FACE_DETECTED"]
        assert len(no_face_warnings) == 1
        assert "profile" in no_face_warnings[0].message


# ──────────────────── Pipeline-Level Edge Cases ────────────────────

class TestPipelineNoViews:
    """Pipeline with no processable views should return errors, not raise."""

    def test_all_none_images(self):
        """No images provided → error, no exception."""
        with patch("app.pipeline.orchestrator.FaceLandmarkerV2"):
            result = run_pipeline(
                frontal_bytes=None,
                profile_bytes=None,
                oblique_bytes=None,
                landmarker=MagicMock(),
            )

        assert isinstance(result, PipelineResult)
        assert result.zone_report is None
        assert result.treatment_plan is None
        assert len(result.views_analyzed) == 0

    def test_all_corrupt_images(self):
        """All images corrupt → error with descriptive message."""
        result = run_pipeline(
            frontal_bytes=b"corrupt",
            profile_bytes=b"corrupt",
            oblique_bytes=b"corrupt",
            landmarker=MagicMock(),
        )

        assert result.zone_report is None
        assert len(result.errors) > 0
        assert "No views could be processed" in result.errors[0]


class TestPipelinePartialViews:
    """Pipeline should handle partial success (some views fail)."""

    def _make_valid_image_bytes(self) -> bytes:
        import cv2
        img = np.full((480, 640, 3), 128, dtype=np.uint8)
        _, buf = cv2.imencode(".png", img)
        return buf.tobytes()

    def test_one_of_three_views_succeeds(self):
        """If only frontal succeeds, views_analyzed should contain only frontal."""
        from tests.fixtures.synthetic import make_symmetric_face

        mock_landmarker = MagicMock()

        # First call (frontal): return valid detection
        valid_detection = make_symmetric_face()
        # Subsequent calls (profile, oblique): no face
        mock_landmarker.detect.side_effect = [
            valid_detection,  # frontal detect
            valid_detection,  # frontal re-detect
            NoFaceResult(),   # profile detect
            NoFaceResult(),   # oblique detect
        ]

        result = run_pipeline(
            frontal_bytes=self._make_valid_image_bytes(),
            profile_bytes=self._make_valid_image_bytes(),
            oblique_bytes=self._make_valid_image_bytes(),
            landmarker=mock_landmarker,
        )

        assert "frontal" in result.views_analyzed
        assert "profile" not in result.views_analyzed
        assert "oblique" not in result.views_analyzed
        # Zone report should still be produced (partial data)
        assert result.zone_report is not None

    def test_missing_landmarker_model(self):
        """If model file is missing, pipeline returns error not exception."""
        result = run_pipeline(
            frontal_bytes=self._make_valid_image_bytes(),
            landmarker=None,  # Will try to create and fail
        )

        assert isinstance(result, PipelineResult)
        assert len(result.errors) > 0


class TestQualityWarningStructure:
    """Quality warnings should always have required fields."""

    def test_warning_has_code_message_severity(self):
        w = QualityWarning(code="TEST", message="test message", severity="high")
        assert w.code == "TEST"
        assert w.message == "test message"
        assert w.severity == "high"

    def test_warning_default_severity(self):
        w = QualityWarning(code="TEST", message="test")
        assert w.severity == "medium"
