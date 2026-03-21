"""Tests for the product database — clinical knowledge base."""

import pytest

from app.treatment.product_database import (
    PRODUCTS,
    ZONE_RECOMMENDATIONS,
    NEUROTOXIN_INDICATIONS,
    VASCULAR_RISK_ZONES,
    STRUCTURAL_PRIORITY,
    ProductCategory,
    InjectionTechnique,
    InjectionDepth,
    get_product,
    get_zone_recommendations,
    get_neurotoxin_indications,
    get_vascular_risk,
    get_structural_priority,
    products_for_category,
    is_high_risk_zone,
)
from app.treatment.zone_definitions import ZONES


class TestProductCatalog:
    def test_catalog_not_empty(self):
        assert len(PRODUCTS) >= 10

    def test_every_product_has_name_and_brand(self):
        for key, p in PRODUCTS.items():
            assert p.name, f"{key} missing name"
            assert p.brand, f"{key} missing brand"

    def test_every_product_has_category(self):
        for key, p in PRODUCTS.items():
            assert isinstance(p.category, ProductCategory)

    def test_ha_deep_products_have_high_g_prime(self):
        for p in products_for_category(ProductCategory.HA_DEEP):
            assert p.g_prime is not None and p.g_prime >= 200, (
                f"{p.name} is HA_DEEP but G' is {p.g_prime}"
            )

    def test_ha_soft_products_have_low_g_prime(self):
        for p in products_for_category(ProductCategory.HA_SOFT):
            assert p.g_prime is not None and p.g_prime < 200, (
                f"{p.name} is HA_SOFT but G' is {p.g_prime}"
            )

    def test_neurotoxin_products_exist(self):
        toxins = products_for_category(ProductCategory.NEUROTOXIN)
        assert len(toxins) >= 3
        names = {p.name for p in toxins}
        assert "Botox" in names
        assert "Dysport" in names

    def test_skin_boosters_exist(self):
        boosters = products_for_category(ProductCategory.SKIN_BOOSTER)
        assert len(boosters) >= 2

    def test_get_product_existing(self):
        p = get_product("juvederm_voluma")
        assert p is not None
        assert p.name == "Juvederm Voluma"
        assert p.category == ProductCategory.HA_DEEP

    def test_get_product_nonexistent(self):
        assert get_product("nonexistent") is None

    def test_duration_months_range_valid(self):
        for key, p in PRODUCTS.items():
            lo, hi = p.duration_months
            assert lo <= hi, f"{key} has invalid duration range"
            assert lo >= 0


class TestZoneRecommendations:
    def test_all_19_zones_have_structural_priority(self):
        for zone_id in ZONES:
            assert zone_id in STRUCTURAL_PRIORITY, (
                f"Zone {zone_id} missing from STRUCTURAL_PRIORITY"
            )

    def test_recommendations_cover_key_zones(self):
        """Key zones must have at least one product recommendation."""
        key_zones = ["Ck2", "Lp1", "Ch1", "Ns1", "Tt1", "Jl1"]
        for zone_id in key_zones:
            recs = get_zone_recommendations(zone_id)
            assert len(recs) >= 1, f"Zone {zone_id} has no recommendations"

    def test_recommendation_volume_ranges_valid(self):
        for zone_id, recs in ZONE_RECOMMENDATIONS.items():
            for r in recs:
                lo, hi = r.volume_range_ml
                assert 0 < lo <= hi, (
                    f"Zone {zone_id} rec has invalid volume range ({lo}, {hi})"
                )

    def test_recommendation_has_products(self):
        for zone_id, recs in ZONE_RECOMMENDATIONS.items():
            for r in recs:
                assert len(r.products) >= 1

    def test_recommendation_has_techniques(self):
        for zone_id, recs in ZONE_RECOMMENDATIONS.items():
            for r in recs:
                assert len(r.techniques) >= 1

    def test_midface_uses_deep_fillers(self):
        """Midface structural zones should recommend high G' products."""
        ck2_recs = get_zone_recommendations("Ck2")
        categories = {r.category for r in ck2_recs}
        assert ProductCategory.HA_DEEP in categories

    def test_lip_uses_soft_fillers(self):
        """Lip zones should recommend soft HA products."""
        lp1_recs = get_zone_recommendations("Lp1")
        categories = {r.category for r in lp1_recs}
        assert ProductCategory.HA_SOFT in categories

    def test_empty_zone_returns_empty(self):
        assert get_zone_recommendations("XX9") == []


class TestNeurotoxinIndications:
    def test_glabella_has_neurotoxin(self):
        inds = get_neurotoxin_indications("Bw2")
        assert len(inds) >= 1
        assert "Corrugator" in inds[0].target_muscle or "Procerus" in inds[0].target_muscle

    def test_forehead_has_neurotoxin(self):
        inds = get_neurotoxin_indications("Fo1")
        assert len(inds) >= 1
        assert "Frontalis" in inds[0].target_muscle

    def test_dose_ranges_valid(self):
        for zone_id, inds in NEUROTOXIN_INDICATIONS.items():
            for ind in inds:
                lo, hi = ind.dose_range_units
                assert 0 < lo <= hi, f"Zone {zone_id} has invalid dose range"

    def test_lip_flip_low_dose(self):
        """Lip flip should use very low neurotoxin doses."""
        lp1_inds = get_neurotoxin_indications("Lp1")
        if lp1_inds:
            assert lp1_inds[0].dose_range_units[1] <= 10

    def test_empty_zone_returns_empty(self):
        assert get_neurotoxin_indications("Ck2") == []


class TestVascularRisk:
    def test_tear_trough_is_high_risk(self):
        assert is_high_risk_zone("Tt1")
        risk = get_vascular_risk("Tt1")
        assert len(risk) >= 1

    def test_nasal_profile_is_high_risk(self):
        assert is_high_risk_zone("Pf1")

    def test_forehead_not_high_risk(self):
        assert not is_high_risk_zone("Fo1")

    def test_nonexistent_zone_not_high_risk(self):
        assert not is_high_risk_zone("XX9")
        assert get_vascular_risk("XX9") == ()


class TestStructuralPriority:
    def test_midface_structural_comes_first(self):
        """Ck1 and Ck2 should have priority 1 (treat first)."""
        assert get_structural_priority("Ck1") == 1
        assert get_structural_priority("Ck2") == 1

    def test_detail_zones_come_last(self):
        """Lip and neurotoxin zones should have priority 5."""
        assert get_structural_priority("Lp1") == 5
        assert get_structural_priority("Fo1") == 5

    def test_structural_before_detail(self):
        """All structural zones should have lower priority number than detail zones."""
        structural = get_structural_priority("Ck2")
        detail = get_structural_priority("Lp1")
        assert structural < detail

    def test_nonexistent_zone_default(self):
        assert get_structural_priority("XX9") == 5
