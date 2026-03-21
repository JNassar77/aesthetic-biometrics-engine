"""
Multi-view fusion engine.

Combines landmark-based measurements from frontal, profile, and oblique views
into a unified per-zone analysis result.

CRITICAL DESIGN RULE:
- Only LANDMARK GEOMETRY is fused across views.
- BLENDSHAPES are NEVER fused — they remain view-bound because
  the patient's expression changes between photo captures.

Fusion strategy per zone:
1. Identify which views contribute to the zone (primary + secondary).
2. For each measurement, use the primary view's value as base.
3. If a secondary view also measures the same metric, apply
   confidence-weighted averaging.
4. Detect contradictions between views (e.g., large discrepancy
   in a measurement that should be consistent).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.treatment.zone_definitions import (
    ZONES, ZoneDefinition, ViewPriority, zones_needing_fusion,
)


@dataclass
class ViewMeasurement:
    """A single measurement from one view."""
    metric_name: str
    value: float
    unit: str = "mm"
    view: str = ""
    confidence: float = 1.0


@dataclass
class FusedMeasurement:
    """A measurement fused from one or more views."""
    metric_name: str
    fused_value: float
    unit: str = "mm"
    primary_view: str = ""
    contributing_views: list[str] = field(default_factory=list)
    confidence: float = 1.0
    contradiction: bool = False
    contradiction_detail: str = ""


@dataclass
class ViewContradiction:
    """A detected contradiction between views for a zone."""
    zone_id: str
    metric_name: str
    view_a: str
    value_a: float
    view_b: str
    value_b: float
    difference: float
    difference_pct: float
    description: str


@dataclass
class ZoneFusionResult:
    """Fused result for one zone from multiple views."""
    zone_id: str
    zone_name: str
    region: str
    primary_view: str
    contributing_views: list[str] = field(default_factory=list)
    measurements: list[FusedMeasurement] = field(default_factory=list)
    contradictions: list[ViewContradiction] = field(default_factory=list)
    fusion_confidence: float = 1.0


@dataclass
class FusionResult:
    """Complete multi-view fusion output."""
    zones: list[ZoneFusionResult] = field(default_factory=list)
    contradictions: list[ViewContradiction] = field(default_factory=list)
    views_used: list[str] = field(default_factory=list)


# Confidence weights for each view type per region
# Primary view gets the highest weight, secondary views confirm
VIEW_CONFIDENCE: dict[str, float] = {
    "primary": 1.0,
    "secondary": 0.7,
}

# Contradiction thresholds: if two views disagree by more than this,
# flag a contradiction (metric-type-dependent)
CONTRADICTION_THRESHOLDS: dict[str, float] = {
    "mm": 3.0,        # >3mm difference between views = contradiction
    "deg": 10.0,      # >10° difference = contradiction
    "ratio": 0.15,    # >0.15 ratio difference = contradiction
    "score": 15.0,    # >15 points on a 0-100 score = contradiction
    "%": 10.0,        # >10% difference = contradiction
}


def _get_contradiction_threshold(unit: str) -> float:
    """Get the contradiction threshold for a measurement unit."""
    return CONTRADICTION_THRESHOLDS.get(unit, 3.0)


def _fuse_values(
    primary_value: float,
    secondary_values: list[tuple[float, float]],  # (value, confidence)
) -> tuple[float, float]:
    """Confidence-weighted fusion of a primary value with secondary measurements.

    Args:
        primary_value: Value from the primary view (confidence = 1.0)
        secondary_values: List of (value, confidence) from secondary views

    Returns:
        (fused_value, overall_confidence)
    """
    if not secondary_values:
        return primary_value, 1.0

    total_weight = VIEW_CONFIDENCE["primary"]
    weighted_sum = primary_value * VIEW_CONFIDENCE["primary"]

    for value, conf in secondary_values:
        weight = conf * VIEW_CONFIDENCE["secondary"]
        weighted_sum += value * weight
        total_weight += weight

    fused = weighted_sum / total_weight
    # Confidence increases with more confirming views
    confidence = min(1.0, 0.8 + len(secondary_values) * 0.1)

    return fused, confidence


def _detect_contradiction(
    metric_name: str,
    unit: str,
    view_a: str,
    value_a: float,
    view_b: str,
    value_b: float,
    zone_id: str,
) -> ViewContradiction | None:
    """Check if two views contradict each other for a measurement."""
    threshold = _get_contradiction_threshold(unit)
    diff = abs(value_a - value_b)

    # Calculate percentage difference relative to the larger value
    max_val = max(abs(value_a), abs(value_b), 0.01)
    diff_pct = (diff / max_val) * 100

    if diff > threshold:
        return ViewContradiction(
            zone_id=zone_id,
            metric_name=metric_name,
            view_a=view_a,
            value_a=round(value_a, 2),
            view_b=view_b,
            value_b=round(value_b, 2),
            difference=round(diff, 2),
            difference_pct=round(diff_pct, 1),
            description=(
                f"Zone {zone_id}: {metric_name} differs by {diff:.1f}{unit} "
                f"({diff_pct:.0f}%) between {view_a} ({value_a:.1f}) "
                f"and {view_b} ({value_b:.1f})."
            ),
        )
    return None


def fuse_zone_measurements(
    zone_def: ZoneDefinition,
    view_measurements: dict[str, list[ViewMeasurement]],
) -> ZoneFusionResult:
    """Fuse measurements for a single zone from multiple views.

    Args:
        zone_def: Zone definition with primary/secondary views
        view_measurements: Dict of view_name → list of measurements for this zone

    Returns:
        Fused zone result with combined measurements and any contradictions
    """
    primary = zone_def.primary_view.value
    secondary_views = [v.value for v in zone_def.secondary_views]

    contributing = [primary] if primary in view_measurements else []
    contributing += [v for v in secondary_views if v in view_measurements]

    fused_measurements: list[FusedMeasurement] = []
    contradictions: list[ViewContradiction] = []

    # Collect all unique metrics across views
    all_metrics: dict[str, dict[str, ViewMeasurement]] = {}
    for view_name, measurements in view_measurements.items():
        for m in measurements:
            if m.metric_name not in all_metrics:
                all_metrics[m.metric_name] = {}
            all_metrics[m.metric_name][view_name] = m

    for metric_name, view_data in all_metrics.items():
        # Get primary view measurement
        primary_m = view_data.get(primary)
        secondary_ms = [
            (view_data[v].value, view_data[v].confidence)
            for v in secondary_views
            if v in view_data
        ]

        if primary_m is not None:
            fused_val, confidence = _fuse_values(primary_m.value, secondary_ms)
            unit = primary_m.unit

            # Check for contradictions between views
            for sv in secondary_views:
                if sv in view_data:
                    contradiction = _detect_contradiction(
                        metric_name, unit,
                        primary, primary_m.value,
                        sv, view_data[sv].value,
                        zone_def.zone_id,
                    )
                    if contradiction is not None:
                        contradictions.append(contradiction)
                        # Lower confidence if contradiction detected
                        confidence *= 0.6

            fused_measurements.append(FusedMeasurement(
                metric_name=metric_name,
                fused_value=round(fused_val, 2),
                unit=unit,
                primary_view=primary,
                contributing_views=[v for v in contributing if v in view_data],
                confidence=round(confidence, 2),
                contradiction=any(
                    c.metric_name == metric_name for c in contradictions
                ),
            ))
        elif view_data:
            # No primary view available — use best available secondary
            best_view = max(view_data.keys(), key=lambda v: view_data[v].confidence)
            m = view_data[best_view]
            fused_measurements.append(FusedMeasurement(
                metric_name=metric_name,
                fused_value=round(m.value, 2),
                unit=m.unit,
                primary_view=best_view,
                contributing_views=[best_view],
                confidence=round(m.confidence * 0.8, 2),  # Penalize missing primary
            ))

    # Overall fusion confidence
    if fused_measurements:
        fusion_conf = sum(m.confidence for m in fused_measurements) / len(fused_measurements)
    else:
        fusion_conf = 0.0

    return ZoneFusionResult(
        zone_id=zone_def.zone_id,
        zone_name=zone_def.zone_name,
        region=zone_def.region.value,
        primary_view=primary,
        contributing_views=contributing,
        measurements=fused_measurements,
        contradictions=contradictions,
        fusion_confidence=round(fusion_conf, 2),
    )


def fuse_all_zones(
    zone_view_data: dict[str, dict[str, list[ViewMeasurement]]],
    available_views: list[str] | None = None,
) -> FusionResult:
    """Fuse measurements for all zones across all available views.

    Args:
        zone_view_data: Nested dict: zone_id → view_name → list[ViewMeasurement]
        available_views: Which views were provided (e.g., ["frontal", "profile"])

    Returns:
        Complete fusion result with all zones and contradictions
    """
    if available_views is None:
        # Infer from data
        all_views = set()
        for zone_data in zone_view_data.values():
            all_views.update(zone_data.keys())
        available_views = sorted(all_views)

    zone_results: list[ZoneFusionResult] = []
    all_contradictions: list[ViewContradiction] = []

    for zone_id, zone_def in ZONES.items():
        view_data = zone_view_data.get(zone_id, {})

        # Only process zones that have data from at least one view
        if not view_data:
            continue

        # For zones that don't need fusion, just pass through the primary view
        if not zone_def.needs_fusion:
            result = fuse_zone_measurements(zone_def, view_data)
        else:
            result = fuse_zone_measurements(zone_def, view_data)

        zone_results.append(result)
        all_contradictions.extend(result.contradictions)

    return FusionResult(
        zones=zone_results,
        contradictions=all_contradictions,
        views_used=available_views,
    )
