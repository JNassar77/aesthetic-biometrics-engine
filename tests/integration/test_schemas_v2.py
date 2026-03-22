"""Tests for V2 Pydantic API schemas."""

import pytest
from uuid import uuid4, UUID
from datetime import datetime, timezone

from app.models.schemas_v2 import (
    AssessmentResponse,
    CalibrationResponse,
    CompareRequest,
    ComparisonResponse,
    ContraindicationResponse,
    FacialThirdsResponse,
    GlobalMetricsResponse,
    HeadPoseResponse,
    HeatmapEntryResponse,
    HealthResponse,
    ImageQualityResponse,
    MeasurementDeltaResponse,
    NeurotoxinRecommendationResponse,
    PatientHistoryResponse,
    AssessmentSummary,
    ProductRecommendationResponse,
    QualityWarningResponse,
    SessionPlanResponse,
    TreatmentConcernResponse,
    TreatmentPlanResponse,
    ZoneDeltaResponse,
    ZoneFindingResponse,
    ZoneMeasurementResponse,
    ZoneResultResponse,
)


# ──────────────────────── Quality Models ────────────────────────

class TestQualityWarningResponse:
    def test_basic_creation(self):
        w = QualityWarningResponse(code="LOW_RESOLUTION", message="Image below 720p.")
        assert w.code == "LOW_RESOLUTION"
        assert w.severity == "low"

    def test_with_severity(self):
        w = QualityWarningResponse(code="NO_FACE", message="No face.", severity="critical")
        assert w.severity == "critical"


class TestImageQualityResponse:
    def test_accepted_image(self):
        iq = ImageQualityResponse(accepted=True, confidence=0.95)
        assert iq.accepted is True
        assert iq.warnings == []

    def test_rejected_image_with_warnings(self):
        iq = ImageQualityResponse(
            accepted=False,
            warnings=[QualityWarningResponse(code="NO_FACE", message="No face detected.", severity="critical")],
            confidence=0.0,
        )
        assert iq.accepted is False
        assert len(iq.warnings) == 1


# ──────────────────────── Zone Models ────────────────────────

class TestZoneMeasurementResponse:
    def test_basic(self):
        m = ZoneMeasurementResponse(name="lip_ratio", value=0.476, unit="ratio")
        assert m.name == "lip_ratio"
        assert m.unit == "ratio"

    def test_with_ideal_range(self):
        m = ZoneMeasurementResponse(
            name="ogee_score", value=52, unit="score",
            ideal_min=70, ideal_max=100, deviation_pct=-25.7,
        )
        assert m.ideal_min == 70
        assert m.deviation_pct == -25.7


class TestZoneFindingResponse:
    def test_basic(self):
        f = ZoneFindingResponse(
            description="Malar flattening detected",
            severity_contribution=4.5,
            source_view="oblique",
        )
        assert f.severity_contribution == 4.5

    def test_severity_bounds(self):
        with pytest.raises(Exception):
            ZoneFindingResponse(description="x", severity_contribution=11, source_view="frontal")


class TestZoneResultResponse:
    def test_full_zone(self):
        z = ZoneResultResponse(
            zone_id="Ck2",
            zone_name="Zygomatic Eminence",
            region="midface",
            severity=6.0,
            findings=[ZoneFindingResponse(description="Volume loss", severity_contribution=6.0, source_view="oblique")],
            measurements=[ZoneMeasurementResponse(name="ogee_score", value=52, unit="score")],
            primary_view="oblique",
            confirmed_by=["frontal"],
        )
        assert z.zone_id == "Ck2"
        assert len(z.findings) == 1
        assert z.confirmed_by == ["frontal"]

    def test_severity_bounds(self):
        with pytest.raises(Exception):
            ZoneResultResponse(zone_id="X", zone_name="X", region="x", severity=11, primary_view="frontal")


# ──────────────────────── Treatment Plan Models ────────────────────────

class TestProductRecommendationResponse:
    def test_basic(self):
        p = ProductRecommendationResponse(
            products=["Juvederm Voluma", "Radiesse"],
            category="HA_DEEP",
            techniques=["BOLUS"],
            depth="SUPRAPERIOSTEAL",
            volume_range_ml=[1.0, 1.5],
            description="Deep-plane volumizer",
        )
        assert len(p.products) == 2
        assert p.volume_range_ml == [1.0, 1.5]


class TestTreatmentConcernResponse:
    def test_basic(self):
        tc = TreatmentConcernResponse(
            priority=1,
            zone_id="Ck2",
            zone_name="Zygomatic Eminence",
            severity=6.0,
            concern="Midface volume loss",
        )
        assert tc.priority == 1
        assert tc.is_high_risk is False


class TestTreatmentPlanResponse:
    def test_empty_plan(self):
        tp = TreatmentPlanResponse()
        assert tp.primary_concerns == []
        assert tp.total_volume_estimate_ml == [0.0, 0.0]

    def test_plan_with_concerns(self):
        tp = TreatmentPlanResponse(
            primary_concerns=[
                TreatmentConcernResponse(
                    priority=1, zone_id="Ck2", zone_name="Zygomatic Eminence",
                    severity=6.0, concern="Volume loss",
                ),
            ],
            session_count=2,
            total_volume_estimate_ml=[2.5, 3.5],
        )
        assert len(tp.primary_concerns) == 1
        assert tp.session_count == 2


# ──────────────────────── Assessment Response ────────────────────────

class TestAssessmentResponse:
    def test_minimal_response(self):
        r = AssessmentResponse(
            image_quality={
                "frontal": ImageQualityResponse(accepted=True, confidence=0.9),
                "profile": ImageQualityResponse(accepted=True, confidence=0.85),
                "oblique": ImageQualityResponse(accepted=False, confidence=0.0),
            },
            global_metrics=GlobalMetricsResponse(
                symmetry_index=91.2,
                facial_thirds=FacialThirdsResponse(upper=0.32, middle=0.34, lower=0.34),
                golden_ratio_deviation=4.2,
            ),
            zones=[],
            aesthetic_score=85.0,
            treatment_plan=TreatmentPlanResponse(),
            calibration=CalibrationResponse(method="iris", px_per_mm=5.2, confidence=0.92),
        )
        assert r.engine_version == "2.0.0"
        assert isinstance(r.assessment_id, UUID)
        assert r.aesthetic_score == 85.0

    def test_with_zones_and_plan(self):
        r = AssessmentResponse(
            image_quality={"frontal": ImageQualityResponse(accepted=True, confidence=0.9)},
            global_metrics=GlobalMetricsResponse(
                symmetry_index=85.0,
                facial_thirds=FacialThirdsResponse(upper=0.32, middle=0.34, lower=0.34),
                golden_ratio_deviation=5.0,
            ),
            zones=[
                ZoneResultResponse(
                    zone_id="Ck2", zone_name="Zygomatic Eminence",
                    region="midface", severity=6.0, primary_view="oblique",
                ),
            ],
            aesthetic_score=72.0,
            treatment_plan=TreatmentPlanResponse(session_count=1),
            calibration=CalibrationResponse(method="iris", px_per_mm=5.0, confidence=0.9),
        )
        assert len(r.zones) == 1

    def test_json_serialization(self):
        r = AssessmentResponse(
            image_quality={"frontal": ImageQualityResponse(accepted=True, confidence=0.9)},
            global_metrics=GlobalMetricsResponse(
                symmetry_index=90.0,
                facial_thirds=FacialThirdsResponse(upper=0.33, middle=0.33, lower=0.34),
                golden_ratio_deviation=3.0,
            ),
            zones=[],
            aesthetic_score=90.0,
            treatment_plan=TreatmentPlanResponse(),
            calibration=CalibrationResponse(method="iris", px_per_mm=5.0, confidence=0.9),
        )
        data = r.model_dump(mode="json")
        assert "assessment_id" in data
        assert "zones" in data
        assert "treatment_plan" in data


# ──────────────────────── Comparison Models ────────────────────────

class TestCompareRequest:
    def test_basic(self):
        req = CompareRequest(
            pre_assessment_id=uuid4(),
            post_assessment_id=uuid4(),
        )
        assert req.treatment_date is None

    def test_with_notes(self):
        req = CompareRequest(
            pre_assessment_id=uuid4(),
            post_assessment_id=uuid4(),
            treatment_date="2026-03-15",
            treatment_notes="Midface filler 1.5ml bilateral",
        )
        assert req.treatment_notes is not None


class TestComparisonResponse:
    def test_basic(self):
        pre_id = uuid4()
        post_id = uuid4()
        cr = ComparisonResponse(
            pre_assessment_id=pre_id,
            post_assessment_id=post_id,
            zone_deltas=[],
            improvement_score=65.0,
            aesthetic_score_pre=72.0,
            aesthetic_score_post=85.0,
            aesthetic_score_delta=13.0,
        )
        assert cr.improvement_score == 65.0
        assert cr.zones_improved == 0


class TestZoneDeltaResponse:
    def test_improved(self):
        zd = ZoneDeltaResponse(
            zone_id="Ck2", zone_name="Zygomatic Eminence", region="midface",
            pre_severity=6.0, post_severity=2.5,
            severity_delta=-3.5, severity_improvement_pct=58.3,
            status="improved",
        )
        assert zd.status == "improved"
        assert zd.severity_delta < 0


# ──────────────────────── Patient History ────────────────────────

class TestPatientHistoryResponse:
    def test_empty_history(self):
        pid = uuid4()
        h = PatientHistoryResponse(patient_id=pid)
        assert h.total_count == 0
        assert h.assessments == []

    def test_with_assessments(self):
        pid = uuid4()
        h = PatientHistoryResponse(
            patient_id=pid,
            assessments=[
                AssessmentSummary(
                    assessment_id=uuid4(),
                    timestamp=datetime.now(timezone.utc),
                    aesthetic_score=75.0,
                    zones_count=12,
                    primary_concern="Midface volume loss",
                    views_analyzed=["frontal", "profile", "oblique"],
                ),
            ],
            total_count=1,
        )
        assert len(h.assessments) == 1


# ──────────────────────── Health ────────────────────────

class TestHealthResponse:
    def test_default(self):
        h = HealthResponse()
        assert h.status == "healthy"
        assert h.version == "2.0.0"
        assert h.model_loaded is False

    def test_with_model(self):
        h = HealthResponse(model_loaded=True, supabase_connected=True)
        assert h.model_loaded is True
