"""
Pydantic models for zone-based analysis results.

These models represent the output of the analysis engines,
structured per treatment zone. Used in API responses and Supabase storage.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ZoneMeasurement(BaseModel):
    """A single measurement within a zone."""
    name: str
    value: float
    unit: str = "mm"
    ideal_min: float | None = None
    ideal_max: float | None = None
    deviation_pct: float | None = None  # % deviation from ideal range


class ZoneFinding(BaseModel):
    """A clinical finding for a zone."""
    description: str
    severity_contribution: float = Field(ge=0, le=10)
    source_view: str  # "frontal", "profile", "oblique"


class ZoneResult(BaseModel):
    """Complete analysis result for one treatment zone."""
    zone_id: str
    zone_name: str
    region: str  # "upper_face", "midface", "lower_face", "profile"
    severity: float = Field(ge=0, le=10)
    findings: list[ZoneFinding] = []
    measurements: list[ZoneMeasurement] = []
    primary_view: str
    confirmed_by: list[str] = []  # additional views that confirmed findings
    calibration_method: str = "iris"


class SymmetryResult(BaseModel):
    """Symmetry analysis for a paired zone or global measurement."""
    zone_id: str | None = None  # None for global symmetry
    metric_name: str
    left_value: float
    right_value: float
    difference_mm: float
    difference_pct: float
    is_significant: bool = False  # True if beyond clinical threshold


class ProportionResult(BaseModel):
    """Facial proportion measurement."""
    name: str
    measured_ratio: float
    ideal_ratio: float
    deviation_pct: float
    description: str = ""


class GlobalMetrics(BaseModel):
    """Global facial metrics across all zones."""
    symmetry_index: float = Field(ge=0, le=100)
    facial_thirds: dict[str, float]  # upper, middle, lower ratios
    facial_fifths: dict[str, float] | None = None  # horizontal fifths
    golden_ratio_deviation: float
    lip_ratio: float | None = None
    aesthetic_score: float = Field(ge=0, le=100)


class CalibrationInfo(BaseModel):
    """Calibration metadata for the analysis."""
    method: str  # "iris" or "face_width_estimate"
    px_per_mm: float
    confidence: float
    iris_width_px: float | None = None
    face_width_px: float | None = None
