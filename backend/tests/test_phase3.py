"""
COMPAREX Backend – Phase 3 Marketplace Intelligence Core Tests
"""

from app.adapters.factory import MarketplaceFactory, SampleMockAdapter
from app.services.comparison_engine import ComparisonEngineService
from app.services.matching_engine import ProductMatchingEngine


def test_marketplace_factory_registration():
    """Verify MarketplaceFactory adapter registration and instantiation."""
    MarketplaceFactory.register("mock_test", SampleMockAdapter)
    adapter = MarketplaceFactory.get_adapter("mock_test", "https://example.com")

    assert adapter is not None
    assert adapter.marketplace_slug == "mock_test"
    assert adapter.base_url == "https://example.com"


def test_comparison_engine_matrix_calculation():
    """Verify ComparisonEngineService price matrix calculation."""
    sample_listings = [
        {
            "id": "lst-1",
            "price": 29990.0,
            "original_price": 34990.0,
            "discount_percent": 14.29,
            "is_available": True,
            "is_prime": True,
            "rating": 4.6,
        },
        {
            "id": "lst-2",
            "price": 31990.0,
            "original_price": 34990.0,
            "discount_percent": 8.57,
            "is_available": True,
            "is_prime": False,
            "rating": 4.2,
        },
        {
            "id": "lst-3",
            "price": 28990.0,
            "original_price": 34990.0,
            "discount_percent": 17.15,
            "is_available": True,
            "is_prime": True,
            "rating": 4.8,
        },
    ]

    res = ComparisonEngineService.calculate_comparison_matrix(
        product_id="prod-123",
        product_name="Sony Headphones",
        listings=sample_listings,
    )

    assert res["total_listings"] == 3
    assert res["lowest_price"] == 28990.0
    assert res["highest_price"] == 31990.0
    assert res["price_spread"] == 3000.0
    assert res["best_listing_id"] == "lst-3"


def test_product_matching_engine_similarity():
    """Verify ProductMatchingEngine fuzzy title similarity and duplicate evaluation."""
    title1 = "Apple iPhone 15 Pro Max 256GB Natural Titanium"
    title2 = "Apple iPhone 15 Pro Max - 256 GB (Natural Titanium)"

    sim = ProductMatchingEngine.calculate_title_similarity(title1, title2)
    assert sim > 0.80

    p1 = {
        "name": title1,
        "brand": "Apple",
        "specifications": {"storage": "256GB", "ram": "8GB"},
    }
    p2 = {
        "name": title2,
        "brand": "Apple",
        "specifications": {"storage": "256GB", "ram": "8GB"},
    }

    eval_res = ProductMatchingEngine.evaluate_duplicate_candidate(p1, p2)
    assert eval_res["is_duplicate"] is True
    assert eval_res["confidence_score"] >= 0.75
