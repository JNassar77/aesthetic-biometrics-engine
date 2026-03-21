"""
Contraindication checker — safety layer for treatment plan generation.

Evaluates zone analysis results for potential contraindications:
1. Extreme asymmetry (possible underlying pathology — refer to specialist)
2. Vascular risk zones with high severity (flag for caution)
3. Conflicting treatments (e.g., neurotoxin + filler in same muscle group)
4. Excessive total volume warnings

Does NOT replace clinical judgment — provides automated safety flags
that should be reviewed by the treating physician.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.models.zone_models import ZoneResult
from app.treatment.product_database import (
    is_high_risk_zone,
    get_vascular_risk,
    VASCULAR_RISK_ZONES,
)


class ContraindicationSeverity(str, Enum):
    WARNING = "warning"           # Proceed with caution
    CAUTION = "caution"           # Requires experienced injector
    REFERRAL = "referral"         # Consider specialist referral
    CONTRAINDICATED = "contraindicated"  # Do not treat this zone


@dataclass
class Contraindication:
    """A contraindication or safety flag."""
    severity: ContraindicationSeverity
    zone_id: str | None  # None for global contraindications
    code: str            # Machine-readable code
    message: str         # Human-readable description
    recommendation: str  # What to do about it


# ──────────────────────── Thresholds ────────────────────────

EXTREME_ASYMMETRY_THRESHOLD = 8.0   # Zone severity > 8 with asymmetry findings
PATHOLOGY_SEVERITY_THRESHOLD = 9.0  # May indicate underlying condition
HIGH_RISK_SEVERITY_THRESHOLD = 5.0  # Extra caution needed in vascular zones
EXCESSIVE_TOTAL_SEVERITY = 60.0     # Sum of all severities — global overtreatment risk


# ──────────────────────── Check Functions ────────────────────────

def _check_extreme_asymmetry(zones: list[ZoneResult]) -> list[Contraindication]:
    """Flag zones with extreme asymmetry that may indicate pathology."""
    results: list[Contraindication] = []

    for zone in zones:
        if zone.severity < EXTREME_ASYMMETRY_THRESHOLD:
            continue

        # Check if findings mention asymmetry
        has_asymmetry = any(
            "asymmetry" in f.description.lower() for f in zone.findings
        )
        if has_asymmetry:
            results.append(Contraindication(
                severity=ContraindicationSeverity.REFERRAL,
                zone_id=zone.zone_id,
                code="EXTREME_ASYMMETRY",
                message=(
                    f"Zone {zone.zone_id} ({zone.zone_name}) shows extreme asymmetry "
                    f"(severity {zone.severity:.1f}/10). This may indicate underlying "
                    f"pathology such as facial nerve palsy, skeletal asymmetry, or "
                    f"previous trauma."
                ),
                recommendation=(
                    "Consider specialist referral before aesthetic treatment. "
                    "Rule out pathological causes of asymmetry."
                ),
            ))

    return results


def _check_pathological_severity(zones: list[ZoneResult]) -> list[Contraindication]:
    """Flag zones with severity that suggests pathological rather than aesthetic issues."""
    results: list[Contraindication] = []

    for zone in zones:
        if zone.severity < PATHOLOGY_SEVERITY_THRESHOLD:
            continue

        results.append(Contraindication(
            severity=ContraindicationSeverity.CAUTION,
            zone_id=zone.zone_id,
            code="HIGH_SEVERITY",
            message=(
                f"Zone {zone.zone_id} ({zone.zone_name}) has very high severity "
                f"({zone.severity:.1f}/10). Measurements significantly deviate from "
                f"normal ranges."
            ),
            recommendation=(
                "Verify measurements manually. Consider whether aesthetic treatment "
                "alone is appropriate or if surgical/orthodontic intervention is indicated."
            ),
        ))

    return results


def _check_vascular_risk(zones: list[ZoneResult]) -> list[Contraindication]:
    """Flag high-risk vascular zones that need experienced injectors."""
    results: list[Contraindication] = []

    for zone in zones:
        if not is_high_risk_zone(zone.zone_id):
            continue
        if zone.severity < HIGH_RISK_SEVERITY_THRESHOLD:
            continue

        vessels = get_vascular_risk(zone.zone_id)
        vessel_str = ", ".join(vessels)

        results.append(Contraindication(
            severity=ContraindicationSeverity.CAUTION,
            zone_id=zone.zone_id,
            code="VASCULAR_RISK",
            message=(
                f"Zone {zone.zone_id} ({zone.zone_name}) requires treatment in a "
                f"vascular risk area. Relevant vessels: {vessel_str}."
            ),
            recommendation=(
                "Use blunt cannula where possible. Aspirate before injection. "
                "Have hyaluronidase available. Treatment should be performed by "
                "an experienced injector."
            ),
        ))

    return results


def _check_tear_trough_special(zones: list[ZoneResult]) -> list[Contraindication]:
    """Special tear trough contraindication checks."""
    results: list[Contraindication] = []

    tt_zone = next((z for z in zones if z.zone_id == "Tt1"), None)
    if tt_zone is None or tt_zone.severity < 1.0:
        return results

    # Check if severity is high — tear trough is very technique-sensitive
    if tt_zone.severity >= 6.0:
        results.append(Contraindication(
            severity=ContraindicationSeverity.CAUTION,
            zone_id="Tt1",
            code="TEAR_TROUGH_DEEP",
            message=(
                "Deep tear trough deformity detected. HA filler in this area "
                "carries risk of Tyndall effect, lymphatic obstruction, and "
                "vascular compromise."
            ),
            recommendation=(
                "Consider addressing midface volume (Ck2/Ck3) first — this "
                "often reduces tear trough depth significantly. If direct "
                "treatment needed, use blunt cannula and conservative volumes "
                "(max 0.1-0.2ml per side per session)."
            ),
        ))

    return results


def _check_overtreatment_risk(zones: list[ZoneResult]) -> list[Contraindication]:
    """Flag if total treatment scope is excessive for one plan."""
    results: list[Contraindication] = []

    total_severity = sum(z.severity for z in zones)
    treatable_zones = sum(1 for z in zones if z.severity >= 1.0)

    if total_severity > EXCESSIVE_TOTAL_SEVERITY:
        results.append(Contraindication(
            severity=ContraindicationSeverity.WARNING,
            zone_id=None,
            code="OVERTREATMENT_RISK",
            message=(
                f"Total severity across {treatable_zones} zones is {total_severity:.0f}. "
                f"Treating all zones simultaneously may lead to unnatural results."
            ),
            recommendation=(
                "Prioritize structural zones in session 1. Reassess after initial "
                "treatment before addressing additional zones. Consider a staged "
                "approach over 3-4 sessions."
            ),
        ))

    return results


def _check_glabella_forehead_dependency(
    zones: list[ZoneResult],
) -> list[Contraindication]:
    """Check for glabella-forehead neurotoxin dependency."""
    results: list[Contraindication] = []

    bw2 = next((z for z in zones if z.zone_id == "Bw2"), None)
    fo1 = next((z for z in zones if z.zone_id == "Fo1"), None)

    # If forehead treatment is indicated but glabella is not, warn
    if fo1 and fo1.severity >= 3.0 and (bw2 is None or bw2.severity < 1.0):
        results.append(Contraindication(
            severity=ContraindicationSeverity.WARNING,
            zone_id="Fo1",
            code="FOREHEAD_WITHOUT_GLABELLA",
            message=(
                "Forehead neurotoxin indicated but glabella (Bw2) does not show "
                "significant findings. Treating frontalis without corrugator/procerus "
                "can cause brow ptosis."
            ),
            recommendation=(
                "Always include glabella treatment when treating forehead. "
                "Consider lower forehead doses if brow position is already low."
            ),
        ))

    return results


# ──────────────────────── Main Check Function ────────────────────────

def check_contraindications(zones: list[ZoneResult]) -> list[Contraindication]:
    """Run all contraindication checks on zone results.

    Args:
        zones: List of ZoneResult from zone_analyzer.analyze().

    Returns:
        List of Contraindication objects, sorted by severity (most severe first).
    """
    results: list[Contraindication] = []

    results.extend(_check_extreme_asymmetry(zones))
    results.extend(_check_pathological_severity(zones))
    results.extend(_check_vascular_risk(zones))
    results.extend(_check_tear_trough_special(zones))
    results.extend(_check_overtreatment_risk(zones))
    results.extend(_check_glabella_forehead_dependency(zones))

    # Sort: CONTRAINDICATED > REFERRAL > CAUTION > WARNING
    severity_order = {
        ContraindicationSeverity.CONTRAINDICATED: 0,
        ContraindicationSeverity.REFERRAL: 1,
        ContraindicationSeverity.CAUTION: 2,
        ContraindicationSeverity.WARNING: 3,
    }
    results.sort(key=lambda c: severity_order.get(c.severity, 4))

    return results
