"""Tests for the clinical PDF report (Task 11)."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.models.schemas_v2 import (
    AssessmentResponse, CalibrationResponse, ContraindicationResponse,
    FacialThirdsResponse, GlobalMetricsResponse, HeadPoseResponse,
    ImageQualityResponse, ProductRecommendationResponse, Reconstruction3DResponse,
    TreatmentConcernResponse, TreatmentPlanResponse, ZoneFindingResponse,
    ZoneMeasurementResponse, ZoneResultResponse,
)
from app.services.pdf_report import render_assessment_report
from app.api.v2_routes import _assessment_response_from_row


def _sample_response(with_reconstruction=True, with_zones=True) -> AssessmentResponse:
    zones = []
    if with_zones:
        zones = [ZoneResultResponse(
            zone_id="Tt1", zone_name="Tear Trough", region="midface",
            severity=6.5, primary_view="frontal", confirmed_by=["oblique"],
            findings=[ZoneFindingResponse(
                description="Infraorbital hollow 3.2mm",
                severity_contribution=6.5, source_view="frontal")],
            measurements=[
                ZoneMeasurementResponse(name="tear_trough_depth_left", value=3.2, unit="mm",
                                        estimated=True, ideal_min=0.0, ideal_max=1.0, deviation_pct=220.0),
                ZoneMeasurementResponse(name="lip_ratio", value=1.5, unit="ratio",
                                        estimated=False, ideal_min=1.4, ideal_max=1.7),
            ],
        )]
    rec = None
    if with_reconstruction:
        rec = Reconstruction3DResponse(
            available=True, depth_source="multi_view_3d",
            views_used=["frontal", "oblique_left", "oblique_right"],
            n_views=3, angular_spread_deg=62.8, reprojection_rms_mm=2.683,
        )
    return AssessmentResponse(
        assessment_id=uuid4(),
        image_quality={"frontal": ImageQualityResponse(accepted=True, confidence=0.9)},
        global_metrics=GlobalMetricsResponse(
            symmetry_index=88.5,
            facial_thirds=FacialThirdsResponse(upper=0.33, middle=0.34, lower=0.33),
            golden_ratio_deviation=4.2, lip_ratio=1.5,
            head_pose=HeadPoseResponse(yaw=-1.2, pitch=4.8, roll=0.5)),
        zones=zones,
        aesthetic_score=82.0,
        treatment_plan=TreatmentPlanResponse(
            primary_concerns=[TreatmentConcernResponse(
                priority=1, zone_id="Tt1", zone_name="Tear Trough", severity=6.5,
                concern="Volume loss", is_high_risk=True, vascular_risk=["angular artery"],
                filler_recommendations=[ProductRecommendationResponse(
                    products=["Restylane"], category="HA filler", techniques=["cannula"],
                    depth="deep", volume_range_ml=[0.5, 1.0], description="x")],
                session=1)],
            contraindications=[ContraindicationResponse(
                severity="CAUTION", code="VASCULAR",
                message="High vascular risk zone", recommendation="Use cannula")],
            total_volume_estimate_ml=[0.5, 1.0], total_neurotoxin_units=[0, 0],
            session_count=1),
        calibration=CalibrationResponse(method="iris", px_per_mm=4.6, confidence=0.95, reliable=True),
        reconstruction=rec,
        processing_time_ms=842,
        views_analyzed=["frontal", "oblique_left", "oblique_right", "profile"],
        warnings=[],
    )


class TestRenderReport:
    def test_produces_valid_pdf(self):
        pdf = render_assessment_report(_sample_response())
        assert pdf[:5] == b"%PDF-"
        assert len(pdf) > 1500

    def test_handles_no_reconstruction(self):
        pdf = render_assessment_report(_sample_response(with_reconstruction=False))
        assert pdf[:5] == b"%PDF-"

    def test_handles_empty_zones_and_plan(self):
        resp = _sample_response(with_zones=False)
        resp.treatment_plan = TreatmentPlanResponse()
        pdf = render_assessment_report(resp)
        assert pdf[:5] == b"%PDF-"

    def test_handles_unreliable_calibration_warning(self):
        resp = _sample_response()
        resp.calibration.reliable = False
        resp.warnings = ["CALIBRATION_UNRELIABLE: method=face_width_estimate"]
        pdf = render_assessment_report(resp)
        assert pdf[:5] == b"%PDF-"

    def test_patient_label_used(self):
        pdf = render_assessment_report(_sample_response(), patient_label="DEMO-001")
        assert pdf[:5] == b"%PDF-"


class TestAssessmentResponseFromRow:
    def test_reconstructs_core_fields_and_estimated_flag(self):
        sample = _sample_response()
        row = {
            "id": str(sample.assessment_id),
            "patient_id": None,
            "image_quality": {"frontal": {"accepted": True, "confidence": 0.9}},
            "global_metrics": sample.global_metrics.model_dump(),
            "zones": [z.model_dump() for z in sample.zones],
            "treatment_plan": sample.treatment_plan.model_dump(),
            "aesthetic_score": 82.0,
            "calibration_method": "iris",
            "engine_version": "2.2.0",
            "processing_time_ms": 842,
        }
        resp = _assessment_response_from_row(row)
        assert resp.aesthetic_score == 82.0
        assert resp.calibration.method == "iris"
        assert resp.calibration.reliable is False  # full calibration not stored
        assert len(resp.zones) == 1
        # estimated flags survive the round-trip → report honesty preserved
        est = [m for m in resp.zones[0].measurements if m.estimated]
        assert any(m.name == "tear_trough_depth_left" for m in est)
        # and the reconstructed response renders
        assert render_assessment_report(resp)[:5] == b"%PDF-"

    def test_handles_missing_global_metrics(self):
        row = {"id": str(uuid4()), "zones": [], "aesthetic_score": 100.0}
        resp = _assessment_response_from_row(row)
        assert resp.global_metrics.symmetry_index == 0.0


class TestReportEndpoints:
    def setup_method(self):
        self.client = TestClient(app)

    def test_post_report_returns_pdf(self):
        body = _sample_response().model_dump(mode="json")
        resp = self.client.post("/api/v2/report", json=body)
        assert resp.status_code == 200, resp.text
        assert resp.headers["content-type"] == "application/pdf"
        assert resp.content[:5] == b"%PDF-"

    def test_get_report_503_without_supabase(self, monkeypatch):
        monkeypatch.setattr(settings, "supabase_url", "")
        resp = self.client.get(f"/api/v2/assessment/{uuid4()}/report")
        assert resp.status_code == 503

    def test_get_report_renders_stored_assessment(self, monkeypatch):
        sample = _sample_response()
        row = {
            "id": str(sample.assessment_id), "patient_id": None,
            "image_quality": {}, "global_metrics": sample.global_metrics.model_dump(),
            "zones": [z.model_dump() for z in sample.zones],
            "treatment_plan": sample.treatment_plan.model_dump(),
            "aesthetic_score": 82.0, "calibration_method": "iris",
            "engine_version": "2.2.0", "processing_time_ms": 842,
        }
        monkeypatch.setattr(settings, "supabase_url", "http://supabase.local")

        async def _fake_get(aid):
            return row

        monkeypatch.setattr("app.services.supabase_service.get_assessment", _fake_get)
        resp = self.client.get(f"/api/v2/assessment/{sample.assessment_id}/report")
        assert resp.status_code == 200, resp.text
        assert resp.content[:5] == b"%PDF-"

    def test_get_report_404_when_missing(self, monkeypatch):
        monkeypatch.setattr(settings, "supabase_url", "http://supabase.local")

        async def _fake_get(aid):
            return None

        monkeypatch.setattr("app.services.supabase_service.get_assessment", _fake_get)
        resp = self.client.get(f"/api/v2/assessment/{uuid4()}/report")
        assert resp.status_code == 404
