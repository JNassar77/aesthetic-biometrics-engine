"""
Pydantic V2 API schemas for the Aesthetic Biometrics Engine.

These models define the request/response contracts for the V2 API.
Internal dataclasses (ZoneReport, TreatmentPlan, ComparisonResult) are
converted to these serializable Pydantic models at the API boundary.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ──────────────────────── Image Quality ────────────────────────

class ImageQualityResponse(BaseModel):
    """Quality assessment for one uploaded image."""
    accepted: bool
    warnings: list[QualityWarningResponse] = []
    confidence: float = Field(ge=0, le=1)


class QualityWarningResponse(BaseModel):
    """A single quality warning."""
    code: str
    message: str
    severity: str = "low"  # low, medium, high, critical


# ──────────────────────── Calibration ────────────────────────

class CalibrationResponse(BaseModel):
    """Calibration metadata."""
    method: str  # "iris" or "face_width_estimate"
    px_per_mm: float
    confidence: float = Field(ge=0, le=1)


# ──────────────────────── Global Metrics ────────────────────────

class HeadPoseResponse(BaseModel):
    """Head pose angles from transformation matrix."""
    yaw: float
    pitch: float
    roll: float


class FacialThirdsResponse(BaseModel):
    """Facial thirds proportions."""
    upper: float
    middle: float
    lower: float


class GlobalMetricsResponse(BaseModel):
    """Global facial metrics across all zones."""
    symmetry_index: float = Field(ge=0, le=100)
    facial_thirds: FacialThirdsResponse
    golden_ratio_deviation: float
    lip_ratio: float | None = None
    head_pose: HeadPoseResponse | None = None


# ──────────────────────── Zone Analysis ────────────────────────

class ZoneMeasurementResponse(BaseModel):
    """A single measurement within a zone."""
    name: str
    value: float
    unit: str = "mm"
    ideal_min: float | None = None
    ideal_max: float | None = None
    deviation_pct: float | None = None


class ZoneFindingResponse(BaseModel):
    """A clinical finding for a zone."""
    description: str
    severity_contribution: float = Field(ge=0, le=10)
    source_view: str


class ZoneResultResponse(BaseModel):
    """Complete analysis result for one treatment zone."""
    zone_id: str
    zone_name: str
    region: str
    severity: float = Field(ge=0, le=10)
    findings: list[ZoneFindingResponse] = []
    measurements: list[ZoneMeasurementResponse] = []
    primary_view: str
    confirmed_by: list[str] = []
    calibration_method: str = "iris"


# ──────────────────────── Treatment Plan ────────────────────────

class ProductRecommendationResponse(BaseModel):
    """A specific product recommendation."""
    products: list[str]
    category: str
    techniques: list[str]
    depth: str
    volume_range_ml: list[float]  # [min, max]
    description: str
    safety_notes: list[str] = []


class NeurotoxinRecommendationResponse(BaseModel):
    """Neurotoxin recommendation for a zone."""
    target_muscle: str
    products: list[str]
    dose_range_units: list[int]  # [min, max]
    safety_notes: list[str] = []


class TreatmentConcernResponse(BaseModel):
    """A single treatment concern."""
    priority: int
    zone_id: str
    zone_name: str
    severity: float
    concern: str
    filler_recommendations: list[ProductRecommendationResponse] = []
    neurotoxin_recommendations: list[NeurotoxinRecommendationResponse] = []
    is_high_risk: bool = False
    vascular_risk: list[str] = []
    session: int = 1


class ContraindicationResponse(BaseModel):
    """A contraindication or safety warning."""
    severity: str  # WARNING, CAUTION, REFERRAL, CONTRAINDICATED
    zone_id: str | None = None
    code: str
    message: str
    recommendation: str


class SessionPlanResponse(BaseModel):
    """Treatment session plan."""
    session_number: int
    concerns: list[TreatmentConcernResponse]
    total_filler_volume_ml: list[float]  # [min, max]
    total_neurotoxin_units: list[int]    # [min, max]
    focus: str


class TreatmentPlanResponse(BaseModel):
    """Complete treatment plan."""
    primary_concerns: list[TreatmentConcernResponse] = []
    secondary_concerns: list[TreatmentConcernResponse] = []
    contraindications: list[ContraindicationResponse] = []
    sessions: list[SessionPlanResponse] = []
    total_volume_estimate_ml: list[float] = [0.0, 0.0]  # [min, max]
    total_neurotoxin_units: list[int] = [0, 0]           # [min, max]
    session_count: int = 1


# ──────────────────────── Complete Assessment Response ────────────────────────

class AssessmentResponse(BaseModel):
    """Complete V2 assessment response — the main API output."""
    assessment_id: UUID = Field(default_factory=uuid4)
    patient_id: UUID | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Quality per image
    image_quality: dict[str, ImageQualityResponse]  # frontal, profile, oblique

    # Global metrics
    global_metrics: GlobalMetricsResponse

    # Zone-based analysis
    zones: list[ZoneResultResponse]
    aesthetic_score: float = Field(ge=0, le=100)

    # Treatment plan
    treatment_plan: TreatmentPlanResponse

    # Calibration info
    calibration: CalibrationResponse

    # Metadata
    engine_version: str = "2.1.0"
    processing_time_ms: int | None = None
    views_analyzed: list[str] = []

    model_config = {"json_schema_extra": {
        "example": {
            "assessment_id": "550e8400-e29b-41d4-a716-446655440000",
            "patient_id": None,
            "engine_version": "2.1.0",
        }
    }}


# ──────────────────────── Comparison ────────────────────────

class MeasurementDeltaResponse(BaseModel):
    """Change in a single measurement."""
    name: str
    pre_value: float
    post_value: float
    delta: float
    delta_pct: float
    unit: str
    improved: bool


class ZoneDeltaResponse(BaseModel):
    """Change in one zone between pre and post."""
    zone_id: str
    zone_name: str
    region: str
    pre_severity: float
    post_severity: float
    severity_delta: float
    severity_improvement_pct: float
    measurement_deltas: list[MeasurementDeltaResponse] = []
    status: str = "unchanged"


class HeatmapEntryResponse(BaseModel):
    """Visualization data for one zone."""
    zone_id: str
    zone_name: str
    region: str
    pre_intensity: float
    post_intensity: float
    delta_intensity: float
    color_code: str


class ComparisonResponse(BaseModel):
    """Before/After comparison result."""
    comparison_id: UUID = Field(default_factory=uuid4)
    pre_assessment_id: UUID
    post_assessment_id: UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    zone_deltas: list[ZoneDeltaResponse]
    improvement_score: float = Field(ge=0, le=100)
    aesthetic_score_pre: float
    aesthetic_score_post: float
    aesthetic_score_delta: float

    zones_improved: int = 0
    zones_worsened: int = 0
    zones_unchanged: int = 0
    zones_resolved: int = 0
    zones_new: int = 0

    heatmap: list[HeatmapEntryResponse] = []
    summary: str = ""


# ──────────────────────── Compare Request ────────────────────────

class CompareRequest(BaseModel):
    """Request body for the comparison endpoint."""
    pre_assessment_id: UUID
    post_assessment_id: UUID
    treatment_date: str | None = None
    treatment_notes: str | None = None


# ──────────────────────── Patient History ────────────────────────

class AssessmentSummary(BaseModel):
    """Lightweight assessment summary for history listing."""
    assessment_id: UUID
    timestamp: datetime
    aesthetic_score: float
    zones_count: int
    primary_concern: str | None = None
    views_analyzed: list[str] = []
    engine_version: str = "2.1.0"


class PatientHistoryResponse(BaseModel):
    """Patient assessment history."""
    patient_id: UUID
    assessments: list[AssessmentSummary] = []
    total_count: int = 0


# ──────────────────────── Health ────────────────────────

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "2.1.0"
    model_loaded: bool = False
    supabase_connected: bool = False
    uptime_seconds: float | None = None


# Forward reference update for ImageQualityResponse
ImageQualityResponse.model_rebuild()
