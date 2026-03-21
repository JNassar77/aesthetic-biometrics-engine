"""
Product database — clinical knowledge base for aesthetic medicine products.

Contains structured data for:
- Hyaluronic acid (HA) fillers: rheology (G'), viscosity, indications
- Non-HA fillers: CaHA (Radiesse), PLLA (Sculptra)
- Neurotoxins: Botox, Dysport, Xeomin
- Skin quality boosters: Profhilo, Volite

Each product includes zone compatibility, technique recommendations,
volume estimates, and safety considerations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ProductCategory(str, Enum):
    HA_DEEP = "ha_deep"            # High G', deep plane volume
    HA_MEDIUM = "ha_medium"        # Mid G', contouring/support
    HA_SOFT = "ha_soft"            # Low G', lips and fine lines
    NON_HA_VOLUMIZER = "non_ha"    # CaHA, PLLA — biostimulators
    NEUROTOXIN = "neurotoxin"      # BoNT-A
    SKIN_BOOSTER = "skin_booster"  # Hydration, skin quality


class InjectionTechnique(str, Enum):
    BOLUS = "bolus"
    LINEAR_THREADING = "linear_threading"
    SERIAL_PUNCTURE = "serial_puncture"
    FAN = "fan"
    FERN = "fern"
    MICRODROPLET = "microdroplet"
    BAP = "bap"  # Bio-Aesthetic Points
    MESOTHERAPY = "mesotherapy"
    INTRADERMAL = "intradermal"


class InjectionDepth(str, Enum):
    SUPRAPERIOSTEAL = "supraperiosteal"   # On bone
    DEEP_SUBCUTANEOUS = "deep_subcutaneous"
    SUBCUTANEOUS = "subcutaneous"
    SUBDERMAL = "subdermal"
    INTRADERMAL = "intradermal"
    INTRAMUSCULAR = "intramuscular"


@dataclass(frozen=True)
class ProductProfile:
    """Complete profile for one aesthetic medicine product."""
    name: str
    brand: str
    category: ProductCategory
    g_prime: float | None = None          # Elastic modulus (Pa), higher = stiffer
    viscosity: str = ""                    # Qualitative: low/medium/high
    duration_months: tuple[int, int] = (0, 0)  # Range of expected duration
    compatible_zones: tuple[str, ...] = ()
    preferred_techniques: tuple[InjectionTechnique, ...] = ()
    preferred_depth: InjectionDepth | None = None
    description: str = ""


@dataclass(frozen=True)
class ZoneProductRecommendation:
    """Recommendation for treating a specific zone."""
    zone_id: str
    category: ProductCategory
    products: tuple[str, ...]
    techniques: tuple[InjectionTechnique, ...]
    depth: InjectionDepth
    volume_range_ml: tuple[float, float]  # Min, max per side
    description: str = ""
    safety_notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class NeurotoxinIndication:
    """Neurotoxin indication for a specific zone/muscle."""
    zone_id: str
    target_muscle: str
    products: tuple[str, ...]
    dose_range_units: tuple[int, int]  # Min, max units (Botox-equivalent)
    description: str = ""
    safety_notes: tuple[str, ...] = ()


# ──────────────────────── PRODUCT CATALOG ────────────────────────

PRODUCTS: dict[str, ProductProfile] = {

    # ── HA Deep (High G') ──

    "juvederm_voluma": ProductProfile(
        name="Juvederm Voluma",
        brand="Allergan",
        category=ProductCategory.HA_DEEP,
        g_prime=274.0,
        viscosity="high",
        duration_months=(12, 18),
        compatible_zones=("Ck1", "Ck2", "Ch1", "Jl1"),
        preferred_techniques=(InjectionTechnique.BOLUS, InjectionTechnique.LINEAR_THREADING),
        preferred_depth=InjectionDepth.SUPRAPERIOSTEAL,
        description="High-projection HA filler for deep midface volumization and chin augmentation",
    ),

    "juvederm_volux": ProductProfile(
        name="Juvederm Volux",
        brand="Allergan",
        category=ProductCategory.HA_DEEP,
        g_prime=350.0,
        viscosity="very_high",
        duration_months=(12, 24),
        compatible_zones=("Ch1", "Jl1"),
        preferred_techniques=(InjectionTechnique.BOLUS, InjectionTechnique.LINEAR_THREADING),
        preferred_depth=InjectionDepth.SUPRAPERIOSTEAL,
        description="Highest G' HA filler for jawline definition and chin projection",
    ),

    # ── HA Medium ──

    "juvederm_vollure": ProductProfile(
        name="Juvederm Vollure",
        brand="Allergan",
        category=ProductCategory.HA_MEDIUM,
        g_prime=178.0,
        viscosity="medium",
        duration_months=(12, 18),
        compatible_zones=("Ns1", "Mn1", "Jw1", "Ck3"),
        preferred_techniques=(InjectionTechnique.LINEAR_THREADING, InjectionTechnique.FAN),
        preferred_depth=InjectionDepth.DEEP_SUBCUTANEOUS,
        description="Medium-lift HA filler for nasolabial folds and marionette lines",
    ),

    "restylane_lyft": ProductProfile(
        name="Restylane Lyft",
        brand="Galderma",
        category=ProductCategory.HA_MEDIUM,
        g_prime=225.0,
        viscosity="medium_high",
        duration_months=(9, 12),
        compatible_zones=("Ck1", "Ck2", "Ck3", "Ch1"),
        preferred_techniques=(InjectionTechnique.BOLUS, InjectionTechnique.LINEAR_THREADING),
        preferred_depth=InjectionDepth.SUPRAPERIOSTEAL,
        description="Midface volume restoration and cheek augmentation",
    ),

    # ── HA Soft (Low G') ──

    "juvederm_volbella": ProductProfile(
        name="Juvederm Volbella",
        brand="Allergan",
        category=ProductCategory.HA_SOFT,
        g_prime=98.0,
        viscosity="low",
        duration_months=(9, 12),
        compatible_zones=("Lp1", "Lp2", "Lp3", "Tt1"),
        preferred_techniques=(InjectionTechnique.SERIAL_PUNCTURE, InjectionTechnique.MICRODROPLET),
        preferred_depth=InjectionDepth.SUBDERMAL,
        description="Soft HA filler for lip augmentation and perioral rejuvenation",
    ),

    "restylane_kysse": ProductProfile(
        name="Restylane Kysse",
        brand="Galderma",
        category=ProductCategory.HA_SOFT,
        g_prime=125.0,
        viscosity="medium_low",
        duration_months=(9, 12),
        compatible_zones=("Lp1", "Lp2"),
        preferred_techniques=(InjectionTechnique.SERIAL_PUNCTURE, InjectionTechnique.LINEAR_THREADING),
        preferred_depth=InjectionDepth.SUBDERMAL,
        description="Dynamic lip filler with natural movement preservation",
    ),

    "teoxane_kiss": ProductProfile(
        name="Teoxane RHA Kiss",
        brand="Teoxane",
        category=ProductCategory.HA_SOFT,
        g_prime=110.0,
        viscosity="medium_low",
        duration_months=(9, 12),
        compatible_zones=("Lp1", "Lp2"),
        preferred_techniques=(InjectionTechnique.SERIAL_PUNCTURE, InjectionTechnique.LINEAR_THREADING),
        preferred_depth=InjectionDepth.SUBDERMAL,
        description="RHA-crosslinked lip filler for natural results",
    ),

    # ── Non-HA Volumizers ──

    "radiesse": ProductProfile(
        name="Radiesse",
        brand="Merz",
        category=ProductCategory.NON_HA_VOLUMIZER,
        g_prime=350.0,
        viscosity="high",
        duration_months=(12, 18),
        compatible_zones=("Ck1", "Ck2", "Ch1", "Jl1", "Jw1"),
        preferred_techniques=(InjectionTechnique.BOLUS, InjectionTechnique.LINEAR_THREADING),
        preferred_depth=InjectionDepth.SUPRAPERIOSTEAL,
        description="CaHA filler for deep volumization + collagen stimulation",
    ),

    "sculptra": ProductProfile(
        name="Sculptra",
        brand="Galderma",
        category=ProductCategory.NON_HA_VOLUMIZER,
        duration_months=(18, 24),
        compatible_zones=("T1", "Ck2", "Ck3"),
        preferred_techniques=(InjectionTechnique.FAN, InjectionTechnique.LINEAR_THREADING),
        preferred_depth=InjectionDepth.DEEP_SUBCUTANEOUS,
        description="PLLA biostimulator for progressive volume restoration",
    ),

    # ── Neurotoxins ──

    "botox": ProductProfile(
        name="Botox",
        brand="Allergan",
        category=ProductCategory.NEUROTOXIN,
        duration_months=(3, 5),
        compatible_zones=("Bw2", "Fo1"),
        preferred_depth=InjectionDepth.INTRAMUSCULAR,
        description="OnabotulinumtoxinA — gold standard neurotoxin",
    ),

    "dysport": ProductProfile(
        name="Dysport",
        brand="Galderma",
        category=ProductCategory.NEUROTOXIN,
        duration_months=(3, 5),
        compatible_zones=("Bw2", "Fo1"),
        preferred_depth=InjectionDepth.INTRAMUSCULAR,
        description="AbobotulinumtoxinA — higher diffusion radius",
    ),

    "xeomin": ProductProfile(
        name="Xeomin",
        brand="Merz",
        category=ProductCategory.NEUROTOXIN,
        duration_months=(3, 5),
        compatible_zones=("Bw2", "Fo1"),
        preferred_depth=InjectionDepth.INTRAMUSCULAR,
        description="IncobotulinumtoxinA — pure neurotoxin without complexing proteins",
    ),

    # ── Skin Boosters ──

    "profhilo": ProductProfile(
        name="Profhilo",
        brand="IBSA",
        category=ProductCategory.SKIN_BOOSTER,
        duration_months=(4, 6),
        compatible_zones=("Ck3", "T1"),
        preferred_techniques=(InjectionTechnique.BAP,),
        preferred_depth=InjectionDepth.SUBCUTANEOUS,
        description="High-concentration HA bioremodeler (32+32mg) — BAP technique",
    ),

    "juvederm_volite": ProductProfile(
        name="Juvederm Volite",
        brand="Allergan",
        category=ProductCategory.SKIN_BOOSTER,
        duration_months=(6, 9),
        compatible_zones=("Ck3", "T1"),
        preferred_techniques=(InjectionTechnique.MESOTHERAPY, InjectionTechnique.INTRADERMAL),
        preferred_depth=InjectionDepth.INTRADERMAL,
        description="Microdose HA for skin hydration and quality improvement",
    ),
}


# ──────────────────────── ZONE → PRODUCT MAPPING ────────────────────────

ZONE_RECOMMENDATIONS: dict[str, list[ZoneProductRecommendation]] = {

    # ── UPPER FACE ──

    "T1": [
        ZoneProductRecommendation(
            zone_id="T1",
            category=ProductCategory.NON_HA_VOLUMIZER,
            products=("Sculptra", "Radiesse"),
            techniques=(InjectionTechnique.FAN, InjectionTechnique.LINEAR_THREADING),
            depth=InjectionDepth.DEEP_SUBCUTANEOUS,
            volume_range_ml=(0.5, 1.5),
            description="Temporal hollowing — biostimulator preferred for gradual restoration",
            safety_notes=("Superficial temporal artery — aspirate before injection",),
        ),
        ZoneProductRecommendation(
            zone_id="T1",
            category=ProductCategory.SKIN_BOOSTER,
            products=("Profhilo", "Juvederm Volite"),
            techniques=(InjectionTechnique.BAP,),
            depth=InjectionDepth.SUBCUTANEOUS,
            volume_range_ml=(0.3, 0.5),
            description="Skin quality improvement in temporal area",
        ),
    ],

    "Bw1": [
        ZoneProductRecommendation(
            zone_id="Bw1",
            category=ProductCategory.HA_DEEP,
            products=("Juvederm Voluma", "Restylane Lyft"),
            techniques=(InjectionTechnique.BOLUS,),
            depth=InjectionDepth.SUPRAPERIOSTEAL,
            volume_range_ml=(0.1, 0.3),
            description="Lateral brow lift via deep plane volumization",
            safety_notes=("Supraorbital artery — inject deep, on bone",),
        ),
    ],

    # ── MIDFACE ──

    "Ck1": [
        ZoneProductRecommendation(
            zone_id="Ck1",
            category=ProductCategory.HA_DEEP,
            products=("Juvederm Voluma", "Restylane Lyft", "Radiesse"),
            techniques=(InjectionTechnique.BOLUS,),
            depth=InjectionDepth.SUPRAPERIOSTEAL,
            volume_range_ml=(0.3, 0.8),
            description="Zygomatic arch augmentation — skeletal framework support",
            safety_notes=("Zygomaticofacial artery — supraperiosteal injection safest",),
        ),
    ],

    "Ck2": [
        ZoneProductRecommendation(
            zone_id="Ck2",
            category=ProductCategory.HA_DEEP,
            products=("Juvederm Voluma", "Restylane Lyft", "Radiesse"),
            techniques=(InjectionTechnique.BOLUS, InjectionTechnique.LINEAR_THREADING),
            depth=InjectionDepth.SUPRAPERIOSTEAL,
            volume_range_ml=(0.5, 1.5),
            description="Malar eminence — key for ogee curve restoration",
            safety_notes=("Infraorbital artery — stay lateral and deep",),
        ),
    ],

    "Ck3": [
        ZoneProductRecommendation(
            zone_id="Ck3",
            category=ProductCategory.HA_MEDIUM,
            products=("Juvederm Vollure", "Restylane Lyft"),
            techniques=(InjectionTechnique.FAN, InjectionTechnique.LINEAR_THREADING),
            depth=InjectionDepth.DEEP_SUBCUTANEOUS,
            volume_range_ml=(0.5, 1.0),
            description="Anteromedial cheek volume restoration",
        ),
        ZoneProductRecommendation(
            zone_id="Ck3",
            category=ProductCategory.SKIN_BOOSTER,
            products=("Profhilo",),
            techniques=(InjectionTechnique.BAP,),
            depth=InjectionDepth.SUBCUTANEOUS,
            volume_range_ml=(0.5, 1.0),
            description="Skin quality and hydration improvement",
        ),
    ],

    "Tt1": [
        ZoneProductRecommendation(
            zone_id="Tt1",
            category=ProductCategory.HA_SOFT,
            products=("Juvederm Volbella",),
            techniques=(InjectionTechnique.MICRODROPLET, InjectionTechnique.LINEAR_THREADING),
            depth=InjectionDepth.SUBDERMAL,
            volume_range_ml=(0.1, 0.3),
            description="Tear trough correction — requires conservative approach",
            safety_notes=(
                "HIGH-RISK ZONE: Angular artery — use blunt cannula preferred",
                "Start conservatively (0.1ml per side), reassess at 2 weeks",
                "Risk of Tyndall effect with superficial placement",
            ),
        ),
    ],

    "Ns1": [
        ZoneProductRecommendation(
            zone_id="Ns1",
            category=ProductCategory.HA_MEDIUM,
            products=("Juvederm Vollure",),
            techniques=(InjectionTechnique.LINEAR_THREADING, InjectionTechnique.FAN),
            depth=InjectionDepth.DEEP_SUBCUTANEOUS,
            volume_range_ml=(0.3, 0.8),
            description="Nasolabial fold softening — address midface volume first",
            safety_notes=("Facial artery — aspirate, use blunt cannula if available",),
        ),
    ],

    # ── LOWER FACE ──

    "Lp1": [
        ZoneProductRecommendation(
            zone_id="Lp1",
            category=ProductCategory.HA_SOFT,
            products=("Juvederm Volbella", "Restylane Kysse", "Teoxane RHA Kiss"),
            techniques=(InjectionTechnique.SERIAL_PUNCTURE, InjectionTechnique.MICRODROPLET),
            depth=InjectionDepth.SUBDERMAL,
            volume_range_ml=(0.3, 0.8),
            description="Upper lip augmentation — vermilion border definition + body volume",
            safety_notes=("Superior labial artery — inject slowly, aspirate",),
        ),
    ],

    "Lp2": [
        ZoneProductRecommendation(
            zone_id="Lp2",
            category=ProductCategory.HA_SOFT,
            products=("Juvederm Volbella", "Restylane Kysse"),
            techniques=(InjectionTechnique.SERIAL_PUNCTURE, InjectionTechnique.MICRODROPLET),
            depth=InjectionDepth.SUBDERMAL,
            volume_range_ml=(0.2, 0.5),
            description="Lower lip enhancement — usually needs less than upper lip",
            safety_notes=("Inferior labial artery — same caution as upper lip",),
        ),
    ],

    "Lp3": [
        ZoneProductRecommendation(
            zone_id="Lp3",
            category=ProductCategory.HA_SOFT,
            products=("Juvederm Volbella",),
            techniques=(InjectionTechnique.MICRODROPLET,),
            depth=InjectionDepth.SUBDERMAL,
            volume_range_ml=(0.05, 0.15),
            description="Oral commissure elevation — small volumes, precise placement",
        ),
    ],

    "Mn1": [
        ZoneProductRecommendation(
            zone_id="Mn1",
            category=ProductCategory.HA_MEDIUM,
            products=("Juvederm Vollure",),
            techniques=(InjectionTechnique.LINEAR_THREADING, InjectionTechnique.FAN),
            depth=InjectionDepth.DEEP_SUBCUTANEOUS,
            volume_range_ml=(0.3, 0.8),
            description="Marionette line softening — address jowl/jawline first",
            safety_notes=("Facial artery — lateral to the fold",),
        ),
    ],

    "Jw1": [
        ZoneProductRecommendation(
            zone_id="Jw1",
            category=ProductCategory.HA_DEEP,
            products=("Juvederm Voluma", "Radiesse"),
            techniques=(InjectionTechnique.BOLUS,),
            depth=InjectionDepth.SUPRAPERIOSTEAL,
            volume_range_ml=(0.3, 0.5),
            description="Pre-jowl sulcus fill — deep plane for structural support",
        ),
    ],

    "Ch1": [
        ZoneProductRecommendation(
            zone_id="Ch1",
            category=ProductCategory.HA_DEEP,
            products=("Juvederm Volux", "Juvederm Voluma", "Radiesse"),
            techniques=(InjectionTechnique.BOLUS, InjectionTechnique.LINEAR_THREADING),
            depth=InjectionDepth.SUPRAPERIOSTEAL,
            volume_range_ml=(0.5, 1.5),
            description="Chin projection and shaping — supraperiosteal bolus",
            safety_notes=("Mental nerve — avoid lateral mental foramen area",),
        ),
    ],

    "Jl1": [
        ZoneProductRecommendation(
            zone_id="Jl1",
            category=ProductCategory.HA_DEEP,
            products=("Juvederm Volux", "Juvederm Voluma", "Radiesse"),
            techniques=(InjectionTechnique.LINEAR_THREADING, InjectionTechnique.BOLUS),
            depth=InjectionDepth.SUPRAPERIOSTEAL,
            volume_range_ml=(0.5, 1.5),
            description="Jawline definition — linear threading along mandibular border",
            safety_notes=("Facial artery at mandibular notch — palpate before injection",),
        ),
    ],

    # ── PROFILE-SPECIFIC ──

    "Pf1": [
        ZoneProductRecommendation(
            zone_id="Pf1",
            category=ProductCategory.HA_MEDIUM,
            products=("Juvederm Vollure",),
            techniques=(InjectionTechnique.LINEAR_THREADING,),
            depth=InjectionDepth.SUBDERMAL,
            volume_range_ml=(0.1, 0.5),
            description="Nasal profile refinement — non-surgical rhinoplasty",
            safety_notes=(
                "HIGH-RISK ZONE: Dorsal nasal artery — inject slowly, use blunt cannula",
                "Risk of skin necrosis and visual impairment with vascular compromise",
            ),
        ),
    ],

    "Pf2": [
        ZoneProductRecommendation(
            zone_id="Pf2",
            category=ProductCategory.HA_SOFT,
            products=("Juvederm Volbella", "Restylane Kysse"),
            techniques=(InjectionTechnique.SERIAL_PUNCTURE,),
            depth=InjectionDepth.SUBDERMAL,
            volume_range_ml=(0.3, 0.8),
            description="Lip projection enhancement — vermilion augmentation",
        ),
    ],

    "Pf3": [
        ZoneProductRecommendation(
            zone_id="Pf3",
            category=ProductCategory.HA_DEEP,
            products=("Juvederm Volux", "Radiesse"),
            techniques=(InjectionTechnique.BOLUS,),
            depth=InjectionDepth.SUPRAPERIOSTEAL,
            volume_range_ml=(0.3, 1.0),
            description="Submental contouring — chin-neck angle improvement",
        ),
    ],
}


# ──────────────────────── NEUROTOXIN INDICATIONS ────────────────────────

NEUROTOXIN_INDICATIONS: dict[str, list[NeurotoxinIndication]] = {

    "Bw2": [
        NeurotoxinIndication(
            zone_id="Bw2",
            target_muscle="Corrugator supercilii",
            products=("Botox", "Dysport", "Xeomin"),
            dose_range_units=(10, 25),
            description="Glabella complex — '11 lines' treatment",
            safety_notes=("Risk of brow ptosis if injected too low",),
        ),
        NeurotoxinIndication(
            zone_id="Bw2",
            target_muscle="Procerus",
            products=("Botox", "Dysport", "Xeomin"),
            dose_range_units=(5, 10),
            description="Horizontal glabellar lines",
        ),
    ],

    "Fo1": [
        NeurotoxinIndication(
            zone_id="Fo1",
            target_muscle="Frontalis",
            products=("Botox", "Dysport", "Xeomin"),
            dose_range_units=(10, 30),
            description="Forehead horizontal lines",
            safety_notes=(
                "Always treat glabella first to prevent compensatory brow ptosis",
                "Use lower doses in patients with low brow position",
            ),
        ),
    ],

    "Lp1": [
        NeurotoxinIndication(
            zone_id="Lp1",
            target_muscle="Orbicularis oris",
            products=("Botox",),
            dose_range_units=(2, 6),
            description="Lip flip — subtle upper lip eversion",
            safety_notes=("Very low doses — risk of incompetent lip seal",),
        ),
    ],
}


# ──────────────────────── HIGH-RISK VASCULAR ZONES ────────────────────────

VASCULAR_RISK_ZONES: dict[str, tuple[str, ...]] = {
    "Tt1": ("Angular artery", "Infraorbital artery"),
    "Ns1": ("Facial artery",),
    "Pf1": ("Dorsal nasal artery", "Angular artery"),
    "Lp1": ("Superior labial artery",),
    "Lp2": ("Inferior labial artery",),
    "Jl1": ("Facial artery at mandibular notch",),
    "T1": ("Superficial temporal artery",),
    "Bw1": ("Supraorbital artery",),
}


# ──────────────────────── CLINICAL ORDERING ────────────────────────

# Structural priority: zones that should be treated first because
# they provide the foundation for other treatments.
# Lower number = treat first.
STRUCTURAL_PRIORITY: dict[str, int] = {
    # Structural framework (treat first)
    "Ck1": 1,   # Zygomatic arch — skeletal base
    "Ck2": 1,   # Malar eminence — midface foundation
    "Ch1": 1,   # Chin — lower face anchor
    "Jl1": 2,   # Jawline — structural contour
    "Jw1": 2,   # Pre-jowl — structural support

    # Volume restoration (treat second)
    "T1": 3,    # Temporal — upper frame
    "Ck3": 3,   # Anteromedial cheek — midface fill
    "Tt1": 3,   # Tear trough — midface support

    # Fold/line softening (treat third — often resolved by volume above)
    "Ns1": 4,   # Nasolabial — often improves with midface volume
    "Mn1": 4,   # Marionette — often improves with jawline treatment
    "Bw1": 4,   # Brow — responds to temple/forehead treatment

    # Detail/refinement (treat last)
    "Lp1": 5,   # Upper lip
    "Lp2": 5,   # Lower lip
    "Lp3": 5,   # Lip corners
    "Fo1": 5,   # Forehead (neurotoxin)
    "Bw2": 5,   # Glabella (neurotoxin)

    # Profile (independent — can parallel structural)
    "Pf1": 3,   # Nasal profile
    "Pf2": 5,   # Lip projection
    "Pf3": 2,   # Chin-neck angle
}


# ──────────────────────── PUBLIC API ────────────────────────

def get_product(product_key: str) -> ProductProfile | None:
    return PRODUCTS.get(product_key)


def get_zone_recommendations(zone_id: str) -> list[ZoneProductRecommendation]:
    return ZONE_RECOMMENDATIONS.get(zone_id, [])


def get_neurotoxin_indications(zone_id: str) -> list[NeurotoxinIndication]:
    return NEUROTOXIN_INDICATIONS.get(zone_id, [])


def get_vascular_risk(zone_id: str) -> tuple[str, ...]:
    return VASCULAR_RISK_ZONES.get(zone_id, ())


def get_structural_priority(zone_id: str) -> int:
    return STRUCTURAL_PRIORITY.get(zone_id, 5)


def products_for_category(category: ProductCategory) -> list[ProductProfile]:
    return [p for p in PRODUCTS.values() if p.category == category]


def is_high_risk_zone(zone_id: str) -> bool:
    return zone_id in VASCULAR_RISK_ZONES
