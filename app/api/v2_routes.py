"""
V2 API routes for the Aesthetic Biometrics Engine.

Endpoints:
- POST /api/v2/assessment — 3 images → full zone analysis + treatment plan
- POST /api/v2/compare — compare two assessments (before/after)
- GET  /api/v2/patients/{id}/history — patient assessment history
- GET  /api/v2/health — health check
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import settings
from app.pipeline.orchestrator import run_pipeline, PipelineResult
from app.models.schemas_v2 import (
    AssessmentResponse,
    CalibrationResponse,
    CompareRequest,
    ComparisonResponse,
    ContraindicationResponse,
    GlobalMetricsResponse,
    FacialThirdsResponse,
    HeadPoseResponse,
    HeatmapEntryResponse,
    HealthResponse,
    ImageQualityResponse,
    MeasurementDeltaResponse,
    NeurotoxinRecommendationResponse,
    PatientHistoryResponse,
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

router = APIRouter()

MAX_IMAGE_BYTES = settings.max_image_size_mb * 1024 * 1024


# ──────────────────────── Converters: Internal → API Response ────────────────────────

def _convert_zone_result(zr) -> ZoneResultResponse:
    """Convert internal ZoneResult to API response model."""
    return ZoneResultResponse(
        zone_id=zr.zone_id,
        zone_name=zr.zone_name,
        region=zr.region,
        severity=zr.severity,
        findings=[
            ZoneFindingResponse(
                description=f.description,
                severity_contribution=f.severity_contribution,
                source_view=f.source_view,
            )
            for f in zr.findings
        ],
        measurements=[
            ZoneMeasurementResponse(
                name=m.name,
                value=m.value,
                unit=m.unit,
                ideal_min=m.ideal_min,
                ideal_max=m.ideal_max,
                deviation_pct=m.deviation_pct,
            )
            for m in zr.measurements
        ],
        primary_view=zr.primary_view,
        confirmed_by=zr.confirmed_by,
        calibration_method=zr.calibration_method,
    )


def _convert_treatment_plan(plan) -> TreatmentPlanResponse:
    """Convert internal TreatmentPlan to API response model."""

    def _concern(c) -> TreatmentConcernResponse:
        return TreatmentConcernResponse(
            priority=c.priority,
            zone_id=c.zone_id,
            zone_name=c.zone_name,
            severity=c.severity,
            concern=c.concern,
            filler_recommendations=[
                ProductRecommendationResponse(
                    products=r.products,
                    category=r.category,
                    techniques=r.techniques,
                    depth=r.depth,
                    volume_range_ml=list(r.volume_range_ml),
                    description=r.description,
                    safety_notes=r.safety_notes,
                )
                for r in c.filler_recommendations
            ],
            neurotoxin_recommendations=[
                NeurotoxinRecommendationResponse(
                    target_muscle=n.target_muscle,
                    products=n.products,
                    dose_range_units=list(n.dose_range_units),
                    safety_notes=n.safety_notes,
                )
                for n in c.neurotoxin_recommendations
            ],
            is_high_risk=c.is_high_risk,
            vascular_risk=list(c.vascular_risk),
            session=c.session,
        )

    def _contra(ci) -> ContraindicationResponse:
        return ContraindicationResponse(
            severity=ci.severity.value if hasattr(ci.severity, "value") else str(ci.severity),
            zone_id=ci.zone_id,
            code=ci.code,
            message=ci.message,
            recommendation=ci.recommendation,
        )

    def _session(s) -> SessionPlanResponse:
        return SessionPlanResponse(
            session_number=s.session_number,
            concerns=[_concern(c) for c in s.concerns],
            total_filler_volume_ml=list(s.total_filler_volume_ml),
            total_neurotoxin_units=list(s.total_neurotoxin_units),
            focus=s.focus,
        )

    return TreatmentPlanResponse(
        primary_concerns=[_concern(c) for c in plan.primary_concerns],
        secondary_concerns=[_concern(c) for c in plan.secondary_concerns],
        contraindications=[_contra(ci) for ci in plan.contraindications],
        sessions=[_session(s) for s in plan.sessions],
        total_volume_estimate_ml=list(plan.total_volume_estimate_ml),
        total_neurotoxin_units=list(plan.total_neurotoxin_units),
        session_count=plan.session_count,
    )


def _build_assessment_response(
    result: PipelineResult,
    patient_id: UUID | None = None,
) -> AssessmentResponse:
    """Build the full AssessmentResponse from a PipelineResult."""

    # Image quality per view
    image_quality: dict[str, ImageQualityResponse] = {}
    for view_name in ("frontal", "profile", "oblique"):
        vr = result.view_results.get(view_name)
        if vr is None:
            image_quality[view_name] = ImageQualityResponse(
                accepted=False,
                warnings=[QualityWarningResponse(
                    code="NOT_PROVIDED",
                    message=f"No {view_name} image was provided.",
                    severity="high",
                )],
                confidence=0.0,
            )
        else:
            image_quality[view_name] = ImageQualityResponse(
                accepted=vr.accepted,
                warnings=[
                    QualityWarningResponse(
                        code=w.code,
                        message=w.message,
                        severity=w.severity,
                    )
                    for w in vr.quality_warnings
                ],
                confidence=vr.confidence,
            )

    # Global metrics
    zr = result.zone_report
    gm = zr.global_metrics if zr else None

    # Head pose from frontal view
    head_pose_resp = None
    frontal_vr = result.view_results.get("frontal")
    if frontal_vr and frontal_vr.head_pose:
        hp = frontal_vr.head_pose
        head_pose_resp = HeadPoseResponse(yaw=hp.yaw, pitch=hp.pitch, roll=hp.roll)

    if gm:
        global_metrics = GlobalMetricsResponse(
            symmetry_index=gm.symmetry_index,
            facial_thirds=FacialThirdsResponse(
                upper=gm.facial_thirds.get("upper", 0.33),
                middle=gm.facial_thirds.get("middle", 0.33),
                lower=gm.facial_thirds.get("lower", 0.34),
            ),
            golden_ratio_deviation=gm.golden_ratio_deviation,
            lip_ratio=gm.lip_ratio,
            head_pose=head_pose_resp,
        )
    else:
        global_metrics = GlobalMetricsResponse(
            symmetry_index=0.0,
            facial_thirds=FacialThirdsResponse(upper=0.33, middle=0.33, lower=0.34),
            golden_ratio_deviation=0.0,
            head_pose=head_pose_resp,
        )

    # Zones
    zones = [_convert_zone_result(z) for z in zr.zones] if zr else []

    # Aesthetic score
    aesthetic_score = zr.aesthetic_score if zr else 0.0

    # Treatment plan
    tp = result.treatment_plan
    treatment_plan = _convert_treatment_plan(tp) if tp else TreatmentPlanResponse()

    # Calibration
    cal = zr.calibration if zr else None
    calibration = CalibrationResponse(
        method=cal.method if cal else "unknown",
        px_per_mm=cal.px_per_mm if cal else 0.0,
        confidence=cal.confidence if cal else 0.0,
    )

    return AssessmentResponse(
        assessment_id=result.assessment_id,
        patient_id=patient_id,
        image_quality=image_quality,
        global_metrics=global_metrics,
        zones=zones,
        aesthetic_score=aesthetic_score,
        treatment_plan=treatment_plan,
        calibration=calibration,
        processing_time_ms=result.processing_time_ms,
        views_analyzed=result.views_analyzed,
    )


# ──────────────────────── Endpoints ────────────────────────

@router.post(
    "/assessment",
    response_model=AssessmentResponse,
    summary="Run a complete 3-view facial assessment",
    description=(
        "Upload frontal, profile, and oblique images for a complete zone-based "
        "analysis with treatment plan. At least one image is required."
    ),
)
async def create_assessment(
    frontal: UploadFile | None = File(None, description="Frontal (0°) face image"),
    profile: UploadFile | None = File(None, description="Profile (90°) face image"),
    oblique: UploadFile | None = File(None, description="Oblique (45°) face image"),
    patient_id: str | None = Form(None, description="Patient UUID (optional)"),
):
    """POST /api/v2/assessment — 3 images → full analysis + treatment plan."""

    # Validate: at least one image
    if frontal is None and profile is None and oblique is None:
        raise HTTPException(status_code=400, detail="At least one image must be provided.")

    # Read image bytes
    frontal_bytes = await frontal.read() if frontal else None
    profile_bytes = await profile.read() if profile else None
    oblique_bytes = await oblique.read() if oblique else None

    # Size validation
    for name, data in [("frontal", frontal_bytes), ("profile", profile_bytes), ("oblique", oblique_bytes)]:
        if data and len(data) > MAX_IMAGE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"{name} image exceeds maximum size of {settings.max_image_size_mb}MB.",
            )

    # Parse patient_id
    parsed_patient_id: UUID | None = None
    if patient_id:
        try:
            parsed_patient_id = UUID(patient_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid patient_id format. Must be a UUID.")

    # Run pipeline
    result = run_pipeline(
        frontal_bytes=frontal_bytes,
        profile_bytes=profile_bytes,
        oblique_bytes=oblique_bytes,
        patient_id=parsed_patient_id,
    )

    # Check for fatal errors
    if result.zone_report is None:
        error_msg = "; ".join(result.errors) if result.errors else "Analysis failed."
        # Check if it's a no-face issue
        no_face_views = [
            vn for vn, vr in result.view_results.items()
            if vr.rejection_reason == "NO_FACE_DETECTED"
        ]
        if no_face_views:
            raise HTTPException(
                status_code=422,
                detail=f"No face detected in: {', '.join(no_face_views)}. {error_msg}",
            )
        raise HTTPException(status_code=422, detail=error_msg)

    return _build_assessment_response(result, parsed_patient_id)


@router.post(
    "/compare",
    response_model=ComparisonResponse,
    summary="Compare two assessments (before/after)",
    description="Computes zone-by-zone deltas and improvement score between two assessments.",
)
async def compare_assessments(request: CompareRequest):
    """POST /api/v2/compare — before/after comparison.

    NOTE: This endpoint requires Supabase to be configured to fetch stored
    assessments. Currently returns a placeholder until Sprint 9 integration.
    """
    # TODO (Sprint 9): Fetch pre/post ZoneReports from Supabase
    # For now, return 501 until Supabase integration is complete
    raise HTTPException(
        status_code=501,
        detail=(
            "Comparison endpoint requires Supabase integration (Sprint 9). "
            "Use the comparison_engine.compare() function directly for now."
        ),
    )


@router.get(
    "/patients/{patient_id}/history",
    response_model=PatientHistoryResponse,
    summary="Get patient assessment history",
    description="Returns all assessments for a patient, ordered by date.",
)
async def get_patient_history(patient_id: UUID):
    """GET /api/v2/patients/{id}/history — assessment timeline.

    NOTE: Requires Supabase integration. Placeholder until Sprint 9.
    """
    # TODO (Sprint 9): Query Supabase for patient's assessments
    raise HTTPException(
        status_code=501,
        detail=(
            "Patient history endpoint requires Supabase integration (Sprint 9). "
            "Assessments will be queryable once persistence is configured."
        ),
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="V2 API health check",
)
async def health_check():
    """GET /api/v2/health — check API and model status."""
    import os
    from app.detection.face_landmarker import DEFAULT_MODEL_PATH

    model_loaded = os.path.exists(DEFAULT_MODEL_PATH)

    supabase_connected = bool(settings.supabase_url and settings.supabase_key)

    return HealthResponse(
        status="healthy",
        version="2.0.0",
        model_loaded=model_loaded,
        supabase_connected=supabase_connected,
    )
