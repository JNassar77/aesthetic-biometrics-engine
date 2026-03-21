"""
Comparison Engine — Before/After treatment analysis.

Compares two ZoneReports (pre-treatment and post-treatment) to quantify
treatment outcomes:
1. Per-zone delta: severity change, measurement changes
2. Overall improvement score (0-100)
3. Heatmap data for frontend visualization (zone → color intensity)

Pure computation — no database dependencies. Results can be persisted
in Supabase `treatment_comparisons.zone_deltas` as JSONB.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models.zone_models import ZoneResult, ZoneMeasurement
from app.analysis.zone_analyzer import ZoneReport, REGION_WEIGHTS


# ──────────────────────── Data Models ────────────────────────

@dataclass
class MeasurementDelta:
    """Change in a single measurement between pre and post."""
    name: str
    pre_value: float
    post_value: float
    delta: float           # post - pre (negative = improvement for deviations)
    delta_pct: float       # % change relative to pre
    unit: str
    improved: bool         # True if moved closer to ideal range


@dataclass
class ZoneDelta:
    """Change in one zone between pre and post assessment."""
    zone_id: str
    zone_name: str
    region: str
    pre_severity: float
    post_severity: float
    severity_delta: float          # post - pre (negative = improvement)
    severity_improvement_pct: float  # % improvement (positive = better)
    measurement_deltas: list[MeasurementDelta] = field(default_factory=list)
    status: str = "unchanged"      # "improved", "worsened", "unchanged", "new", "resolved"


@dataclass
class HeatmapEntry:
    """Visualization data for one zone in a before/after heatmap."""
    zone_id: str
    zone_name: str
    region: str
    pre_intensity: float    # 0-1, based on pre severity (0=no issue, 1=severe)
    post_intensity: float   # 0-1, based on post severity
    delta_intensity: float  # -1 to +1, improvement vs worsening
    color_code: str         # Suggested color: green=improved, red=worsened, gray=unchanged


@dataclass
class ComparisonResult:
    """Complete before/after comparison."""
    zone_deltas: list[ZoneDelta]
    improvement_score: float          # 0-100 overall improvement
    aesthetic_score_pre: float        # Pre aesthetic score
    aesthetic_score_post: float       # Post aesthetic score
    aesthetic_score_delta: float      # Post - Pre (positive = improvement)
    zones_improved: int
    zones_worsened: int
    zones_unchanged: int
    zones_resolved: int               # Zones that dropped below treatment threshold
    zones_new: int                    # Zones that appeared post-treatment
    heatmap: list[HeatmapEntry] = field(default_factory=list)
    summary: str = ""


# ──────────────────────── Constants ────────────────────────

SEVERITY_CHANGE_THRESHOLD = 0.5   # Min change to count as improved/worsened
RESOLVED_THRESHOLD = 1.0          # Below this severity = resolved
MEASUREMENT_CHANGE_THRESHOLD = 0.05  # Min % change to count as changed


# ──────────────────────── Delta Computation ────────────────────────

def _compute_measurement_deltas(
    pre_measurements: list[ZoneMeasurement],
    post_measurements: list[ZoneMeasurement],
) -> list[MeasurementDelta]:
    """Compute per-measurement deltas between pre and post."""
    pre_lookup = {m.name: m for m in pre_measurements}
    post_lookup = {m.name: m for m in post_measurements}

    all_names = set(pre_lookup.keys()) | set(post_lookup.keys())
    deltas: list[MeasurementDelta] = []

    for name in sorted(all_names):
        pre_m = pre_lookup.get(name)
        post_m = post_lookup.get(name)

        if pre_m is None or post_m is None:
            continue  # Measurement only in one assessment — skip

        delta = post_m.value - pre_m.value
        if pre_m.value != 0:
            delta_pct = round((delta / abs(pre_m.value)) * 100, 1)
        else:
            delta_pct = 0.0 if delta == 0 else 100.0

        # Determine if this is an improvement:
        # If we have ideal ranges, check if post is closer to ideal
        improved = False
        if pre_m.ideal_min is not None and pre_m.ideal_max is not None:
            ideal_mid = (pre_m.ideal_min + pre_m.ideal_max) / 2
            pre_dist = abs(pre_m.value - ideal_mid)
            post_dist = abs(post_m.value - ideal_mid)
            improved = post_dist < pre_dist - MEASUREMENT_CHANGE_THRESHOLD
        else:
            # No ideal range — treat decrease in deviation-type metrics as improvement
            if "asymmetry" in name.lower() or "deviation" in name.lower() or "deficit" in name.lower():
                improved = delta < 0
            elif "depth" in name.lower() and "tear" in name.lower():
                improved = delta < 0  # Less depth = better for tear trough

        deltas.append(MeasurementDelta(
            name=name,
            pre_value=round(pre_m.value, 2),
            post_value=round(post_m.value, 2),
            delta=round(delta, 2),
            delta_pct=delta_pct,
            unit=pre_m.unit,
            improved=improved,
        ))

    return deltas


def _compute_zone_delta(
    pre_zone: ZoneResult | None,
    post_zone: ZoneResult | None,
) -> ZoneDelta:
    """Compute delta for a single zone."""
    if pre_zone is None and post_zone is not None:
        return ZoneDelta(
            zone_id=post_zone.zone_id,
            zone_name=post_zone.zone_name,
            region=post_zone.region,
            pre_severity=0.0,
            post_severity=post_zone.severity,
            severity_delta=post_zone.severity,
            severity_improvement_pct=-100.0 if post_zone.severity > 0 else 0.0,
            status="new",
        )

    if post_zone is None and pre_zone is not None:
        return ZoneDelta(
            zone_id=pre_zone.zone_id,
            zone_name=pre_zone.zone_name,
            region=pre_zone.region,
            pre_severity=pre_zone.severity,
            post_severity=0.0,
            severity_delta=-pre_zone.severity,
            severity_improvement_pct=100.0,
            status="resolved",
        )

    # Both exist
    assert pre_zone is not None and post_zone is not None

    severity_delta = post_zone.severity - pre_zone.severity
    if pre_zone.severity > 0:
        improvement_pct = round((-severity_delta / pre_zone.severity) * 100, 1)
    else:
        improvement_pct = 0.0 if severity_delta == 0 else -100.0

    # Status
    if post_zone.severity < RESOLVED_THRESHOLD and pre_zone.severity >= RESOLVED_THRESHOLD:
        status = "resolved"
    elif severity_delta < -SEVERITY_CHANGE_THRESHOLD:
        status = "improved"
    elif severity_delta > SEVERITY_CHANGE_THRESHOLD:
        status = "worsened"
    else:
        status = "unchanged"

    measurement_deltas = _compute_measurement_deltas(
        pre_zone.measurements, post_zone.measurements,
    )

    return ZoneDelta(
        zone_id=pre_zone.zone_id,
        zone_name=pre_zone.zone_name,
        region=pre_zone.region,
        pre_severity=pre_zone.severity,
        post_severity=post_zone.severity,
        severity_delta=round(severity_delta, 1),
        severity_improvement_pct=improvement_pct,
        measurement_deltas=measurement_deltas,
        status=status,
    )


# ──────────────────────── Heatmap Generation ────────────────────────

def _generate_heatmap(zone_deltas: list[ZoneDelta]) -> list[HeatmapEntry]:
    """Generate visualization heatmap data from zone deltas."""
    heatmap: list[HeatmapEntry] = []

    for zd in zone_deltas:
        pre_intensity = min(1.0, zd.pre_severity / 10.0)
        post_intensity = min(1.0, zd.post_severity / 10.0)

        # Delta intensity: -1 (fully improved) to +1 (fully worsened)
        if zd.pre_severity > 0:
            delta_intensity = zd.severity_delta / max(zd.pre_severity, 1.0)
        else:
            delta_intensity = min(1.0, zd.post_severity / 5.0) if zd.post_severity > 0 else 0.0
        delta_intensity = max(-1.0, min(1.0, delta_intensity))

        # Color suggestion
        if zd.status == "resolved":
            color_code = "#22c55e"    # green-500
        elif zd.status == "improved":
            color_code = "#4ade80"    # green-400
        elif zd.status == "worsened":
            color_code = "#ef4444"    # red-500
        elif zd.status == "new":
            color_code = "#f97316"    # orange-500
        else:
            color_code = "#9ca3af"    # gray-400

        heatmap.append(HeatmapEntry(
            zone_id=zd.zone_id,
            zone_name=zd.zone_name,
            region=zd.region,
            pre_intensity=round(pre_intensity, 2),
            post_intensity=round(post_intensity, 2),
            delta_intensity=round(delta_intensity, 2),
            color_code=color_code,
        ))

    return heatmap


# ──────────────────────── Improvement Score ────────────────────────

def _compute_improvement_score(zone_deltas: list[ZoneDelta]) -> float:
    """Compute overall improvement score (0-100).

    Weighted by region importance (same weights as aesthetic score).
    100 = all zones fully resolved, 0 = no improvement or worsened.
    50 = baseline (no change).
    """
    if not zone_deltas:
        return 50.0

    weighted_improvement = 0.0
    weight_total = 0.0

    for zd in zone_deltas:
        if zd.pre_severity < RESOLVED_THRESHOLD and zd.status != "new":
            continue  # Skip zones that were already fine

        w = REGION_WEIGHTS.get(zd.region, 1.0)

        # Improvement ratio: how much of the severity was resolved
        if zd.pre_severity > 0:
            improvement_ratio = -zd.severity_delta / zd.pre_severity
        elif zd.status == "new":
            improvement_ratio = -1.0  # New problem = negative
        else:
            improvement_ratio = 0.0

        # Clamp to [-1, 1]
        improvement_ratio = max(-1.0, min(1.0, improvement_ratio))

        weighted_improvement += improvement_ratio * w
        weight_total += w

    if weight_total == 0:
        return 50.0

    # Scale from [-1, 1] to [0, 100] where 50 = no change
    raw = weighted_improvement / weight_total
    return round(max(0.0, min(100.0, 50.0 + raw * 50.0)), 1)


# ──────────────────────── Summary Text ────────────────────────

def _generate_summary(result: ComparisonResult) -> str:
    """Generate a human-readable summary of the comparison."""
    parts: list[str] = []

    # Aesthetic score change
    delta_sign = "+" if result.aesthetic_score_delta > 0 else ""
    parts.append(
        f"Aesthetic score: {result.aesthetic_score_pre:.1f} → "
        f"{result.aesthetic_score_post:.1f} ({delta_sign}{result.aesthetic_score_delta:.1f})"
    )

    # Zone status counts
    statuses: list[str] = []
    if result.zones_improved > 0:
        statuses.append(f"{result.zones_improved} improved")
    if result.zones_resolved > 0:
        statuses.append(f"{result.zones_resolved} resolved")
    if result.zones_unchanged > 0:
        statuses.append(f"{result.zones_unchanged} unchanged")
    if result.zones_worsened > 0:
        statuses.append(f"{result.zones_worsened} worsened")
    if result.zones_new > 0:
        statuses.append(f"{result.zones_new} new concerns")
    if statuses:
        parts.append(f"Zones: {', '.join(statuses)}")

    # Overall assessment
    if result.improvement_score >= 75:
        parts.append("Overall: Excellent treatment outcome")
    elif result.improvement_score >= 60:
        parts.append("Overall: Good improvement")
    elif result.improvement_score >= 50:
        parts.append("Overall: Moderate improvement")
    elif result.improvement_score >= 40:
        parts.append("Overall: Minimal change")
    else:
        parts.append("Overall: Concerns noted — review treatment approach")

    return ". ".join(parts) + "."


# ──────────────────────── Main Compare Function ────────────────────────

def compare(pre: ZoneReport, post: ZoneReport) -> ComparisonResult:
    """Compare two ZoneReports to quantify treatment outcomes.

    Args:
        pre: ZoneReport from before treatment.
        post: ZoneReport from after treatment.

    Returns:
        ComparisonResult with per-zone deltas, improvement score,
        and heatmap visualization data.
    """
    # Build zone lookups
    pre_zones = {z.zone_id: z for z in pre.zones}
    post_zones = {z.zone_id: z for z in post.zones}
    all_zone_ids = set(pre_zones.keys()) | set(post_zones.keys())

    # Compute deltas
    zone_deltas: list[ZoneDelta] = []
    for zone_id in sorted(all_zone_ids):
        delta = _compute_zone_delta(pre_zones.get(zone_id), post_zones.get(zone_id))
        zone_deltas.append(delta)

    # Sort by absolute severity delta (most changed first)
    zone_deltas.sort(key=lambda d: abs(d.severity_delta), reverse=True)

    # Count statuses
    zones_improved = sum(1 for d in zone_deltas if d.status == "improved")
    zones_worsened = sum(1 for d in zone_deltas if d.status == "worsened")
    zones_unchanged = sum(1 for d in zone_deltas if d.status == "unchanged")
    zones_resolved = sum(1 for d in zone_deltas if d.status == "resolved")
    zones_new = sum(1 for d in zone_deltas if d.status == "new")

    # Improvement score
    improvement_score = _compute_improvement_score(zone_deltas)

    # Heatmap
    heatmap = _generate_heatmap(zone_deltas)

    # Aesthetic score deltas
    aesthetic_delta = round(post.aesthetic_score - pre.aesthetic_score, 1)

    result = ComparisonResult(
        zone_deltas=zone_deltas,
        improvement_score=improvement_score,
        aesthetic_score_pre=pre.aesthetic_score,
        aesthetic_score_post=post.aesthetic_score,
        aesthetic_score_delta=aesthetic_delta,
        zones_improved=zones_improved,
        zones_worsened=zones_worsened,
        zones_unchanged=zones_unchanged,
        zones_resolved=zones_resolved,
        zones_new=zones_new,
        heatmap=heatmap,
    )

    result.summary = _generate_summary(result)
    return result
