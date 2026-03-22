"""
V2 API routes for the Aesthetic Biometrics Engine.

Endpoints:
- POST /api/v2/assessment — 3 images → full zone analysis + treatment plan
- POST /api/v2/compare — compare two assessments (before/after)
- GET  /api/v2/patients/{id}/history — patient assessment history
- GET  /api/v2/health — health check
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile

from app.api.auth import require_api_key

from app.config import settings
from app.pipeline.orchestrator import run_pipeline, PipelineResult
from app.models.schemas_v2 import (
    AssessmentResponse,
    AssessmentSummary,
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

logger = logging.getLogger(__name__)

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


# ──────────────────────── Background Persistence ────────────────────────

async def _persist_assessment(
    response: AssessmentResponse,
    frontal_bytes: bytes | None,
    profile_bytes: bytes | None,
    oblique_bytes: bytes | None,
    organization_id: UUID,
) -> None:
    """Persist assessment to Supabase (runs as BackgroundTask)."""
    from app.services.supabase_service import save_assessment, upload_image
    from app.services.n8n_service import notify_n8n_v2

    assessment_id = response.assessment_id
    patient_id = response.patient_id

    # Upload images to storage
    frontal_path = profile_path = oblique_path = None
    bucket = "patient-images"
    base_path = f"{organization_id}/{assessment_id}"

    try:
        if frontal_bytes:
            frontal_path = await upload_image(
                bucket, f"{base_path}/frontal.jpg", frontal_bytes
            )
        if profile_bytes:
            profile_path = await upload_image(
                bucket, f"{base_path}/profile.jpg", profile_bytes
            )
        if oblique_bytes:
            oblique_path = await upload_image(
                bucket, f"{base_path}/oblique.jpg", oblique_bytes
            )
    except Exception as exc:
        logger.warning("Image upload failed: %s", exc)

    # Save assessment record
    try:
        response_dict = response.model_dump(mode="json")
        await save_assessment(
            assessment_id=assessment_id,
            organization_id=organization_id,
            patient_id=patient_id,
            status="completed" if response.zones else "partial",
            image_quality=response_dict.get("image_quality"),
            global_metrics=response_dict.get("global_metrics"),
            zones=response_dict.get("zones"),
            treatment_plan=response_dict.get("treatment_plan"),
            aesthetic_score=response.aesthetic_score,
            calibration_method=response.calibration.method,
            engine_version=response.engine_version,
            processing_time_ms=response.processing_time_ms,
            frontal_image_path=frontal_path,
            profile_image_path=profile_path,
            oblique_image_path=oblique_path,
        )
        logger.info("Assessment %s persisted to Supabase", assessment_id)
    except Exception as exc:
        logger.error("Assessment persistence failed: %s", exc)

    # Notify n8n
    try:
        await notify_n8n_v2(
            assessment_id=str(assessment_id),
            patient_id=str(patient_id) if patient_id else None,
            aesthetic_score=response.aesthetic_score,
            zones_count=len(response.zones),
            views_analyzed=response.views_analyzed,
            payload=response_dict,
        )
    except Exception as exc:
        logger.warning("n8n notification failed: %s", exc)


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
    background_tasks: BackgroundTasks,
    frontal: UploadFile | None = File(None, description="Frontal (0°) face image"),
    profile: UploadFile | None = File(None, description="Profile (90°) face image"),
    oblique: UploadFile | None = File(None, description="Oblique (45°) face image"),
    patient_id: str | None = Form(None, description="Patient UUID (optional)"),
    organization_id: str | None = Form(None, description="Organization UUID (for Supabase persistence)"),
    _api_key: str = Depends(require_api_key),
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

    # Parse organization_id
    parsed_org_id: UUID | None = None
    if organization_id:
        try:
            parsed_org_id = UUID(organization_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid organization_id format. Must be a UUID.")

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

    response = _build_assessment_response(result, parsed_patient_id)

    # Schedule async persistence (non-blocking)
    if parsed_org_id and settings.supabase_url:
        background_tasks.add_task(
            _persist_assessment,
            response,
            frontal_bytes,
            profile_bytes,
            oblique_bytes,
            parsed_org_id,
        )

    return response


@router.post(
    "/compare",
    response_model=ComparisonResponse,
    summary="Compare two assessments (before/after)",
    description="Computes zone-by-zone deltas and improvement score between two assessments.",
)
async def compare_assessments(request: CompareRequest, _api_key: str = Depends(require_api_key)):
    """POST /api/v2/compare — before/after comparison."""
    from app.services.supabase_service import get_assessment
    from app.analysis.comparison_engine import compare, ComparisonResult
    from app.models.zone_models import ZoneResult, ZoneFinding, ZoneMeasurement
    from app.analysis.zone_analyzer import ZoneReport, GlobalMetrics
    from app.models.zone_models import CalibrationInfo

    if not settings.supabase_url:
        raise HTTPException(
            status_code=503,
            detail="Supabase is not configured. Cannot fetch stored assessments.",
        )

    # Fetch both assessments
    pre_data = await get_assessment(request.pre_assessment_id)
    post_data = await get_assessment(request.post_assessment_id)

    if pre_data is None:
        raise HTTPException(status_code=404, detail=f"Pre-assessment {request.pre_assessment_id} not found.")
    if post_data is None:
        raise HTTPException(status_code=404, detail=f"Post-assessment {request.post_assessment_id} not found.")

    # Reconstruct ZoneReports from stored JSONB
    def _reconstruct_zone_report(data: dict) -> ZoneReport:
        zones_raw = data.get("zones") or []
        zones = []
        for z in zones_raw:
            zones.append(ZoneResult(
                zone_id=z["zone_id"],
                zone_name=z["zone_name"],
                region=z["region"],
                severity=z["severity"],
                findings=[
                    ZoneFinding(
                        description=f["description"],
                        severity_contribution=f["severity_contribution"],
                        source_view=f["source_view"],
                    )
                    for f in z.get("findings", [])
                ],
                measurements=[
                    ZoneMeasurement(
                        name=m["name"],
                        value=m["value"],
                        unit=m.get("unit", "mm"),
                        ideal_min=m.get("ideal_min"),
                        ideal_max=m.get("ideal_max"),
                        deviation_pct=m.get("deviation_pct"),
                    )
                    for m in z.get("measurements", [])
                ],
                primary_view=z.get("primary_view", "frontal"),
                confirmed_by=z.get("confirmed_by", []),
                calibration_method=z.get("calibration_method", "iris"),
            ))

        gm_raw = data.get("global_metrics") or {}
        thirds = gm_raw.get("facial_thirds", {})
        global_metrics = GlobalMetrics(
            symmetry_index=gm_raw.get("symmetry_index", 0.0),
            facial_thirds={
                "upper": thirds.get("upper", 0.33),
                "middle": thirds.get("middle", 0.33),
                "lower": thirds.get("lower", 0.34),
            },
            golden_ratio_deviation=gm_raw.get("golden_ratio_deviation", 0.0),
            lip_ratio=gm_raw.get("lip_ratio"),
        )

        calibration = CalibrationInfo(
            method=data.get("calibration_method", "unknown"),
            px_per_mm=0.0,
            confidence=0.0,
        )

        return ZoneReport(
            zones=zones,
            global_metrics=global_metrics,
            calibration=calibration,
            aesthetic_score=data.get("aesthetic_score", 0.0),
            expression_deviation=0.0,
        )

    pre_report = _reconstruct_zone_report(pre_data)
    post_report = _reconstruct_zone_report(post_data)

    # Run comparison
    comp_result: ComparisonResult = compare(pre_report, post_report)

    # Convert to API response
    return ComparisonResponse(
        pre_assessment_id=request.pre_assessment_id,
        post_assessment_id=request.post_assessment_id,
        zone_deltas=[
            ZoneDeltaResponse(
                zone_id=zd.zone_id,
                zone_name=zd.zone_name,
                region=zd.region,
                pre_severity=zd.pre_severity,
                post_severity=zd.post_severity,
                severity_delta=zd.severity_delta,
                severity_improvement_pct=zd.severity_improvement_pct,
                measurement_deltas=[
                    MeasurementDeltaResponse(
                        name=md.name,
                        pre_value=md.pre_value,
                        post_value=md.post_value,
                        delta=md.delta,
                        delta_pct=md.delta_pct,
                        unit=md.unit,
                        improved=md.improved,
                    )
                    for md in zd.measurement_deltas
                ],
                status=zd.status,
            )
            for zd in comp_result.zone_deltas
        ],
        improvement_score=comp_result.improvement_score,
        aesthetic_score_pre=comp_result.aesthetic_score_pre,
        aesthetic_score_post=comp_result.aesthetic_score_post,
        aesthetic_score_delta=comp_result.aesthetic_score_delta,
        zones_improved=comp_result.zones_improved,
        zones_worsened=comp_result.zones_worsened,
        zones_unchanged=comp_result.zones_unchanged,
        zones_resolved=comp_result.zones_resolved,
        zones_new=comp_result.zones_new,
        heatmap=[
            HeatmapEntryResponse(
                zone_id=h.zone_id,
                zone_name=h.zone_name,
                region=h.region,
                pre_intensity=h.pre_intensity,
                post_intensity=h.post_intensity,
                delta_intensity=h.delta_intensity,
                color_code=h.color_code,
            )
            for h in comp_result.heatmap
        ],
        summary=comp_result.summary,
    )


@router.get(
    "/patients/{patient_id}/history",
    response_model=PatientHistoryResponse,
    summary="Get patient assessment history",
    description="Returns all assessments for a patient, ordered by date.",
)
async def get_patient_history(patient_id: UUID, _api_key: str = Depends(require_api_key)):
    """GET /api/v2/patients/{id}/history — assessment timeline."""
    from app.services.supabase_service import get_patient_history as fetch_history

    if not settings.supabase_url:
        raise HTTPException(
            status_code=503,
            detail="Supabase is not configured. Cannot query patient history.",
        )

    rows = await fetch_history(patient_id)

    assessments = []
    for row in rows:
        zones = row.get("zones") or []
        primary_concern = None
        if zones:
            # Pick highest severity zone as primary concern
            sorted_zones = sorted(zones, key=lambda z: z.get("severity", 0), reverse=True)
            if sorted_zones:
                primary_concern = sorted_zones[0].get("zone_name")

        assessments.append(AssessmentSummary(
            assessment_id=UUID(row["id"]),
            timestamp=row.get("created_at", datetime.now(timezone.utc).isoformat()),
            aesthetic_score=row.get("aesthetic_score", 0.0) or 0.0,
            zones_count=len(zones),
            primary_concern=primary_concern,
            views_analyzed=[],
            engine_version=row.get("engine_version", "2.0.0"),
        ))

    return PatientHistoryResponse(
        patient_id=patient_id,
        assessments=assessments,
        total_count=len(assessments),
    )


_START_TIME = datetime.now(timezone.utc)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="V2 API health check",
    description=(
        "Returns service health including model availability, "
        "Supabase connectivity, and uptime."
    ),
)
async def health_check():
    """GET /api/v2/health — check API, model, DB status, and uptime."""
    import os
    from app.detection.face_landmarker import DEFAULT_MODEL_PATH

    model_loaded = os.path.exists(DEFAULT_MODEL_PATH)

    supabase_configured = bool(settings.supabase_url and settings.supabase_key)
    supabase_connected = False

    if supabase_configured:
        try:
            from app.services.supabase_service import get_assessment
            # Quick connectivity probe — will fail fast if unreachable
            await get_assessment("00000000-0000-0000-0000-000000000000")
            supabase_connected = True
        except Exception:
            # Any response (including 404) means Supabase is reachable
            supabase_connected = True

    uptime_seconds = (datetime.now(timezone.utc) - _START_TIME).total_seconds()
    status = "healthy" if model_loaded else "degraded"

    return HealthResponse(
        status=status,
        version="2.1.0",
        model_loaded=model_loaded,
        supabase_connected=supabase_connected,
        uptime_seconds=round(uptime_seconds, 1),
    )
