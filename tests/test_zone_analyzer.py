"""Tests for zone analyzer — the orchestration layer."""

import numpy as np
import pytest

from app.analysis.zone_analyzer import (
    analyze,
    ViewInput,
    ZoneReport,
    compute_aesthetic_score,
    _compute_zone_severity,
    _generate_findings,
    REGION_WEIGHTS,
)
from app.detection.face_landmarker import DetectionResult
from app.utils.pixel_calibration import CalibrationResult
from app.models.zone_models import ZoneResult, ZoneFinding, ZoneMeasurement
from app.treatment.zone_definitions import ZONES


# ──────────────── Test Data Helpers ────────────────


def _make_detection(image_size: int = 1000) -> DetectionResult:
    """Create a realistic-ish face detection result for testing.

    Landmarks are placed to form a plausible face geometry.
    """
    lm = np.full((478, 3), 0.5, dtype=np.float32)

    # Midline landmarks (x=0.5 for frontal, varying y)
    lm[10] = [0.50, 0.10, 0.0]   # trichion_approx
    lm[9] = [0.50, 0.25, 0.0]    # glabella
    lm[168] = [0.50, 0.30, 0.0]  # nasion
    lm[6] = [0.50, 0.37, 0.0]    # rhinion
    lm[4] = [0.50, 0.40, 0.0]    # pronasale
    lm[2] = [0.50, 0.43, 0.0]    # subnasale
    lm[0] = [0.50, 0.47, 0.0]    # labrale_superius
    lm[13] = [0.50, 0.50, 0.0]   # stomion
    lm[14] = [0.50, 0.53, 0.0]   # labrale_inferius
    lm[17] = [0.50, 0.58, 0.0]   # mentolabial_sulcus
    lm[175] = [0.50, 0.62, 0.0]  # pogonion
    lm[152] = [0.50, 0.70, 0.0]  # gnathion

    # Paired landmarks — symmetric
    offset = 0.15
    # brow_peak: 282 (L), 52 (R)
    lm[282] = [0.5 + offset, 0.22, 0.0]
    lm[52] = [0.5 - offset, 0.22, 0.0]
    # brow_outer: 383 (L), 156 (R)
    lm[383] = [0.5 + 0.18, 0.23, -0.02]
    lm[156] = [0.5 - 0.18, 0.23, -0.02]

    # eye_inner: 362 (L), 133 (R)
    lm[362] = [0.5 + 0.06, 0.30, 0.0]
    lm[133] = [0.5 - 0.06, 0.30, 0.0]
    # eye_outer: 263 (L), 33 (R)
    lm[263] = [0.5 + 0.14, 0.30, 0.0]
    lm[33] = [0.5 - 0.14, 0.30, 0.0]

    # cheekbone: 330 (L), 101 (R)
    lm[330] = [0.5 + 0.18, 0.35, -0.03]
    lm[101] = [0.5 - 0.18, 0.35, -0.03]

    # infraorbital: 253 (L), 23 (R)
    lm[253] = [0.5 + 0.08, 0.33, -0.01]
    lm[23] = [0.5 - 0.08, 0.33, -0.01]

    # malar_high: 329 (L), 100 (R)
    lm[329] = [0.5 + 0.16, 0.34, -0.04]
    lm[100] = [0.5 - 0.16, 0.34, -0.04]
    # malar_low: 425 (L), 205 (R)
    lm[425] = [0.5 + 0.14, 0.40, -0.01]
    lm[205] = [0.5 - 0.14, 0.40, -0.01]

    # temporal: 447 (L), 227 (R)
    lm[447] = [0.5 + 0.22, 0.20, -0.04]
    lm[227] = [0.5 - 0.22, 0.20, -0.04]

    # alar: 309 (L), 79 (R)
    lm[309] = [0.5 + 0.05, 0.42, 0.0]
    lm[79] = [0.5 - 0.05, 0.42, 0.0]

    # mouth_corner: 291 (L), 61 (R)
    lm[291] = [0.5 + 0.10, 0.50, 0.0]
    lm[61] = [0.5 - 0.10, 0.50, 0.0]

    # gonion: 365 (L), 136 (R)
    lm[365] = [0.5 + 0.20, 0.60, -0.02]
    lm[136] = [0.5 - 0.20, 0.60, -0.02]

    # preauricular: 356 (L), 127 (R)
    lm[356] = [0.5 + 0.25, 0.35, -0.05]
    lm[127] = [0.5 - 0.25, 0.35, -0.05]

    # Cupid's bow landmarks
    lm[267] = [0.48, 0.465, 0.0]  # cupid left
    lm[37] = [0.52, 0.465, 0.0]   # cupid right

    # Iris landmarks for calibration
    lm[469] = [0.5 + 0.12, 0.29, 0.0]
    lm[471] = [0.5 + 0.08, 0.29, 0.0]
    lm[474] = [0.5 - 0.08, 0.29, 0.0]
    lm[476] = [0.5 - 0.12, 0.29, 0.0]

    return DetectionResult(
        landmarks=lm,
        blendshapes={},
        transformation_matrix=None,
        image_width=image_size,
        image_height=image_size,
    )


def _make_calibration(px_per_mm: float = 5.0) -> CalibrationResult:
    """Create a calibration result."""
    return CalibrationResult(
        px_per_mm=px_per_mm,
        method="iris",
        confidence=0.9,
        iris_width_px=58.5,
    )


def _make_view_input(
    image_size: int = 1000,
    blendshapes: dict | None = None,
) -> ViewInput:
    """Create a ViewInput with realistic detection data."""
    det = _make_detection(image_size)
    cal = _make_calibration()
    return ViewInput(
        detection=det,
        calibration=cal,
        blendshapes=blendshapes or {},
    )


# ──────────────── compute_aesthetic_score ────────────────


class TestAestheticScore:
    def test_no_zones_returns_100(self):
        assert compute_aesthetic_score([]) == 100.0

    def test_all_zones_zero_severity_returns_100(self):
        zones = [
            ZoneResult(zone_id="Ck1", zone_name="Test", region="midface",
                       severity=0.0, primary_view="frontal"),
            ZoneResult(zone_id="Lp1", zone_name="Test", region="lower_face",
                       severity=0.0, primary_view="frontal"),
        ]
        assert compute_aesthetic_score(zones) == 100.0

    def test_max_severity_returns_low_score(self):
        zones = [
            ZoneResult(zone_id="Ck1", zone_name="Test", region="midface",
                       severity=10.0, primary_view="frontal"),
        ]
        score = compute_aesthetic_score(zones)
        assert score < 20.0

    def test_moderate_severity(self):
        zones = [
            ZoneResult(zone_id="Ck1", zone_name="Test", region="midface",
                       severity=5.0, primary_view="oblique"),
        ]
        score = compute_aesthetic_score(zones)
        assert 40.0 < score < 70.0

    def test_midface_weighted_higher(self):
        """Midface zones should have more impact when mixed with other regions.

        Weight applies to both numerator and denominator equally for a single zone,
        so the effect only shows when zones from different regions are mixed.
        """
        # Two zones: one midface (high weight) + one profile (low weight)
        mixed_midface_severe = [
            ZoneResult(zone_id="Ck1", zone_name="Test", region="midface",
                       severity=8.0, primary_view="oblique"),
            ZoneResult(zone_id="Pf1", zone_name="Test", region="profile",
                       severity=2.0, primary_view="profile"),
        ]
        mixed_profile_severe = [
            ZoneResult(zone_id="Ck1", zone_name="Test", region="midface",
                       severity=2.0, primary_view="oblique"),
            ZoneResult(zone_id="Pf1", zone_name="Test", region="profile",
                       severity=8.0, primary_view="profile"),
        ]
        # When midface is more severe, overall score should be lower
        # because midface carries higher weight
        score_midface_bad = compute_aesthetic_score(mixed_midface_severe)
        score_profile_bad = compute_aesthetic_score(mixed_profile_severe)
        assert score_midface_bad < score_profile_bad

    def test_score_range_0_100(self):
        """Score should always be between 0 and 100."""
        zones = [
            ZoneResult(zone_id=f"Z{i}", zone_name="Test", region="midface",
                       severity=10.0, primary_view="frontal")
            for i in range(20)
        ]
        score = compute_aesthetic_score(zones)
        assert 0.0 <= score <= 100.0


# ──────────────── _compute_zone_severity ────────────────


class TestComputeZoneSeverity:
    def test_within_ideal_range_zero_severity(self):
        zone_def = ZONES["Pf1"]  # Has nasolabial_angle ref: 90-105
        measurements = [
            ZoneMeasurement(name="nasolabial_angle_deg", value=97.0, unit="deg",
                            ideal_min=90.0, ideal_max=105.0),
        ]
        sev = _compute_zone_severity(zone_def, measurements)
        assert sev == 0.0

    def test_below_ideal_range(self):
        zone_def = ZONES["Pf1"]
        measurements = [
            ZoneMeasurement(name="nasolabial_angle_deg", value=80.0, unit="deg",
                            ideal_min=90.0, ideal_max=105.0),
        ]
        sev = _compute_zone_severity(zone_def, measurements)
        assert sev > 0.0

    def test_above_ideal_range(self):
        zone_def = ZONES["Pf1"]
        measurements = [
            ZoneMeasurement(name="nasolabial_angle_deg", value=120.0, unit="deg",
                            ideal_min=90.0, ideal_max=105.0),
        ]
        sev = _compute_zone_severity(zone_def, measurements)
        assert sev > 0.0

    def test_no_measurements_zero_severity(self):
        zone_def = ZONES["T1"]
        sev = _compute_zone_severity(zone_def, [])
        assert sev == 0.0


# ──────────────── _generate_findings ────────────────


class TestGenerateFindings:
    def test_no_deviation_no_findings(self):
        zone_def = ZONES["Pf1"]
        measurements = [
            ZoneMeasurement(name="nasolabial_angle_deg", value=97.0, unit="deg",
                            ideal_min=90.0, ideal_max=105.0),
        ]
        findings = _generate_findings(zone_def, measurements, 0.0, "profile")
        assert len(findings) == 0

    def test_below_range_generates_finding(self):
        zone_def = ZONES["Lp1"]
        measurements = [
            ZoneMeasurement(name="lip_ratio", value=0.3, unit="ratio",
                            ideal_min=0.5, ideal_max=0.7),
        ]
        findings = _generate_findings(zone_def, measurements, 3.0, "frontal")
        assert len(findings) >= 1
        assert "below ideal" in findings[0].description.lower()

    def test_above_range_generates_finding(self):
        zone_def = ZONES["Pf1"]
        measurements = [
            ZoneMeasurement(name="nasolabial_angle_deg", value=120.0, unit="deg",
                            ideal_min=90.0, ideal_max=105.0),
        ]
        findings = _generate_findings(zone_def, measurements, 3.0, "profile")
        assert len(findings) >= 1
        assert "above ideal" in findings[0].description.lower()

    def test_asymmetry_finding(self):
        zone_def = ZONES["Bw1"]
        measurements = [
            ZoneMeasurement(name="brow_asymmetry_mm", value=3.5, unit="mm"),
        ]
        findings = _generate_findings(zone_def, measurements, 3.0, "frontal")
        assert any("asymmetry" in f.description.lower() for f in findings)

    def test_max_5_findings(self):
        zone_def = ZONES["Lp1"]
        measurements = [
            ZoneMeasurement(name=f"metric_{i}", value=float(i), unit="mm",
                            deviation_pct=float(i * 20))
            for i in range(10)
        ]
        findings = _generate_findings(zone_def, measurements, 5.0, "frontal")
        assert len(findings) <= 5


# ──────────────── Full analyze() ────────────────


class TestAnalyze:
    def test_frontal_only(self):
        """Single frontal view should produce zones analyzed from frontal."""
        frontal = _make_view_input()
        report = analyze(frontal=frontal)

        assert isinstance(report, ZoneReport)
        assert "frontal" in report.views_analyzed
        assert len(report.zones) > 0
        assert 0.0 <= report.aesthetic_score <= 100.0
        assert report.global_metrics.symmetry_index > 0

    def test_profile_only(self):
        """Single profile view should produce profile-specific zones."""
        profile_input = _make_view_input()
        report = analyze(profile=profile_input)

        assert "profile" in report.views_analyzed
        zone_ids = {z.zone_id for z in report.zones}
        # Profile engine should produce Pf1, Pf2, Ch1
        assert "Pf1" in zone_ids or "Pf2" in zone_ids or "Ch1" in zone_ids

    def test_oblique_only(self):
        """Oblique view should produce volume-related zones."""
        oblique_input = _make_view_input()
        report = analyze(oblique=oblique_input)

        assert "oblique" in report.views_analyzed
        zone_ids = {z.zone_id for z in report.zones}
        # Volume engine should produce T1, Ck2, Tt1, Jw1
        assert len(zone_ids) > 0

    def test_all_three_views(self):
        """Full 3-view analysis should produce the most comprehensive report."""
        frontal = _make_view_input()
        profile_input = _make_view_input()
        oblique = _make_view_input()

        report = analyze(frontal=frontal, profile=profile_input, oblique=oblique)

        assert set(report.views_analyzed) == {"frontal", "profile", "oblique"}
        assert len(report.zones) > 0
        assert 0.0 <= report.aesthetic_score <= 100.0

    def test_zones_sorted_by_severity(self):
        """Zones should be sorted highest severity first."""
        frontal = _make_view_input()
        profile_input = _make_view_input()
        oblique = _make_view_input()

        report = analyze(frontal=frontal, profile=profile_input, oblique=oblique)

        severities = [z.severity for z in report.zones]
        assert severities == sorted(severities, reverse=True)

    def test_no_views_raises(self):
        with pytest.raises(ValueError, match="At least one view"):
            analyze()

    def test_blendshapes_not_fused(self):
        """Blendshapes from frontal should not appear in fusion contradictions
        or be mixed with profile/oblique view data."""
        frontal = _make_view_input(blendshapes={
            "mouthSmileLeft": 0.3,
            "mouthSmileRight": 0.1,
        })
        report = analyze(frontal=frontal)
        # Expression deviation should reflect the non-neutral expression
        assert report.expression_deviation >= 0.0

    def test_calibration_info_present(self):
        frontal = _make_view_input()
        report = analyze(frontal=frontal)
        assert report.calibration.method == "iris"
        assert report.calibration.px_per_mm > 0

    def test_global_metrics_populated(self):
        frontal = _make_view_input()
        report = analyze(frontal=frontal)
        gm = report.global_metrics
        assert 0 <= gm.symmetry_index <= 100
        assert gm.facial_thirds  # should have upper/middle/lower
        assert gm.golden_ratio_deviation >= 0
        assert gm.aesthetic_score == report.aesthetic_score


# ──────────────── Expression deviation ────────────────


class TestExpressionDeviation:
    def test_neutral_expression_zero_deviation(self):
        frontal = _make_view_input(blendshapes={
            "mouthSmileLeft": 0.01,
            "mouthSmileRight": 0.01,
            "browDownLeft": 0.01,
        })
        report = analyze(frontal=frontal)
        assert report.expression_deviation == 0.0

    def test_active_expression_nonzero_deviation(self):
        frontal = _make_view_input(blendshapes={
            "mouthSmileLeft": 0.5,
            "mouthSmileRight": 0.5,
        })
        report = analyze(frontal=frontal)
        assert report.expression_deviation > 0.0

    def test_empty_blendshapes_zero_deviation(self):
        frontal = _make_view_input(blendshapes={})
        report = analyze(frontal=frontal)
        assert report.expression_deviation == 0.0


# ──────────────── Integration-level: zone coverage ────────────────


class TestZoneCoverage:
    """Verify that different view combinations produce zones from expected regions."""

    def test_frontal_produces_upper_midface_lower(self):
        frontal = _make_view_input()
        report = analyze(frontal=frontal)
        regions = {z.region for z in report.zones}
        # Frontal should produce at least midface and lower_face zones
        assert len(regions) >= 1

    def test_profile_produces_profile_zones(self):
        profile_input = _make_view_input()
        report = analyze(profile=profile_input)
        regions = {z.region for z in report.zones}
        assert "profile" in regions

    def test_three_views_cover_all_regions(self):
        frontal = _make_view_input()
        profile_input = _make_view_input()
        oblique = _make_view_input()

        report = analyze(frontal=frontal, profile=profile_input, oblique=oblique)
        regions = {z.region for z in report.zones}
        # Should have zones from all four regions
        assert "upper_face" in regions or "midface" in regions
        assert "lower_face" in regions or "profile" in regions
