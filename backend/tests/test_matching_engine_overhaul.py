"""
COMPAREX Backend – Comprehensive Test Suite for Product Matching & Marketplace Accuracy Overhaul
"""

import pytest
from app.services.matching_engine import ExactProductMatchEngine
from app.services.search_engine import SearchEngineService, SearchIntent


class DummyProduct:
    """Mock product ORM instance for testing search relevance engine."""

    def __init__(
        self,
        name: str,
        brand: str,
        category: str,
        popularity_score: float = 80.0,
        rating: float = 4.5,
        is_quarantined: bool = False,
    ):
        self.name = name
        self.brand = brand
        self.category = category
        self.popularity_score = popularity_score
        self.rating = rating
        self.is_quarantined = is_quarantined


def test_iphone15_search_relevance_isolation():
    """
    Search query: 'iPhone 15'
    Must match: Apple iPhone 15 128GB, Apple iPhone 15 256GB
    Must EXCLUDE: iPhone 16, iPhone 14, iPhone 15 Pro, iPhone 15 Pro Max, iPad, MacBook, AirPods, Watch, Cases
    """
    valid_base1 = DummyProduct("Apple iPhone 15 (128 GB) - Blue", "Apple", "Mobiles")
    valid_base2 = DummyProduct("Apple iPhone 15 (256 GB) - Black", "Apple", "Mobiles")

    wrong_model16 = DummyProduct("Apple iPhone 16 (128 GB) - Teal", "Apple", "Mobiles")
    wrong_model14 = DummyProduct("Apple iPhone 14 (128 GB) - Midnight", "Apple", "Mobiles")
    wrong_variant_pro = DummyProduct("Apple iPhone 15 Pro (128 GB) - Natural Titanium", "Apple", "Mobiles")
    wrong_variant_promax = DummyProduct("Apple iPhone 15 Pro Max (256 GB) - Black Titanium", "Apple", "Mobiles")
    wrong_family_ipad = DummyProduct("Apple iPad Air 10.9 inch", "Apple", "Tablets")
    wrong_family_macbook = DummyProduct("Apple MacBook Air M4", "Apple", "Laptops")
    wrong_family_airpods = DummyProduct("Apple AirPods Pro (2nd Gen)", "Apple", "Headphones")
    wrong_family_watch = DummyProduct("Apple Watch Series 9", "Apple", "Smartwatches")
    wrong_accessory = DummyProduct("Spigen Silicone Case for iPhone 15", "Spigen", "Accessories")

    candidates = [
        valid_base1,
        valid_base2,
        wrong_model16,
        wrong_model14,
        wrong_variant_pro,
        wrong_variant_promax,
        wrong_family_ipad,
        wrong_family_macbook,
        wrong_family_airpods,
        wrong_family_watch,
        wrong_accessory,
    ]

    results = SearchEngineService.filter_and_rank_products(
        products=candidates,
        raw_query="iPhone 15",
        min_threshold=40.0,
    )

    result_names = [p.name for p in results]

    # Verify valid base products are returned
    assert valid_base1 in results
    assert valid_base2 in results

    # Verify all non-matching models, variants, families, and accessories are EXCLUDED
    assert wrong_model16 not in results
    assert wrong_model14 not in results
    assert wrong_variant_pro not in results
    assert wrong_variant_promax not in results
    assert wrong_family_ipad not in results
    assert wrong_family_macbook not in results
    assert wrong_family_airpods not in results
    assert wrong_family_watch not in results
    assert wrong_accessory not in results


def test_samsung_galaxy_s25_ultra_relevance_isolation():
    """
    Search query: 'Samsung Galaxy S25 Ultra'
    Must match: Samsung Galaxy S25 Ultra (512 GB)
    Must EXCLUDE: Samsung Galaxy S25, Samsung Galaxy S25+, Samsung Galaxy S24 Ultra, Galaxy A15, Case
    """
    valid_ultra = DummyProduct("Samsung Galaxy S25 Ultra 5G (512 GB) - Titanium Gray", "Samsung", "Mobiles")
    wrong_base = DummyProduct("Samsung Galaxy S25 5G (128 GB)", "Samsung", "Mobiles")
    wrong_plus = DummyProduct("Samsung Galaxy S25+ 5G (256 GB)", "Samsung", "Mobiles")
    wrong_s24_ultra = DummyProduct("Samsung Galaxy S24 Ultra 5G (256 GB)", "Samsung", "Mobiles")
    wrong_a15 = DummyProduct("Samsung Galaxy A15 5G", "Samsung", "Mobiles")
    wrong_case = DummyProduct("Spigen Armor Case for Galaxy S25 Ultra", "Spigen", "Accessories")

    candidates = [valid_ultra, wrong_base, wrong_plus, wrong_s24_ultra, wrong_a15, wrong_case]

    results = SearchEngineService.filter_and_rank_products(
        products=candidates,
        raw_query="Samsung Galaxy S25 Ultra",
        min_threshold=40.0,
    )

    assert valid_ultra in results
    assert wrong_base not in results
    assert wrong_plus not in results
    assert wrong_s24_ultra not in results
    assert wrong_a15 not in results
    assert wrong_case not in results


def test_macbook_air_m4_relevance_isolation():
    """
    Search query: 'MacBook Air M4'
    Must match: Apple MacBook Air M4 (16GB RAM, 512GB SSD)
    Must EXCLUDE: MacBook Pro M4, MacBook Air M3, iPad Air, iPhone 15
    """
    valid_m4_air = DummyProduct("Apple MacBook Air M4 Chip (16GB RAM, 512GB SSD)", "Apple", "Laptops")
    wrong_pro = DummyProduct("Apple MacBook Pro M4 Chip (18GB RAM, 512GB SSD)", "Apple", "Laptops")
    wrong_m3 = DummyProduct("Apple MacBook Air M3 Chip (8GB RAM, 256GB SSD)", "Apple", "Laptops")
    wrong_ipad = DummyProduct("Apple iPad Air M2", "Apple", "Tablets")

    candidates = [valid_m4_air, wrong_pro, wrong_m3, wrong_ipad]

    results = SearchEngineService.filter_and_rank_products(
        products=candidates,
        raw_query="MacBook Air M4",
        min_threshold=40.0,
    )

    assert valid_m4_air in results
    assert wrong_pro not in results
    assert wrong_m3 not in results
    assert wrong_ipad not in results


def test_marketplace_verification_exact_vs_rejected():
    """Test ExactProductMatchEngine verification and rejection matrix."""

    # 1. Exact match
    is_match, score, reason = ExactProductMatchEngine.evaluate_marketplace_match(
        query_or_product="Apple iPhone 15 (128 GB) - Blue",
        candidate_title="Apple iPhone 15 128GB Blue Smartphone",
    )
    assert is_match is True
    assert score >= 0.90
    assert reason == "EXACT_VERIFIED_MATCH"

    # 2. Wrong model rejection (iPhone 15 vs 16)
    is_match, score, reason = ExactProductMatchEngine.evaluate_marketplace_match(
        query_or_product="Apple iPhone 15 (128 GB)",
        candidate_title="Apple iPhone 16 128GB Black",
    )
    assert is_match is False
    assert score == 0.0
    assert "MODEL_NUMBER_MISMATCH" in reason

    # 3. Wrong variant suffix rejection (iPhone 15 vs 15 Pro)
    is_match, score, reason = ExactProductMatchEngine.evaluate_marketplace_match(
        query_or_product="Apple iPhone 15 (128 GB)",
        candidate_title="Apple iPhone 15 Pro 128GB Natural Titanium",
    )
    assert is_match is False
    assert score == 0.0
    assert "VARIANT_SUFFIX_MISMATCH" in reason

    # 4. Accessory rejection
    is_match, score, reason = ExactProductMatchEngine.evaluate_marketplace_match(
        query_or_product="Apple iPhone 15 (128 GB)",
        candidate_title="Transparent Back Cover Case for Apple iPhone 15",
    )
    assert is_match is False
    assert score == 0.0
    assert "ACCESSORY_MISMATCH" in reason
