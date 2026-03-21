"""
Treatment Plan Generator — converts zone analysis into a prioritized treatment plan.

Takes a ZoneReport (from zone_analyzer.analyze()) and produces a TreatmentPlan with:
1. Severity-based prioritization of zones
2. Clinical ordering (structural before detail)
3. Product recommendations per zone
4. Session planning (what to treat in session 1 vs. 2+)
5. Total volume estimation
6. Contraindication checks

Clinical logic:
- Structural zones first (midface, chin, jawline) → creates foundation
- Detail zones second (lips, folds, lines) → refinement
- Neurotoxin zones independent → can treat in parallel
- High-risk zones flagged with safety notes
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models.zone_models import ZoneResult
from app.treatment.product_database import (
    get_zone_recommendations,
    get_neurotoxin_indications,
    get_structural_priority,
    get_vascular_risk,
    is_high_risk_zone,
    ZoneProductRecommendation,
    NeurotoxinIndication,
    ProductCategory,
    STRUCTURAL_PRIORITY,
)
from app.treatment.contraindication_check import (
    check_contraindications,
    Contraindication,
)


# ──────────────────────── Data Models ────────────────────────

@dataclass
class ProductRecommendation:
    """A specific product recommendation for a zone."""
    products: list[str]
    category: str
    techniques: list[str]
    depth: str
    volume_range_ml: tuple[float, float]
    description: str
    safety_notes: list[str] = field(default_factory=list)


@dataclass
class NeurotoxinRecommendation:
    """Neurotoxin recommendation for a zone."""
    target_muscle: str
    products: list[str]
    dose_range_units: tuple[int, int]
    description: str
    safety_notes: list[str] = field(default_factory=list)


@dataclass
class TreatmentConcern:
    """A single treatment concern with zone, priority, and recommendation."""
    priority: int
    zone_id: str
    zone_name: str
    region: str
    severity: float
    concern: str
    filler_recommendations: list[ProductRecommendation] = field(default_factory=list)
    neurotoxin_recommendations: list[NeurotoxinRecommendation] = field(default_factory=list)
    is_high_risk: bool = False
    vascular_risk: list[str] = field(default_factory=list)
    session: int = 1  # Which session this should be treated in


@dataclass
class SessionPlan:
    """Plan for one treatment session."""
    session_number: int
    concerns: list[TreatmentConcern]
    total_filler_volume_ml: tuple[float, float]  # min, max
    total_neurotoxin_units: tuple[int, int]  # min, max (Botox-equivalent)
    focus: str  # e.g. "Structural foundation" or "Refinement"


@dataclass
class TreatmentPlan:
    """Complete treatment plan from zone analysis."""
    primary_concerns: list[TreatmentConcern]
    secondary_concerns: list[TreatmentConcern]
    contraindications: list[Contraindication]
    sessions: list[SessionPlan]
    total_volume_estimate_ml: tuple[float, float]
    total_neurotoxin_units: tuple[int, int]
    session_count: int
    session_interval_weeks: int = 4


# ──────────────────────── Severity Thresholds ────────────────────────

PRIMARY_SEVERITY_THRESHOLD = 3.0    # Zones with severity >= 3 are primary concerns
SECONDARY_SEVERITY_THRESHOLD = 1.0  # Zones with 1 <= severity < 3 are secondary
TREATMENT_MIN_SEVERITY = 1.0        # Below this, no treatment recommended


# ──────────────────────── Session Planning Logic ────────────────────────

MAX_FILLER_PER_SESSION_ML = 6.0     # Conservative safety limit
MAX_ZONES_PER_SESSION = 6           # Practical limit for one appointment


def _classify_concern(zone: ZoneResult) -> str:
    """Generate a concise clinical concern description from zone findings."""
    if zone.findings:
        # Use the most severe finding as the concern summary
        top_finding = max(zone.findings, key=lambda f: f.severity_contribution)
        # Shorten to a clean concern label
        desc = top_finding.description
        # If it's too long, truncate to the zone name + key info
        if len(desc) > 100:
            return f"{zone.zone_name} — severity {zone.severity:.1f}/10"
        return desc
    return f"{zone.zone_name} — deviation detected (severity {zone.severity:.1f}/10)"


def _build_filler_recommendations(zone_id: str) -> list[ProductRecommendation]:
    """Get filler product recommendations for a zone."""
    recs = get_zone_recommendations(zone_id)
    return [
        ProductRecommendation(
            products=list(r.products),
            category=r.category.value,
            techniques=[t.value for t in r.techniques],
            depth=r.depth.value,
            volume_range_ml=r.volume_range_ml,
            description=r.description,
            safety_notes=list(r.safety_notes),
        )
        for r in recs
    ]


def _build_neurotoxin_recommendations(zone_id: str) -> list[NeurotoxinRecommendation]:
    """Get neurotoxin recommendations for a zone."""
    indications = get_neurotoxin_indications(zone_id)
    return [
        NeurotoxinRecommendation(
            target_muscle=ind.target_muscle,
            products=list(ind.products),
            dose_range_units=ind.dose_range_units,
            description=ind.description,
            safety_notes=list(ind.safety_notes),
        )
        for ind in indications
    ]


def _compute_priority_score(zone: ZoneResult) -> float:
    """Compute a composite priority score for sorting.

    Combines severity (how bad) with structural priority (treat-first order).
    Higher score = higher priority = treat first.
    """
    structural_order = get_structural_priority(zone.zone_id)
    # Invert structural priority (1=highest becomes weight 5, 5=lowest becomes 1)
    structural_weight = 6 - structural_order

    # Composite: severity dominates, structural order breaks ties
    return zone.severity * 2.0 + structural_weight


def _assign_sessions(concerns: list[TreatmentConcern]) -> list[SessionPlan]:
    """Assign treatment concerns to sessions based on clinical logic.

    Rules:
    1. Structural zones (priority 1-2) go in Session 1
    2. Volume/fold zones (priority 3-4) go in Session 1 if capacity allows, else Session 2
    3. Detail zones (priority 5) go in Session 2
    4. Max filler volume per session: 6ml
    5. Max zones per session: 6
    6. Neurotoxin zones can be added to any session (separate from volume limit)
    """
    if not concerns:
        return []

    sessions: dict[int, list[TreatmentConcern]] = {}
    current_session = 1
    current_volume_max = 0.0
    current_zone_count = 0

    # Sort by structural priority, then severity
    sorted_concerns = sorted(
        concerns,
        key=lambda c: (get_structural_priority(c.zone_id), -c.severity),
    )

    for concern in sorted_concerns:
        # Calculate volume for this concern
        concern_volume_max = sum(
            r.volume_range_ml[1] for r in concern.filler_recommendations
        )

        # Check if neurotoxin-only (doesn't consume filler volume)
        is_neurotoxin_only = (
            not concern.filler_recommendations
            and concern.neurotoxin_recommendations
        )

        # Determine session assignment
        needs_new_session = False
        if not is_neurotoxin_only:
            if (current_volume_max + concern_volume_max > MAX_FILLER_PER_SESSION_ML
                    or current_zone_count >= MAX_ZONES_PER_SESSION):
                needs_new_session = True

        if needs_new_session:
            current_session += 1
            current_volume_max = 0.0
            current_zone_count = 0

        concern.session = current_session

        if current_session not in sessions:
            sessions[current_session] = []
        sessions[current_session].append(concern)

        if not is_neurotoxin_only:
            current_volume_max += concern_volume_max
            current_zone_count += 1

    # Build SessionPlan objects
    session_plans: list[SessionPlan] = []
    for session_num in sorted(sessions.keys()):
        session_concerns = sessions[session_num]

        filler_vol_min = sum(
            sum(r.volume_range_ml[0] for r in c.filler_recommendations)
            for c in session_concerns
        )
        filler_vol_max = sum(
            sum(r.volume_range_ml[1] for r in c.filler_recommendations)
            for c in session_concerns
        )
        toxin_min = sum(
            sum(r.dose_range_units[0] for r in c.neurotoxin_recommendations)
            for c in session_concerns
        )
        toxin_max = sum(
            sum(r.dose_range_units[1] for r in c.neurotoxin_recommendations)
            for c in session_concerns
        )

        # Determine session focus
        structural_ids = {z for z, p in STRUCTURAL_PRIORITY.items() if p <= 2}
        has_structural = any(c.zone_id in structural_ids for c in session_concerns)
        if has_structural:
            focus = "Structural foundation and volume restoration"
        elif session_num == 1:
            focus = "Primary treatment areas"
        else:
            focus = "Refinement and detail work"

        session_plans.append(SessionPlan(
            session_number=session_num,
            concerns=session_concerns,
            total_filler_volume_ml=(round(filler_vol_min, 1), round(filler_vol_max, 1)),
            total_neurotoxin_units=(toxin_min, toxin_max),
            focus=focus,
        ))

    return session_plans


# ──────────────────────── Main Generate Function ────────────────────────

def generate(zones: list[ZoneResult]) -> TreatmentPlan:
    """Generate a prioritized treatment plan from zone analysis results.

    Args:
        zones: List of ZoneResult from zone_analyzer.analyze().
               Expected to be sorted by severity (highest first).

    Returns:
        TreatmentPlan with prioritized concerns, product recommendations,
        session planning, and contraindications.
    """
    if not zones:
        return TreatmentPlan(
            primary_concerns=[],
            secondary_concerns=[],
            contraindications=[],
            sessions=[],
            total_volume_estimate_ml=(0.0, 0.0),
            total_neurotoxin_units=(0, 0),
            session_count=0,
        )

    # ── Step 1: Build treatment concerns for zones above threshold ──
    all_concerns: list[TreatmentConcern] = []

    for zone in zones:
        if zone.severity < TREATMENT_MIN_SEVERITY:
            continue

        filler_recs = _build_filler_recommendations(zone.zone_id)
        toxin_recs = _build_neurotoxin_recommendations(zone.zone_id)

        # Skip zone if no treatment options exist
        if not filler_recs and not toxin_recs:
            continue

        vascular = list(get_vascular_risk(zone.zone_id))

        concern = TreatmentConcern(
            priority=0,  # Will be assigned after sorting
            zone_id=zone.zone_id,
            zone_name=zone.zone_name,
            region=zone.region,
            severity=zone.severity,
            concern=_classify_concern(zone),
            filler_recommendations=filler_recs,
            neurotoxin_recommendations=toxin_recs,
            is_high_risk=is_high_risk_zone(zone.zone_id),
            vascular_risk=vascular,
        )
        all_concerns.append(concern)

    # ── Step 2: Sort by composite priority score ──
    all_concerns.sort(key=lambda c: _compute_priority_score(c), reverse=True)

    # Assign priority numbers
    for i, concern in enumerate(all_concerns):
        concern.priority = i + 1

    # ── Step 3: Split into primary and secondary ──
    primary = [c for c in all_concerns if c.severity >= PRIMARY_SEVERITY_THRESHOLD]
    secondary = [c for c in all_concerns if c.severity < PRIMARY_SEVERITY_THRESHOLD]

    # ── Step 4: Session planning (only for primary concerns) ──
    sessions = _assign_sessions(primary)

    # ── Step 5: Contraindication checks ──
    contraindications = check_contraindications(zones)

    # ── Step 6: Total volume and units estimation ──
    total_vol_min = sum(
        sum(r.volume_range_ml[0] for r in c.filler_recommendations)
        for c in all_concerns
    )
    total_vol_max = sum(
        sum(r.volume_range_ml[1] for r in c.filler_recommendations)
        for c in all_concerns
    )
    total_toxin_min = sum(
        sum(r.dose_range_units[0] for r in c.neurotoxin_recommendations)
        for c in all_concerns
    )
    total_toxin_max = sum(
        sum(r.dose_range_units[1] for r in c.neurotoxin_recommendations)
        for c in all_concerns
    )

    session_count = len(sessions)

    return TreatmentPlan(
        primary_concerns=primary,
        secondary_concerns=secondary,
        contraindications=contraindications,
        sessions=sessions,
        total_volume_estimate_ml=(round(total_vol_min, 1), round(total_vol_max, 1)),
        total_neurotoxin_units=(total_toxin_min, total_toxin_max),
        session_count=session_count,
    )
