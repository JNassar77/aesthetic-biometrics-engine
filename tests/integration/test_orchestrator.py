"""Tests for the Pipeline Orchestrator."""

import pytest
from unittest.mock import patch, MagicMock
from uuid import UUID

import numpy as np

from app.pipeline.orchestrator import (
    _process_single_view,
    run_pipeline,
    ViewResult,
    PipelineResult,
)
from app.detection.face_landmarker import DetectionResult, NoFaceResult
from app.utils.pixel_calibration import CalibrationResult
from app.detection.head_pose import HeadPose
from app.pipeline.quality_gate import QualityWarning


# ──────────────────────── Fixtures ────────────────────────

def _make_detection(width=1024, height=1024, blendshapes=None):
    """Create a mock DetectionResult with realistic landmarks."""
    landmarks = np.random.rand(478, 3).astype(np.float32)
    # Make landmarks within normalized range
    landmarks[:, 0] = np.clip(landmarks[:, 0], 0.1, 0.9)
    landmarks[:, 1] = np.clip(landmarks[:, 1], 0.1, 0.9)
    landmarks[:, 2] = np.clip(landmarks[:, 2], -0.1, 0.1)

    return DetectionResult(
        landmarks=landmarks,
        blendshapes=blendshapes or {"mouthSmileLeft": 0.05, "mouthSmileRight": 0.05},
        transformation_matrix=np.eye(4),
        image_width=width,
        image_height=height,
        face_detected=True,
    )


def _make_calibration():
    """Create a mock CalibrationResult."""
    return CalibrationResult(
        px_per_mm=5.0,
        method="iris",
        confidence=0.92,
        iris_width_px=58.5,
    )


def _make_image_bytes():
    """Create minimal valid image bytes (1x1 black JPEG)."""
    # Minimal JPEG
    import struct
    # Create a small numpy array and encode as JPEG-like bytes
    # Using a simple PNG instead (smaller valid file)
    return (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
        b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
        b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )


# ──────────────────────── ViewResult Tests ────────────────────────

class TestViewResult:
    def test_default_values(self):
        vr = ViewResult(view="frontal")
        assert vr.accepted is True
        assert vr.quality_warnings == []
        assert vr.detection is None

    def test_rejected(self):
        vr = ViewResult(view="profile", accepted=False, rejection_reason="NO_FACE_DETECTED")
        assert vr.accepted is False


# ──────────────────────── PipelineResult Tests ────────────────────────

class TestPipelineResult:
    def test_default_values(self):
        pr = PipelineResult()
        assert isinstance(pr.assessment_id, UUID)
        assert pr.zone_report is None
        assert pr.views_analyzed == []
        assert pr.errors == []

    def test_with_views(self):
        pr = PipelineResult(views_analyzed=["frontal", "profile"])
        assert len(pr.views_analyzed) == 2


# ──────────────────────── _process_single_view Tests ────────────────────────

class TestProcessSingleView:
    @patch("app.pipeline.orchestrator.preprocess")
    def test_decode_failure_returns_rejected(self, mock_preprocess):
        mock_preprocess.return_value = None
        mock_landmarker = MagicMock()

        result = _process_single_view(b"bad_bytes", "frontal", mock_landmarker)

        assert result.accepted is False
        assert result.rejection_reason == "IMAGE_DECODE_FAILED"
        assert any(w.code == "IMAGE_DECODE_FAILED" for w in result.quality_warnings)

    @patch("app.pipeline.orchestrator.calibrate")
    @patch("app.pipeline.orchestrator.reprocess_with_face_center")
    @patch("app.pipeline.orchestrator.preprocess")
    def test_no_face_returns_rejected(self, mock_preprocess, mock_reprocess, mock_calibrate):
        mock_preprocess.return_value = np.zeros((1024, 1024, 3), dtype=np.uint8)
        mock_landmarker = MagicMock()
        mock_landmarker.detect.return_value = NoFaceResult()

        result = _process_single_view(b"image_bytes", "frontal", mock_landmarker)

        assert result.accepted is False
        assert result.rejection_reason == "NO_FACE_DETECTED"

    @patch("app.pipeline.orchestrator.extract_head_pose")
    @patch("app.pipeline.orchestrator.calibrate")
    @patch("app.pipeline.orchestrator.reprocess_with_face_center")
    @patch("app.pipeline.orchestrator.preprocess")
    def test_successful_detection(self, mock_preprocess, mock_reprocess, mock_calibrate, mock_pose):
        mock_preprocess.return_value = np.zeros((1024, 1024, 3), dtype=np.uint8)
        mock_reprocess.return_value = np.zeros((1024, 1024, 3), dtype=np.uint8)
        detection = _make_detection()
        mock_landmarker = MagicMock()
        mock_landmarker.detect.return_value = detection
        mock_calibrate.return_value = _make_calibration()
        mock_pose.return_value = HeadPose(yaw=1.0, pitch=-0.5, roll=0.3)

        result = _process_single_view(b"image_bytes", "frontal", mock_landmarker)

        assert result.accepted is True
        assert result.detection is not None
        assert result.calibration is not None
        assert result.head_pose is not None

    @patch("app.pipeline.orchestrator.extract_head_pose")
    @patch("app.pipeline.orchestrator.check_hard_pose_rejection")
    @patch("app.pipeline.orchestrator.calibrate")
    @patch("app.pipeline.orchestrator.reprocess_with_face_center")
    @patch("app.pipeline.orchestrator.preprocess")
    def test_hard_pose_rejection(self, mock_preprocess, mock_reprocess, mock_calibrate, mock_rejection, mock_pose):
        mock_preprocess.return_value = np.zeros((1024, 1024, 3), dtype=np.uint8)
        mock_reprocess.return_value = np.zeros((1024, 1024, 3), dtype=np.uint8)
        detection = _make_detection()
        mock_landmarker = MagicMock()
        mock_landmarker.detect.return_value = detection
        mock_pose.return_value = HeadPose(yaw=45.0, pitch=0.0, roll=0.0)
        mock_rejection.return_value = QualityWarning(
            code="HEAD_POSE_REJECTED",
            message="Head too rotated for frontal view.",
            severity="critical",
        )

        result = _process_single_view(b"image_bytes", "frontal", mock_landmarker)

        assert result.accepted is False
        assert result.rejection_reason == "HEAD_POSE_REJECTED"


# ──────────────────────── run_pipeline Tests ────────────────────────

class TestRunPipeline:
    @patch("app.pipeline.orchestrator.FaceLandmarkerV2")
    def test_no_images_returns_error(self, mock_landmarker_cls):
        """Pipeline with no images should fail with errors."""
        mock_landmarker_cls.return_value = MagicMock()
        result = run_pipeline()
        assert result.zone_report is None
        assert len(result.errors) > 0

    @patch("app.pipeline.orchestrator.plan_generate")
    @patch("app.pipeline.orchestrator.zone_analyze")
    @patch("app.pipeline.orchestrator._process_single_view")
    @patch("app.pipeline.orchestrator.FaceLandmarkerV2")
    def test_single_view_success(self, mock_cls, mock_process, mock_analyze, mock_plan):
        mock_cls.return_value = MagicMock()

        # Mock a successful frontal view
        view_result = ViewResult(
            view="frontal",
            detection=_make_detection(),
            calibration=_make_calibration(),
            accepted=True,
            confidence=0.9,
        )
        mock_process.return_value = view_result

        # Mock zone analysis
        from app.analysis.zone_analyzer import ZoneReport
        from app.models.zone_models import GlobalMetrics, CalibrationInfo
        mock_analyze.return_value = ZoneReport(
            zones=[],
            global_metrics=GlobalMetrics(
                symmetry_index=90.0,
                facial_thirds={"upper": 0.33, "middle": 0.33, "lower": 0.34},
                golden_ratio_deviation=3.0,
                aesthetic_score=85.0,
            ),
            calibration=CalibrationInfo(method="iris", px_per_mm=5.0, confidence=0.92),
            aesthetic_score=85.0,
            expression_deviation=0.05,
            views_analyzed=["frontal"],
        )

        # Mock plan generator
        from app.treatment.plan_generator import TreatmentPlan
        mock_plan.return_value = TreatmentPlan(
            primary_concerns=[],
            secondary_concerns=[],
            contraindications=[],
            sessions=[],
            total_volume_estimate_ml=0.0,
            total_neurotoxin_units=0,
            session_count=0,
        )

        result = run_pipeline(frontal_bytes=b"frontal_image")

        assert result.zone_report is not None
        assert result.treatment_plan is not None
        assert "frontal" in result.views_analyzed
        assert result.processing_time_ms >= 0

    @patch("app.pipeline.orchestrator._process_single_view")
    @patch("app.pipeline.orchestrator.FaceLandmarkerV2")
    def test_all_views_rejected(self, mock_cls, mock_process):
        mock_cls.return_value = MagicMock()
        mock_process.return_value = ViewResult(
            view="frontal", accepted=False, rejection_reason="NO_FACE_DETECTED",
        )

        result = run_pipeline(
            frontal_bytes=b"bad",
            profile_bytes=b"bad",
            oblique_bytes=b"bad",
        )

        assert result.zone_report is None
        assert len(result.errors) > 0

    def test_model_not_found_returns_error(self):
        """If model file is missing, should return gracefully."""
        with patch("app.pipeline.orchestrator.FaceLandmarkerV2") as mock_cls:
            mock_cls.side_effect = FileNotFoundError("Model not found")
            result = run_pipeline(frontal_bytes=b"image")
            assert len(result.errors) > 0
            assert "Model not found" in result.errors[0]

    @patch("app.pipeline.orchestrator.plan_generate")
    @patch("app.pipeline.orchestrator.zone_analyze")
    @patch("app.pipeline.orchestrator._process_single_view")
    @patch("app.pipeline.orchestrator.FaceLandmarkerV2")
    def test_plan_failure_nonblocking(self, mock_cls, mock_process, mock_analyze, mock_plan):
        """Treatment plan failure should not block zone report."""
        mock_cls.return_value = MagicMock()

        view_result = ViewResult(
            view="frontal",
            detection=_make_detection(),
            calibration=_make_calibration(),
            accepted=True,
            confidence=0.9,
        )
        mock_process.return_value = view_result

        from app.analysis.zone_analyzer import ZoneReport
        from app.models.zone_models import GlobalMetrics, CalibrationInfo
        mock_analyze.return_value = ZoneReport(
            zones=[],
            global_metrics=GlobalMetrics(
                symmetry_index=90.0,
                facial_thirds={"upper": 0.33, "middle": 0.33, "lower": 0.34},
                golden_ratio_deviation=3.0,
                aesthetic_score=85.0,
            ),
            calibration=CalibrationInfo(method="iris", px_per_mm=5.0, confidence=0.92),
            aesthetic_score=85.0,
            expression_deviation=0.05,
        )

        mock_plan.side_effect = RuntimeError("Plan generation exploded")

        result = run_pipeline(frontal_bytes=b"image")

        # Zone report should still exist
        assert result.zone_report is not None
        # Treatment plan should be None
        assert result.treatment_plan is None
        # Error should be logged
        assert any("Treatment plan" in e for e in result.errors)
