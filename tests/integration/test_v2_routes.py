"""Tests for V2 API routes."""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from app.api.v2_routes import (
    _convert_zone_result,
    _convert_treatment_plan,
    _build_assessment_response,
)
from app.models.zone_models import ZoneResult, ZoneFinding, ZoneMeasurement
from app.pipeline.orchestrator import PipelineResult, ViewResult
from app.analysis.zone_analyzer import ZoneReport
from app.models.zone_models import GlobalMetrics, CalibrationInfo


# ──────────────────────── Converter Tests ────────────────────────

class TestConvertZoneResult:
    def test_basic_conversion(self):
        zr = ZoneResult(
            zone_id="Ck2",
            zone_name="Zygomatic Eminence",
            region="midface",
            severity=6.0,
            findings=[
                ZoneFinding(description="Volume loss", severity_contribution=6.0, source_view="oblique"),
            ],
            measurements=[
                ZoneMeasurement(name="ogee_score", value=52.0, unit="score", ideal_min=70.0, ideal_max=100.0),
            ],
            primary_view="oblique",
            confirmed_by=["frontal"],
            calibration_method="iris",
        )

        resp = _convert_zone_result(zr)

        assert resp.zone_id == "Ck2"
        assert resp.severity == 6.0
        assert len(resp.findings) == 1
        assert resp.findings[0].description == "Volume loss"
        assert len(resp.measurements) == 1
        assert resp.measurements[0].ideal_min == 70.0

    def test_empty_findings_and_measurements(self):
        zr = ZoneResult(
            zone_id="T1", zone_name="Temporal", region="upper_face",
            severity=0.0, primary_view="oblique",
        )
        resp = _convert_zone_result(zr)
        assert resp.findings == []
        assert resp.measurements == []


class TestConvertTreatmentPlan:
    def test_empty_plan(self):
        from app.treatment.plan_generator import TreatmentPlan
        plan = TreatmentPlan(
            primary_concerns=[],
            secondary_concerns=[],
            contraindications=[],
            sessions=[],
            total_volume_estimate_ml=(0.0, 0.0),
            total_neurotoxin_units=(0, 0),
            session_count=0,
        )
        resp = _convert_treatment_plan(plan)
        assert resp.primary_concerns == []
        assert resp.session_count == 0

    def test_plan_with_concerns(self):
        from app.treatment.plan_generator import (
            TreatmentPlan, TreatmentConcern, ProductRecommendation,
            SessionPlan,
        )
        from app.treatment.contraindication_check import Contraindication, ContraindicationSeverity

        concern = TreatmentConcern(
            priority=1,
            zone_id="Ck2",
            zone_name="Zygomatic Eminence",
            region="midface",
            severity=6.0,
            concern="Midface volume loss",
            filler_recommendations=[
                ProductRecommendation(
                    products=["Juvederm Voluma"],
                    category="HA_DEEP",
                    techniques=["BOLUS"],
                    depth="SUPRAPERIOSTEAL",
                    volume_range_ml=(1.0, 1.5),
                    description="Deep volumizer",
                ),
            ],
            neurotoxin_recommendations=[],
            is_high_risk=False,
            vascular_risk=[],
            session=1,
        )

        contra = Contraindication(
            severity=ContraindicationSeverity.CAUTION,
            zone_id="Tt1",
            code="VASCULAR_RISK",
            message="Near angular artery",
            recommendation="Aspirate before injection",
        )

        session = SessionPlan(
            session_number=1,
            concerns=[concern],
            total_filler_volume_ml=(2.0, 3.0),
            total_neurotoxin_units=(0, 0),
            focus="Structural volume restoration",
        )

        plan = TreatmentPlan(
            primary_concerns=[concern],
            secondary_concerns=[],
            contraindications=[contra],
            sessions=[session],
            total_volume_estimate_ml=(2.0, 3.0),
            total_neurotoxin_units=(0, 0),
            session_count=1,
        )

        resp = _convert_treatment_plan(plan)

        assert len(resp.primary_concerns) == 1
        assert resp.primary_concerns[0].zone_id == "Ck2"
        assert len(resp.primary_concerns[0].filler_recommendations) == 1
        assert resp.primary_concerns[0].filler_recommendations[0].volume_range_ml == [1.0, 1.5]
        assert len(resp.contraindications) == 1
        assert resp.contraindications[0].severity == "caution"
        assert len(resp.sessions) == 1


# ──────────────────────── Build Assessment Response Tests ────────────────────────

class TestBuildAssessmentResponse:
    def _make_pipeline_result(self):
        """Create a minimal successful PipelineResult."""
        from app.detection.face_landmarker import DetectionResult
        from app.utils.pixel_calibration import CalibrationResult
        from app.detection.head_pose import HeadPose
        from app.treatment.plan_generator import TreatmentPlan
        import numpy as np

        detection = DetectionResult(
            landmarks=np.random.rand(478, 3).astype(np.float32),
            blendshapes={"mouthSmileLeft": 0.05},
            transformation_matrix=np.eye(4),
            image_width=1024,
            image_height=1024,
        )
        calibration = CalibrationResult(px_per_mm=5.0, method="iris", confidence=0.92)

        view_result = ViewResult(
            view="frontal",
            detection=detection,
            calibration=calibration,
            accepted=True,
            confidence=0.92,
        )
        view_result.head_pose = HeadPose(yaw=1.0, pitch=-0.5, roll=0.3)

        zone_report = ZoneReport(
            zones=[
                ZoneResult(
                    zone_id="Ck2", zone_name="Zygomatic Eminence",
                    region="midface", severity=6.0, primary_view="oblique",
                    findings=[ZoneFinding(description="Volume loss", severity_contribution=6.0, source_view="oblique")],
                ),
            ],
            global_metrics=GlobalMetrics(
                symmetry_index=91.2,
                facial_thirds={"upper": 0.32, "middle": 0.34, "lower": 0.34},
                golden_ratio_deviation=4.2,
                aesthetic_score=78.0,
            ),
            calibration=CalibrationInfo(method="iris", px_per_mm=5.0, confidence=0.92),
            aesthetic_score=78.0,
            expression_deviation=0.05,
            views_analyzed=["frontal"],
        )

        plan = TreatmentPlan(
            primary_concerns=[], secondary_concerns=[],
            contraindications=[], sessions=[],
            total_volume_estimate_ml=(0.0, 0.0), total_neurotoxin_units=(0, 0), session_count=0,
        )

        result = PipelineResult(
            zone_report=zone_report,
            treatment_plan=plan,
            view_results={"frontal": view_result},
            views_analyzed=["frontal"],
            processing_time_ms=150,
        )
        return result

    def test_builds_valid_response(self):
        result = self._make_pipeline_result()
        resp = _build_assessment_response(result, patient_id=None)

        assert resp.engine_version == "2.1.0"
        assert resp.aesthetic_score == 78.0
        assert len(resp.zones) == 1
        assert resp.zones[0].zone_id == "Ck2"
        assert resp.calibration.method == "iris"
        assert resp.processing_time_ms == 150

    def test_includes_image_quality_for_missing_views(self):
        result = self._make_pipeline_result()
        resp = _build_assessment_response(result)

        # Frontal provided and accepted
        assert resp.image_quality["frontal"].accepted is True
        # Profile and oblique not provided
        assert resp.image_quality["profile"].accepted is False
        assert resp.image_quality["oblique"].accepted is False
        assert resp.image_quality["profile"].warnings[0].code == "NOT_PROVIDED"

    def test_head_pose_included(self):
        result = self._make_pipeline_result()
        resp = _build_assessment_response(result)

        assert resp.global_metrics.head_pose is not None
        assert resp.global_metrics.head_pose.yaw == 1.0

    def test_with_patient_id(self):
        result = self._make_pipeline_result()
        pid = uuid4()
        resp = _build_assessment_response(result, patient_id=pid)
        assert resp.patient_id == pid

    def test_json_serializable(self):
        result = self._make_pipeline_result()
        resp = _build_assessment_response(result)
        data = resp.model_dump(mode="json")
        assert isinstance(data, dict)
        assert "zones" in data
        assert "treatment_plan" in data
        assert "image_quality" in data
