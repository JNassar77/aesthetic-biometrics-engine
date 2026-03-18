from pydantic import BaseModel, Field
from enum import Enum


class ViewAngle(str, Enum):
    FRONTAL = "frontal"
    OBLIQUE = "oblique"
    PROFILE = "profile"


class AnalysisRequest(BaseModel):
    patient_id: str | None = None
    view_angle: ViewAngle
    image_url: str | None = Field(None, description="Supabase storage URL; alternative to file upload")


class SymmetryResult(BaseModel):
    horizontal_deviation_mm: float = Field(description="Horizontal offset from median sagittal line")
    vertical_deviation_mm: float = Field(description="Vertical offset between paired landmarks")
    symmetry_score: float = Field(ge=0, le=100, description="0=asymmetric, 100=perfect symmetry")


class FacialThirds(BaseModel):
    upper_third_ratio: float = Field(description="Trichion to Glabella proportion")
    middle_third_ratio: float = Field(description="Glabella to Subnasale proportion")
    lower_third_ratio: float = Field(description="Subnasale to Mentum proportion")
    deviation_from_ideal: float = Field(description="Deviation from equal 1:1:1 ratio (%)")


class LipAnalysis(BaseModel):
    upper_lip_height_px: float
    lower_lip_height_px: float
    ratio: float = Field(description="Upper:Lower lip ratio (ideal ~1:1.6)")
    deviation_from_ideal: float = Field(description="% deviation from 1:1.6 golden ratio")


class FrontalAnalysis(BaseModel):
    symmetry: SymmetryResult
    facial_thirds: FacialThirds
    lip_analysis: LipAnalysis


class ProfileELine(BaseModel):
    upper_lip_to_eline_mm: float = Field(description="Distance from upper lip to Ricketts E-line")
    lower_lip_to_eline_mm: float = Field(description="Distance from lower lip to Ricketts E-line")
    assessment: str = Field(description="retruded / ideal / protruded")


class NasolabialAngle(BaseModel):
    angle_degrees: float
    ideal_min: float = 90.0
    ideal_max: float = 105.0
    assessment: str


class ChinProjection(BaseModel):
    pogonion_offset_mm: float = Field(description="Pogonion position relative to vertical reference")
    assessment: str


class ProfileAnalysis(BaseModel):
    e_line: ProfileELine
    nasolabial_angle: NasolabialAngle
    chin_projection: ChinProjection


class OgeeCurve(BaseModel):
    curve_score: float = Field(ge=0, le=100, description="0=flat/volume loss, 100=ideal ogee")
    midface_volume_assessment: str = Field(description="adequate / moderate_loss / significant_loss")
    malar_prominence_ratio: float


class ObliqueAnalysis(BaseModel):
    ogee_curve: OgeeCurve


class QualityWarning(BaseModel):
    code: str
    message: str


class AnalysisResponse(BaseModel):
    patient_id: str | None = None
    view_angle: ViewAngle
    analysis: FrontalAnalysis | ProfileAnalysis | ObliqueAnalysis
    quality_warnings: list[QualityWarning] = []
    landmarks_detected: int
    confidence: float = Field(ge=0, le=1)
    metadata: dict = Field(default_factory=dict)
