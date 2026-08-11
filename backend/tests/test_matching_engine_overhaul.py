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


def test_airpods_pro_relevance_isolation():
    """
    Search query: 'AirPods Pro'
    Must match: Apple AirPods Pro (2nd Gen)
    Must EXCLUDE: Apple AirPods 3rd Gen, Apple AirPods Max, Protective Case for AirPods Pro
    """
    valid_pro = DummyProduct("Apple AirPods Pro (2nd Generation) with MagSafe Case", "Apple", "Headphones")
    wrong_gen = DummyProduct("Apple AirPods (3rd Generation) with Lightning Charging Case", "Apple", "Headphones")
    wrong_max = DummyProduct("Apple AirPods Max Wireless Over-Ear Headphones", "Apple", "Headphones")
    wrong_case = DummyProduct("Silicone Protective Case Cover for Apple AirPods Pro", "Spigen", "Accessories")

    candidates = [valid_pro, wrong_gen, wrong_max, wrong_case]

    results = SearchEngineService.filter_and_rank_products(
        products=candidates,
        raw_query="AirPods Pro",
        min_threshold=20.0,
    )

    assert valid_pro in results
    assert wrong_gen not in results
    assert wrong_max not in results
    assert wrong_case not in results


def test_ps5_relevance_isolation():
    """
    Search query: 'PS5'
    Must match: Sony PlayStation 5 Console (Disc Edition)
    Must EXCLUDE: Sony PlayStation 4 Slim, DualSense Wireless Controller for PS5
    """
    valid_ps5 = DummyProduct("Sony PlayStation 5 Console (Disc Edition)", "Sony", "Gaming")
    wrong_ps4 = DummyProduct("Sony PlayStation 4 Slim 1TB Console", "Sony", "Gaming")
    wrong_accessory = DummyProduct("Sony DualSense Wireless Controller for PlayStation 5", "Sony", "Accessories")

    candidates = [valid_ps5, wrong_ps4, wrong_accessory]

    results = SearchEngineService.filter_and_rank_products(
        products=candidates,
        raw_query="PS5",
        min_threshold=40.0,
    )

    assert valid_ps5 in results
    assert wrong_ps4 not in results
    assert wrong_accessory not in results


def test_provider_failure_resilience_and_status_states():
    """
    Test MarketplaceAggregatorService _build_major_marketplace_status.
    Verifies that major marketplaces return proper state objects (verified vs unavailable)
    even when provider calls fail or encounter rate limits.
    """
    from app.services.aggregator_service import MarketplaceAggregatorService

    verified_listings = [
        {
            "marketplace_slug": "amazon",
            "title": "Samsung Galaxy S25 Ultra 5G",
            "price": 129999.0,
            "original_price": 139999.0,
            "discount_percent": 7.0,
            "currency": "INR",
            "listing_url": "https://www.amazon.in/dp/B0D1234567",
            "image_url": "https://m.media-amazon.com/images/I/71xxx.jpg",
            "is_exact_url": True,
            "is_available": True,
            "match_score": 0.95,
        }
    ]

    provider_statuses = {
        "rainforest_amazon": "provider_rate_limit (429)",
        "brightdata_flipkart": "provider_failure (500)",
    }

    status_list = MarketplaceAggregatorService._build_major_marketplace_status(
        canonical_offers=verified_listings,
        provider_statuses=provider_statuses,
        query="Samsung Galaxy S25 Ultra",
        last_checked="2026-08-11T12:00:00Z",
    )

    # Must contain 7 major marketplaces
    assert len(status_list) == 7
    slugs = [s["slug"] for s in status_list]
    assert "amazon" in slugs
    assert "flipkart" in slugs
    assert "croma" in slugs

    # Amazon entry must be verified
    amazon_entry = next(s for s in status_list if s["slug"] == "amazon")
    assert amazon_entry["status"] == "verified"
    assert amazon_entry["price"] == 129999.0
    assert amazon_entry["has_verified_price"] is True
    assert amazon_entry["is_exact_url"] is True

    # Flipkart entry must be unavailable (due to provider failure) with fallback search link
    flipkart_entry = next(s for s in status_list if s["slug"] == "flipkart")
    assert flipkart_entry["status"] == "unavailable"
    assert flipkart_entry["price"] is None
    assert flipkart_entry["has_verified_price"] is False
    assert "flipkart.com/search" in flipkart_entry["listing_url"]

