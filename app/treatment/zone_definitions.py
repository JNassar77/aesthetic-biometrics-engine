"""
Treatment zone definitions — the clinical backbone of the V2 engine.

Defines 16 anatomical treatment zones (inspired by MD Codes) with:
- Landmark mappings (which landmarks define the zone)
- Reference values (ideal ranges for measurements)
- View priorities (which camera angle is primary for each zone)
- Severity calculation parameters

Each zone maps to specific aesthetic medicine interventions
(fillers, neurotoxins, skin quality treatments).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Region(str, Enum):
    UPPER_FACE = "upper_face"
    MIDFACE = "midface"
    LOWER_FACE = "lower_face"
    PROFILE = "profile"


class ViewPriority(str, Enum):
    FRONTAL = "frontal"
    PROFILE = "profile"
    OBLIQUE = "oblique"


@dataclass(frozen=True)
class ReferenceRange:
    """Ideal measurement range for a zone metric."""
    metric_name: str
    ideal_min: float
    ideal_max: float
    unit: str = "mm"
    description: str = ""


@dataclass(frozen=True)
class ZoneDefinition:
    """Complete definition of one treatment zone."""
    zone_id: str
    zone_name: str
    region: Region
    primary_view: ViewPriority
    secondary_views: tuple[ViewPriority, ...] = ()
    needs_fusion: bool = False
    reference_ranges: tuple[ReferenceRange, ...] = ()
    severity_weights: dict[str, float] = field(default_factory=dict)
    description: str = ""


# ──────────────────────── ZONE REGISTRY ────────────────────────

ZONES: dict[str, ZoneDefinition] = {

    # ── UPPER FACE ──

    "T1": ZoneDefinition(
        zone_id="T1",
        zone_name="Temporal",
        region=Region.UPPER_FACE,
        primary_view=ViewPriority.OBLIQUE,
        description="Temporal fossa — hollowing indicates volume loss",
        reference_ranges=(
            ReferenceRange("temporal_depth_mm", -2.0, 2.0, "mm", "Depth relative to brow line"),
        ),
        severity_weights={"volume_deficit": 0.6, "asymmetry": 0.2, "aging": 0.2},
    ),

    "Bw1": ZoneDefinition(
        zone_id="Bw1",
        zone_name="Brow Lateral",
        region=Region.UPPER_FACE,
        primary_view=ViewPriority.FRONTAL,
        secondary_views=(ViewPriority.OBLIQUE,),
        needs_fusion=True,
        description="Lateral brow — ptosis indicates aging or neurotoxin need",
        reference_ranges=(
            ReferenceRange("brow_height_mm", 20.0, 25.0, "mm", "Brow peak height above orbital rim"),
            ReferenceRange("brow_asymmetry_mm", 0.0, 1.5, "mm", "Left-right height difference"),
        ),
        severity_weights={"measurement_deviation": 0.4, "asymmetry": 0.4, "aging": 0.2},
    ),

    "Bw2": ZoneDefinition(
        zone_id="Bw2",
        zone_name="Glabella",
        region=Region.UPPER_FACE,
        primary_view=ViewPriority.FRONTAL,
        description="Glabella complex — corrugator lines, '11' lines",
        reference_ranges=(
            ReferenceRange("glabellar_depth_mm", 0.0, 1.0, "mm", "Corrugator line depth at rest"),
        ),
        severity_weights={"measurement_deviation": 0.3, "aging": 0.4, "muscle_activity": 0.3},
    ),

    "Fo1": ZoneDefinition(
        zone_id="Fo1",
        zone_name="Forehead",
        region=Region.UPPER_FACE,
        primary_view=ViewPriority.FRONTAL,
        secondary_views=(ViewPriority.PROFILE,),
        description="Forehead — horizontal lines, frontalis activity",
        severity_weights={"aging": 0.5, "muscle_activity": 0.3, "measurement_deviation": 0.2},
    ),

    # ── MIDFACE ──

    "Ck1": ZoneDefinition(
        zone_id="Ck1",
        zone_name="Zygomatic Arch",
        region=Region.MIDFACE,
        primary_view=ViewPriority.OBLIQUE,
        secondary_views=(ViewPriority.FRONTAL,),
        needs_fusion=True,
        description="Zygomatic arch — skeletal framework of midface",
        reference_ranges=(
            ReferenceRange("bizygomatic_width_mm", 125.0, 145.0, "mm", "Full face width at cheekbones"),
        ),
        severity_weights={"measurement_deviation": 0.5, "asymmetry": 0.3, "volume_deficit": 0.2},
    ),

    "Ck2": ZoneDefinition(
        zone_id="Ck2",
        zone_name="Zygomatic Eminence",
        region=Region.MIDFACE,
        primary_view=ViewPriority.OBLIQUE,
        secondary_views=(ViewPriority.FRONTAL,),
        needs_fusion=True,
        description="Malar prominence — key for ogee curve and midface volume",
        reference_ranges=(
            ReferenceRange("ogee_curve_score", 70.0, 100.0, "score", "S-curve fluidity 0-100"),
            ReferenceRange("malar_prominence_ratio", 0.75, 1.0, "ratio", "Projection vs. face width"),
        ),
        severity_weights={"volume_deficit": 0.5, "measurement_deviation": 0.3, "asymmetry": 0.2},
    ),

    "Ck3": ZoneDefinition(
        zone_id="Ck3",
        zone_name="Anteromedial Cheek",
        region=Region.MIDFACE,
        primary_view=ViewPriority.OBLIQUE,
        secondary_views=(ViewPriority.FRONTAL,),
        needs_fusion=True,
        description="Midface soft tissue — volume loss leads to nasolabial deepening",
        severity_weights={"volume_deficit": 0.5, "aging": 0.3, "asymmetry": 0.2},
    ),

    "Tt1": ZoneDefinition(
        zone_id="Tt1",
        zone_name="Tear Trough",
        region=Region.MIDFACE,
        primary_view=ViewPriority.FRONTAL,
        secondary_views=(ViewPriority.OBLIQUE,),
        needs_fusion=True,
        description="Infraorbital hollow — tear trough deformity assessment",
        reference_ranges=(
            ReferenceRange("tear_trough_depth_mm", 0.0, 2.0, "mm", "Depth of infraorbital groove"),
        ),
        severity_weights={"volume_deficit": 0.5, "asymmetry": 0.3, "aging": 0.2},
    ),

    "Ns1": ZoneDefinition(
        zone_id="Ns1",
        zone_name="Nasolabial Fold",
        region=Region.MIDFACE,
        primary_view=ViewPriority.FRONTAL,
        secondary_views=(ViewPriority.OBLIQUE,),
        needs_fusion=True,
        description="Nasolabial crease — depth correlates with midface volume loss",
        reference_ranges=(
            ReferenceRange("nasolabial_depth_mm", 0.0, 3.0, "mm", "Fold depth at deepest point"),
            ReferenceRange("nasolabial_asymmetry_mm", 0.0, 1.5, "mm", "Left-right depth difference"),
        ),
        severity_weights={"volume_deficit": 0.4, "measurement_deviation": 0.3, "asymmetry": 0.3},
    ),

    # ── LOWER FACE ──

    "Lp1": ZoneDefinition(
        zone_id="Lp1",
        zone_name="Upper Lip",
        region=Region.LOWER_FACE,
        primary_view=ViewPriority.FRONTAL,
        secondary_views=(ViewPriority.PROFILE,),
        needs_fusion=True,
        description="Upper vermilion — volume, definition, cupid's bow",
        reference_ranges=(
            ReferenceRange("upper_lip_height_mm", 6.0, 9.0, "mm", "Vermilion height"),
            ReferenceRange("lip_ratio", 0.5, 0.7, "ratio", "Upper:lower lip ratio (ideal ~1:1.6)"),
            ReferenceRange("cupid_bow_asymmetry_pct", 0.0, 5.0, "%", "Cupid's bow left-right deviation"),
        ),
        severity_weights={"measurement_deviation": 0.5, "asymmetry": 0.3, "volume_deficit": 0.2},
    ),

    "Lp2": ZoneDefinition(
        zone_id="Lp2",
        zone_name="Lower Lip",
        region=Region.LOWER_FACE,
        primary_view=ViewPriority.FRONTAL,
        secondary_views=(ViewPriority.PROFILE,),
        needs_fusion=True,
        description="Lower vermilion — volume and proportion",
        reference_ranges=(
            ReferenceRange("lower_lip_height_mm", 9.0, 14.0, "mm", "Vermilion height"),
        ),
        severity_weights={"measurement_deviation": 0.5, "asymmetry": 0.2, "volume_deficit": 0.3},
    ),

    "Lp3": ZoneDefinition(
        zone_id="Lp3",
        zone_name="Lip Corners",
        region=Region.LOWER_FACE,
        primary_view=ViewPriority.FRONTAL,
        description="Oral commissures — downturn indicates aging/volume loss",
        reference_ranges=(
            ReferenceRange("mouth_corner_angle_deg", -2.0, 5.0, "deg", "Angle above horizontal (negative=downturn)"),
        ),
        severity_weights={"measurement_deviation": 0.4, "asymmetry": 0.3, "aging": 0.3},
    ),

    "Mn1": ZoneDefinition(
        zone_id="Mn1",
        zone_name="Marionette Lines",
        region=Region.LOWER_FACE,
        primary_view=ViewPriority.FRONTAL,
        secondary_views=(ViewPriority.OBLIQUE,),
        needs_fusion=True,
        description="Marionette folds — depth correlates with jowling and volume loss",
        severity_weights={"volume_deficit": 0.4, "aging": 0.4, "asymmetry": 0.2},
    ),

    "Jw1": ZoneDefinition(
        zone_id="Jw1",
        zone_name="Pre-Jowl Sulcus",
        region=Region.LOWER_FACE,
        primary_view=ViewPriority.FRONTAL,
        secondary_views=(ViewPriority.OBLIQUE,),
        needs_fusion=True,
        description="Pre-jowl depression — lateral to chin, contributes to jowl appearance",
        severity_weights={"volume_deficit": 0.5, "aging": 0.3, "asymmetry": 0.2},
    ),

    "Ch1": ZoneDefinition(
        zone_id="Ch1",
        zone_name="Chin",
        region=Region.LOWER_FACE,
        primary_view=ViewPriority.PROFILE,
        secondary_views=(ViewPriority.FRONTAL,),
        needs_fusion=True,
        description="Chin projection and shape — pogonion position relative to facial planes",
        reference_ranges=(
            ReferenceRange("chin_projection_mm", -4.0, 0.0, "mm", "Pogonion behind Ricketts E-line (negative=retruded)"),
        ),
        severity_weights={"measurement_deviation": 0.6, "asymmetry": 0.2, "volume_deficit": 0.2},
    ),

    "Jl1": ZoneDefinition(
        zone_id="Jl1",
        zone_name="Jawline",
        region=Region.LOWER_FACE,
        primary_view=ViewPriority.PROFILE,
        secondary_views=(ViewPriority.FRONTAL, ViewPriority.OBLIQUE),
        needs_fusion=True,
        description="Jawline contour — definition, gonial angle, and contour breaks",
        reference_ranges=(
            ReferenceRange("gonial_angle_deg", 110.0, 130.0, "deg", "Angle at mandibular angle"),
        ),
        severity_weights={"measurement_deviation": 0.4, "asymmetry": 0.3, "aging": 0.3},
    ),

    # ── PROFILE-SPECIFIC ──

    "Pf1": ZoneDefinition(
        zone_id="Pf1",
        zone_name="Nasal Profile",
        region=Region.PROFILE,
        primary_view=ViewPriority.PROFILE,
        description="Nasal dorsum — hump, saddle, tip projection",
        reference_ranges=(
            ReferenceRange("nasolabial_angle_deg", 90.0, 105.0, "deg", "Angle at columella-subnasale-lip junction"),
            ReferenceRange("nasofrontal_angle_deg", 115.0, 135.0, "deg", "Angle at glabella-nasion-dorsum"),
        ),
        severity_weights={"measurement_deviation": 0.7, "asymmetry": 0.1, "volume_deficit": 0.2},
    ),

    "Pf2": ZoneDefinition(
        zone_id="Pf2",
        zone_name="Lip Projection",
        region=Region.PROFILE,
        primary_view=ViewPriority.PROFILE,
        description="Lip projection relative to E-line and Steiner line",
        reference_ranges=(
            ReferenceRange("upper_lip_to_eline_mm", -4.0, -1.0, "mm", "Upper lip behind Ricketts E-line"),
            ReferenceRange("lower_lip_to_eline_mm", -2.0, 0.0, "mm", "Lower lip behind Ricketts E-line"),
        ),
        severity_weights={"measurement_deviation": 0.7, "volume_deficit": 0.3},
    ),

    "Pf3": ZoneDefinition(
        zone_id="Pf3",
        zone_name="Chin-Neck Angle",
        region=Region.PROFILE,
        primary_view=ViewPriority.PROFILE,
        description="Cervicomental angle — defines jawline-neck junction",
        reference_ranges=(
            ReferenceRange("cervicomental_angle_deg", 105.0, 120.0, "deg", "Angle at submentale-gnathion-neck tangent"),
        ),
        severity_weights={"measurement_deviation": 0.5, "aging": 0.3, "volume_deficit": 0.2},
    ),
}


def get_zone(zone_id: str) -> ZoneDefinition | None:
    return ZONES.get(zone_id)


def all_zone_ids() -> list[str]:
    return list(ZONES.keys())


def zones_for_view(view: str) -> list[ZoneDefinition]:
    """Return zones that use this view as primary or secondary."""
    vp = ViewPriority(view)
    return [
        z for z in ZONES.values()
        if z.primary_view == vp or vp in z.secondary_views
    ]


def zones_needing_fusion() -> list[ZoneDefinition]:
    """Return zones that benefit from multi-view fusion."""
    return [z for z in ZONES.values() if z.needs_fusion]


def zones_by_region(region: Region) -> list[ZoneDefinition]:
    return [z for z in ZONES.values() if z.region == region]
