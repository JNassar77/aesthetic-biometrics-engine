"""Tests for treatment zone definitions."""

import pytest

from app.treatment.zone_definitions import (
    ZONES,
    Region,
    ViewPriority,
    get_zone,
    all_zone_ids,
    zones_for_view,
    zones_needing_fusion,
    zones_by_region,
)


class TestZoneRegistry:
    def test_all_19_zones_defined(self):
        """19 zones: 16 original + Fo1, Pf2, Pf3."""
        assert len(ZONES) == 19

    def test_all_zone_ids_returns_all(self):
        ids = all_zone_ids()
        assert len(ids) == 19
        assert "Ck2" in ids
        assert "Lp1" in ids
        assert "Pf1" in ids

    def test_get_zone_exists(self):
        zone = get_zone("Ck2")
        assert zone is not None
        assert zone.zone_name == "Zygomatic Eminence"

    def test_get_zone_nonexistent(self):
        assert get_zone("XX9") is None

    def test_every_zone_has_region(self):
        for z in ZONES.values():
            assert z.region in Region

    def test_every_zone_has_primary_view(self):
        for z in ZONES.values():
            assert z.primary_view in ViewPriority

    def test_expected_zone_ids(self):
        expected = {
            "T1", "Bw1", "Bw2", "Fo1",
            "Ck1", "Ck2", "Ck3", "Tt1", "Ns1",
            "Lp1", "Lp2", "Lp3", "Mn1", "Jw1", "Ch1", "Jl1",
            "Pf1", "Pf2", "Pf3",
        }
        assert set(ZONES.keys()) == expected


class TestViewFiltering:
    def test_frontal_zones(self):
        frontal = zones_for_view("frontal")
        ids = {z.zone_id for z in frontal}
        assert "Bw1" in ids  # primary
        assert "Lp1" in ids  # primary
        assert "Ch1" in ids  # secondary

    def test_profile_zones(self):
        profile = zones_for_view("profile")
        ids = {z.zone_id for z in profile}
        assert "Pf1" in ids  # primary
        assert "Pf2" in ids
        assert "Ch1" in ids  # primary
        assert "Jl1" in ids  # primary

    def test_oblique_zones(self):
        oblique = zones_for_view("oblique")
        ids = {z.zone_id for z in oblique}
        assert "T1" in ids   # primary
        assert "Ck1" in ids  # primary
        assert "Ck2" in ids  # primary


class TestFusion:
    def test_fusion_zones_exist(self):
        fusion = zones_needing_fusion()
        assert len(fusion) > 5  # Many zones need fusion
        ids = {z.zone_id for z in fusion}
        assert "Ck2" in ids
        assert "Lp1" in ids
        assert "Ns1" in ids

    def test_profile_only_zones_not_fused(self):
        fusion = zones_needing_fusion()
        ids = {z.zone_id for z in fusion}
        assert "Pf1" not in ids  # profile-only, no fusion
        assert "Pf2" not in ids
        assert "Pf3" not in ids


class TestRegionGrouping:
    def test_upper_face(self):
        upper = zones_by_region(Region.UPPER_FACE)
        ids = {z.zone_id for z in upper}
        assert ids == {"T1", "Bw1", "Bw2", "Fo1"}

    def test_midface(self):
        mid = zones_by_region(Region.MIDFACE)
        ids = {z.zone_id for z in mid}
        assert "Ck1" in ids
        assert "Ns1" in ids
        assert "Tt1" in ids

    def test_profile(self):
        prof = zones_by_region(Region.PROFILE)
        ids = {z.zone_id for z in prof}
        assert ids == {"Pf1", "Pf2", "Pf3"}


class TestReferenceRanges:
    def test_lip_zone_has_reference_ranges(self):
        lp1 = get_zone("Lp1")
        assert lp1 is not None
        assert len(lp1.reference_ranges) >= 2
        names = {r.metric_name for r in lp1.reference_ranges}
        assert "lip_ratio" in names
        assert "upper_lip_height_mm" in names

    def test_nasal_profile_has_angles(self):
        pf1 = get_zone("Pf1")
        assert pf1 is not None
        names = {r.metric_name for r in pf1.reference_ranges}
        assert "nasolabial_angle_deg" in names

    def test_severity_weights_sum_to_one(self):
        """All severity weight dictionaries should sum to approximately 1.0."""
        for zone in ZONES.values():
            if zone.severity_weights:
                total = sum(zone.severity_weights.values())
                assert abs(total - 1.0) < 0.01, (
                    f"Zone {zone.zone_id} severity weights sum to {total}"
                )
