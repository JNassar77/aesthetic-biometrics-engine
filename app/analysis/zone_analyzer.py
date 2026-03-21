"""
Zone Analyzer — orchestrates all analysis engines into a unified zone report.

This is the top-level analysis module that:
1. Runs each engine (symmetry, proportion, profile, volume, aging) on the
   appropriate views.
2. Maps engine outputs to the 19 treatment zones.
3. Generates clinical findings text per zone.
4. Computes severity per zone and ranks them.
5. Computes a composite Aesthetic Score (0-100).

Input:  DetectionResult + CalibrationResult per view (frontal, profile, oblique)
Output: ZoneReport with ranked zones, findings, and aesthetic score.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.detection.face_landmarker import DetectionResult
from app.utils.pixel_calibration import CalibrationResult
from app.pipeline.quality_gate import compute_expression_deviation
from app.treatment.zone_definitions import (
    ZONES, ZoneDefinition, Region, ViewPriority,
)
from app.models.zone_models import (
    ZoneResult, ZoneFinding, ZoneMeasurement, GlobalMetrics, CalibrationInfo,
)
from app.analysis import (
    symmetry_engine,
    proportion_engine,
    profile_engine,
    volume_engine,
    aging_engine,
)
from app.analysis.multi_view_fusion import (
    ViewMeasurement, fuse_all_zones, FusionResult,
)


# ──────────────────────── Data Containers ────────────────────────

@dataclass
class ViewInput:
    """Detection + calibration from one view."""
    detection: DetectionResult
    calibration: CalibrationResult
    blendshapes: dict[str, float] = field(default_factory=dict)


@dataclass
class ZoneReport:
    """Complete zone-based analysis report."""
    zones: list[ZoneResult]
    global_metrics: GlobalMetrics
    calibration: CalibrationInfo
    aesthetic_score: float
    expression_deviation: float  # 0-1, how non-neutral the frontal expression was
    views_analyzed: list[str] = field(default_factory=list)
    fusion_contradictions: list[str] = field(default_factory=list)


# ──────────────────────── Region Weights for Aesthetic Score ────────────────────────

REGION_WEIGHTS: dict[str, float] = {
    "upper_face": 1.0,
    "midface": 1.3,
    "lower_face": 1.1,
    "profile": 0.9,
}


# ──────────────────────── Engine → Zone Mapping ────────────────────────

def _extract_symmetry_zone_measurements(
    sym_result: symmetry_engine.SymmetryAnalysis,
) -> dict[str, list[ViewMeasurement]]:
    """Map symmetry engine results to zone measurements."""
    zone_map: dict[str, list[ViewMeasurement]] = {}

    # Map symmetry axes to zones
    AXIS_TO_ZONE = {
        "brow_height": "Bw1",
        "eye_width": "Tt1",
        "cheekbone_height": "Ck1",
        "nasolabial_region": "Ns1",
        "mouth_corner_height": "Lp3",
        "gonion_height": "Jl1",
    }

    for m in sym_result.measurements:
        zone_id = AXIS_TO_ZONE.get(m.axis_name)
        if zone_id:
            if zone_id not in zone_map:
                zone_map[zone_id] = []
            zone_map[zone_id].append(ViewMeasurement(
                metric_name=f"{m.axis_name}_asymmetry",
                value=m.difference_mm,
                unit="mm",
                view="frontal",
                confidence=1.0,
            ))
            zone_map[zone_id].append(ViewMeasurement(
                metric_name=f"{m.axis_name}_asymmetry_pct",
                value=m.difference_pct,
                unit="%",
                view="frontal",
                confidence=1.0,
            ))

    return zone_map


def _extract_proportion_zone_measurements(
    prop_result: proportion_engine.ProportionAnalysis,
) -> dict[str, list[ViewMeasurement]]:
    """Map proportion engine results to zone measurements."""
    zone_map: dict[str, list[ViewMeasurement]] = {}

    # Lip measurements → Lp1, Lp2
    lip = prop_result.lip
    zone_map["Lp1"] = [
        ViewMeasurement("upper_lip_height", lip.upper_lip_height_mm, "mm", "frontal"),
        ViewMeasurement("lip_ratio", lip.lip_ratio, "ratio", "frontal"),
        ViewMeasurement("cupid_bow_asymmetry", lip.cupid_bow_asymmetry_pct, "%", "frontal"),
    ]
    zone_map["Lp2"] = [
        ViewMeasurement("lower_lip_height", lip.lower_lip_height_mm, "mm", "frontal"),
    ]

    return zone_map


def _extract_profile_zone_measurements(
    prof_result: profile_engine.ProfileAnalysis,
) -> dict[str, list[ViewMeasurement]]:
    """Map profile engine results to zone measurements."""
    zone_map: dict[str, list[ViewMeasurement]] = {}

    # E-line → Pf2
    zone_map["Pf2"] = [
        ViewMeasurement("upper_lip_to_eline", prof_result.e_line.upper_lip_to_eline_mm, "mm", "profile"),
        ViewMeasurement("lower_lip_to_eline", prof_result.e_line.lower_lip_to_eline_mm, "mm", "profile"),
    ]

    # Nasal profile → Pf1
    zone_map["Pf1"] = [
        ViewMeasurement("nasolabial_angle", prof_result.nasal.nasolabial_angle_deg, "deg", "profile"),
        ViewMeasurement("nasofrontal_angle", prof_result.nasal.nasofrontal_angle_deg, "deg", "profile"),
        ViewMeasurement("dorsum_deviation", prof_result.nasal.dorsum_deviation_mm, "mm", "profile"),
    ]

    # Chin → Ch1
    zone_map["Ch1"] = [
        ViewMeasurement("chin_projection", prof_result.chin.chin_projection_mm, "mm", "profile"),
        ViewMeasurement("chin_height", prof_result.chin.chin_height_mm, "mm", "profile"),
    ]

    # Cervicomental → Pf3
    if prof_result.cervicomental:
        zone_map["Pf3"] = [
            ViewMeasurement("cervicomental_angle", prof_result.cervicomental.cervicomental_angle_deg, "deg", "profile"),
        ]

    # Steiner → Pf2 (add to existing)
    if prof_result.steiner_upper_lip_mm is not None:
        zone_map["Pf2"].append(
            ViewMeasurement("steiner_upper_lip", prof_result.steiner_upper_lip_mm, "mm", "profile")
        )

    return zone_map


def _extract_volume_zone_measurements(
    vol_result: volume_engine.VolumeAnalysis,
) -> dict[str, list[ViewMeasurement]]:
    """Map volume engine results to zone measurements."""
    zone_map: dict[str, list[ViewMeasurement]] = {}

    # Ogee → Ck2
    zone_map["Ck2"] = [
        ViewMeasurement("ogee_curve_score", vol_result.ogee.score, "score", "oblique"),
        ViewMeasurement("malar_depth", vol_result.ogee.malar_depth_mm, "mm", "oblique"),
    ]

    # Temporal → T1
    zone_map["T1"] = [
        ViewMeasurement("temporal_depth_left", vol_result.temporal.left_depth_mm, "mm", "oblique"),
        ViewMeasurement("temporal_depth_right", vol_result.temporal.right_depth_mm, "mm", "oblique"),
        ViewMeasurement("temporal_asymmetry", vol_result.temporal.asymmetry_mm, "mm", "oblique"),
    ]

    # Tear trough → Tt1
    tt_measurements = zone_map.get("Tt1", [])
    tt_measurements.extend([
        ViewMeasurement("tear_trough_depth_left", vol_result.tear_trough.left_depth_mm, "mm", "frontal"),
        ViewMeasurement("tear_trough_depth_right", vol_result.tear_trough.right_depth_mm, "mm", "frontal"),
    ])
    zone_map["Tt1"] = tt_measurements

    # Jowl → Jw1
    zone_map["Jw1"] = [
        ViewMeasurement("jowl_depth_left", vol_result.jowl.left_depth_mm, "mm", "frontal"),
        ViewMeasurement("jowl_depth_right", vol_result.jowl.right_depth_mm, "mm", "frontal"),
    ]

    return zone_map


def _extract_aging_zone_measurements(
    aging_result: aging_engine.AgingAnalysis,
) -> dict[str, list[ViewMeasurement]]:
    """Map aging engine results to zone measurements."""
    zone_map: dict[str, list[ViewMeasurement]] = {}

    # Frontalis → Fo1
    zone_map["Fo1"] = [
        ViewMeasurement("frontalis_compensation", aging_result.muscle_tonus.frontalis_compensation, "ratio", "frontal"),
    ]

    # Corrugator → Bw2
    zone_map["Bw2"] = [
        ViewMeasurement("corrugator_activity", aging_result.muscle_tonus.corrugator_activity, "ratio", "frontal"),
    ]

    # Gravitational drift → brow zone
    zone_map.setdefault("Bw1", []).append(
        ViewMeasurement("brow_descent", aging_result.gravitational_drift.brow_descent_mm, "mm", "frontal"),
    )

    # Midface descent → Ck3
    zone_map["Ck3"] = [
        ViewMeasurement("malar_descent", aging_result.gravitational_drift.malar_descent_mm, "mm", "frontal"),
    ]

    # Jowl descent → Jw1
    zone_map.setdefault("Jw1", []).append(
        ViewMeasurement("jowl_descent", aging_result.gravitational_drift.jowl_descent_mm, "mm", "frontal"),
    )

    return zone_map


# ──────────────────────── Severity Computation ────────────────────────

def _compute_zone_severity(
    zone_def: ZoneDefinition,
    measurements: list[ZoneMeasurement],
) -> float:
    """Compute severity (0-10) for a zone based on its measurements and reference ranges.

    Uses deviation from ideal ranges, weighted by the zone's severity_weights.
    """
    if not measurements:
        return 0.0

    # Build lookup of reference ranges
    ref_lookup = {r.metric_name: r for r in zone_def.reference_ranges}

    deviations: list[float] = []
    for m in measurements:
        ref = ref_lookup.get(m.name)
        if ref and ref.ideal_min is not None and ref.ideal_max is not None:
            if m.value < ref.ideal_min:
                dev = (ref.ideal_min - m.value) / max(abs(ref.ideal_min), 1.0)
            elif m.value > ref.ideal_max:
                dev = (m.value - ref.ideal_max) / max(abs(ref.ideal_max), 1.0)
            else:
                dev = 0.0
            deviations.append(min(1.0, abs(dev)))

    if not deviations:
        # No reference ranges matched — use a default low severity
        return 0.0

    avg_deviation = sum(deviations) / len(deviations)
    # Scale to 0-10
    return round(min(10.0, avg_deviation * 10), 1)


# ──────────────────────── Findings Text Generation ────────────────────────

def _generate_findings(
    zone_def: ZoneDefinition,
    measurements: list[ZoneMeasurement],
    severity: float,
    view: str,
) -> list[ZoneFinding]:
    """Generate clinical findings text for a zone based on measurements."""
    findings: list[ZoneFinding] = []

    ref_lookup = {r.metric_name: r for r in zone_def.reference_ranges}

    for m in measurements:
        ref = ref_lookup.get(m.name)
        if ref is None:
            # Generic finding
            if m.deviation_pct is not None and abs(m.deviation_pct) > 10:
                findings.append(ZoneFinding(
                    description=f"{m.name}: {m.value:.1f}{m.unit} ({abs(m.deviation_pct):.0f}% from ideal)",
                    severity_contribution=min(severity, 5.0),
                    source_view=view,
                ))
            continue

        # Generate specific finding based on deviation direction
        if m.value < ref.ideal_min:
            deficit = ref.ideal_min - m.value
            findings.append(ZoneFinding(
                description=(
                    f"{zone_def.zone_name}: {ref.description or m.name} "
                    f"is {m.value:.1f}{ref.unit} "
                    f"(below ideal range {ref.ideal_min:.1f}–{ref.ideal_max:.1f}{ref.unit}, "
                    f"deficit: {deficit:.1f}{ref.unit})"
                ),
                severity_contribution=min(10.0, deficit / max(abs(ref.ideal_min), 0.1) * 5),
                source_view=view,
            ))
        elif m.value > ref.ideal_max:
            excess = m.value - ref.ideal_max
            findings.append(ZoneFinding(
                description=(
                    f"{zone_def.zone_name}: {ref.description or m.name} "
                    f"is {m.value:.1f}{ref.unit} "
                    f"(above ideal range {ref.ideal_min:.1f}–{ref.ideal_max:.1f}{ref.unit}, "
                    f"excess: {excess:.1f}{ref.unit})"
                ),
                severity_contribution=min(10.0, excess / max(abs(ref.ideal_max), 0.1) * 5),
                source_view=view,
            ))

    # Add asymmetry findings
    asym_measurements = [m for m in measurements if "asymmetry" in m.name.lower()]
    for m in asym_measurements:
        if m.value > 2.0:  # >2mm or >2% is clinically noticeable
            findings.append(ZoneFinding(
                description=f"{zone_def.zone_name}: asymmetry detected ({m.value:.1f}{m.unit})",
                severity_contribution=min(5.0, m.value / 2.0),
                source_view=view,
            ))

    # Sort by severity contribution (most severe first)
    findings.sort(key=lambda f: f.severity_contribution, reverse=True)
    return findings[:5]  # Cap at 5 findings per zone


# ──────────────────────── Aesthetic Score ────────────────────────

def compute_aesthetic_score(zones: list[ZoneResult]) -> float:
    """Invertierte gewichtete Summe der Zone-Severities.

    100 = keine Behandlung nötig, 0 = maximaler Behandlungsbedarf.
    """
    if not zones:
        return 100.0

    weighted_sum = 0.0
    weight_total = 0.0
    for zone in zones:
        w = REGION_WEIGHTS.get(zone.region, 1.0)
        weighted_sum += zone.severity * w
        weight_total += 10.0 * w  # max severity = 10

    if weight_total == 0:
        return 100.0

    return round(max(0.0, (1.0 - weighted_sum / weight_total) * 100), 1)


# ──────────────────────── Main Analyze Function ────────────────────────

def analyze(
    frontal: ViewInput | None = None,
    profile: ViewInput | None = None,
    oblique: ViewInput | None = None,
) -> ZoneReport:
    """Run complete zone-based analysis across all available views.

    Orchestrates all engines, fuses measurements, generates findings,
    and computes the aesthetic score.

    Args:
        frontal: Frontal view detection + calibration (primary for symmetry/proportions)
        profile: Profile view detection + calibration (primary for E-line/nasal/chin)
        oblique: Oblique view detection + calibration (primary for volume/temporal)

    Returns:
        ZoneReport with ranked zones, findings, and aesthetic score.
    """
    views_analyzed: list[str] = []
    if frontal:
        views_analyzed.append("frontal")
    if profile:
        views_analyzed.append("profile")
    if oblique:
        views_analyzed.append("oblique")

    if not views_analyzed:
        raise ValueError("At least one view must be provided.")

    # ── Step 1: Run engines on appropriate views ──

    # Collect all zone → view → measurements
    zone_view_data: dict[str, dict[str, list[ViewMeasurement]]] = {}

    def _merge_zone_data(
        source: dict[str, list[ViewMeasurement]],
    ) -> None:
        for zone_id, measurements in source.items():
            if zone_id not in zone_view_data:
                zone_view_data[zone_id] = {}
            for m in measurements:
                if m.view not in zone_view_data[zone_id]:
                    zone_view_data[zone_id][m.view] = []
                zone_view_data[zone_id][m.view].append(m)

    # Frontal view engines
    sym_result = None
    prop_result = None
    aging_result = None
    if frontal:
        sym_result = symmetry_engine.analyze(
            frontal.detection, frontal.calibration, frontal.blendshapes or None,
        )
        _merge_zone_data(_extract_symmetry_zone_measurements(sym_result))

        prop_result = proportion_engine.analyze(frontal.detection, frontal.calibration)
        _merge_zone_data(_extract_proportion_zone_measurements(prop_result))

        aging_result = aging_engine.analyze(
            frontal.detection, frontal.calibration, frontal.blendshapes or None,
        )
        _merge_zone_data(_extract_aging_zone_measurements(aging_result))

    # Profile view engines
    prof_result = None
    if profile:
        prof_result = profile_engine.analyze(profile.detection, profile.calibration)
        _merge_zone_data(_extract_profile_zone_measurements(prof_result))

    # Oblique view engines
    vol_result = None
    if oblique:
        vol_result = volume_engine.analyze(oblique.detection, oblique.calibration)
        _merge_zone_data(_extract_volume_zone_measurements(vol_result))

    # ── Step 2: Multi-view fusion ──
    fusion: FusionResult = fuse_all_zones(zone_view_data, views_analyzed)

    # ── Step 3: Build zone results with findings and severity ──
    zone_results: list[ZoneResult] = []

    for fz in fusion.zones:
        zone_def = ZONES.get(fz.zone_id)
        if zone_def is None:
            continue

        # Convert fused measurements to ZoneMeasurement
        zone_measurements: list[ZoneMeasurement] = []
        for fm in fz.measurements:
            # Find reference range for deviation calculation
            ref = next(
                (r for r in zone_def.reference_ranges if r.metric_name == fm.metric_name),
                None,
            )
            dev_pct = None
            ideal_min = None
            ideal_max = None
            if ref:
                ideal_min = ref.ideal_min
                ideal_max = ref.ideal_max
                mid = (ref.ideal_min + ref.ideal_max) / 2
                if mid != 0:
                    dev_pct = round((fm.fused_value - mid) / abs(mid) * 100, 1)

            zone_measurements.append(ZoneMeasurement(
                name=fm.metric_name,
                value=round(fm.fused_value, 2),
                unit=fm.unit,
                ideal_min=ideal_min,
                ideal_max=ideal_max,
                deviation_pct=dev_pct,
            ))

        # Compute severity
        severity = _compute_zone_severity(zone_def, zone_measurements)

        # Generate findings
        findings = _generate_findings(
            zone_def, zone_measurements, severity, fz.primary_view,
        )

        # If severity is 0 but we have findings, use finding severity
        if severity == 0.0 and findings:
            severity = round(
                min(10.0, sum(f.severity_contribution for f in findings) / len(findings)),
                1,
            )

        # Determine calibration method from the primary view
        primary_input = {"frontal": frontal, "profile": profile, "oblique": oblique}.get(fz.primary_view)
        cal_method = primary_input.calibration.method if primary_input else "unknown"

        zone_results.append(ZoneResult(
            zone_id=fz.zone_id,
            zone_name=fz.zone_name,
            region=fz.region,
            severity=severity,
            findings=findings,
            measurements=zone_measurements,
            primary_view=fz.primary_view,
            confirmed_by=[v for v in fz.contributing_views if v != fz.primary_view],
            calibration_method=cal_method,
        ))

    # ── Step 4: Sort by severity (highest first) ──
    zone_results.sort(key=lambda z: z.severity, reverse=True)

    # ── Step 5: Compute aesthetic score ──
    aesthetic_score = compute_aesthetic_score(zone_results)

    # ── Step 6: Build global metrics ──
    symmetry_index = sym_result.global_symmetry_index if sym_result else 100.0
    thirds = {}
    golden_deviation = 0.0
    lip_ratio = None
    if prop_result:
        thirds = {
            "upper": prop_result.thirds.upper_ratio,
            "middle": prop_result.thirds.middle_ratio,
            "lower": prop_result.thirds.lower_ratio,
        }
        golden_deviation = prop_result.golden_ratio.deviation_pct
        lip_ratio = prop_result.lip.lip_ratio

    fifths = None
    if prop_result and prop_result.fifths:
        fifths = {f"segment_{i+1}": r for i, r in enumerate(prop_result.fifths.ratios)}

    global_metrics = GlobalMetrics(
        symmetry_index=symmetry_index,
        facial_thirds=thirds,
        facial_fifths=fifths,
        golden_ratio_deviation=golden_deviation,
        lip_ratio=lip_ratio,
        aesthetic_score=aesthetic_score,
    )

    # ── Step 7: Expression deviation ──
    expression_dev = 0.0
    if frontal:
        expression_dev = compute_expression_deviation(frontal.blendshapes)

    # ── Step 8: Calibration info (use frontal as primary) ──
    primary_cal = frontal.calibration if frontal else (profile.calibration if profile else oblique.calibration)  # type: ignore
    cal_info = CalibrationInfo(
        method=primary_cal.method,
        px_per_mm=primary_cal.px_per_mm,
        confidence=primary_cal.confidence,
        iris_width_px=primary_cal.iris_width_px,
        face_width_px=primary_cal.face_width_px,
    )

    return ZoneReport(
        zones=zone_results,
        global_metrics=global_metrics,
        calibration=cal_info,
        aesthetic_score=aesthetic_score,
        expression_deviation=expression_dev,
        views_analyzed=views_analyzed,
        fusion_contradictions=[c.description for c in fusion.contradictions],
    )
