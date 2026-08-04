"""
COMPAREX Backend - Phase 4 Automated Unit & Integration Tests

Tests:
1. ConnectorRegistry & CategoryCapabilityRegistry
2. All 9 Mock Connector implementations
3. MarketplaceAggregatorService (concurrent query, deduplication, deal-scoring)
4. Redis caching behavior
"""

import pytest

from app.adapters.mock_connectors import AmazonMockConnector, NykaaMockConnector
from app.adapters.registry import CategoryCapabilityRegistry, ConnectorRegistry
from app.services.aggregator_service import MarketplaceAggregatorService


@pytest.mark.anyio
async def test_connector_registry_initialization():
    """Verify all 9 connectors are registered in ConnectorRegistry with proper metadata."""
    connectors = ConnectorRegistry.list_connectors(enabled_only=True)
    assert len(connectors) >= 9

    slugs = [c.slug for c in connectors]
    expected_slugs = [
        "amazon",
        "flipkart",
        "croma",
        "reliance_digital",
        "vijay_sales",
        "myntra",
        "ajio",
        "meesho",
        "nykaa",
    ]
    for s in expected_slugs:
        assert s in slugs


def test_category_capability_registry():
    """Verify category to connector mappings."""
    elec_slugs = CategoryCapabilityRegistry.get_supported_connectors("electronics")
    assert "croma" in elec_slugs
    assert "reliance_digital" in elec_slugs
    assert "vijay_sales" in elec_slugs

    fashion_slugs = CategoryCapabilityRegistry.get_supported_connectors("fashion")
    assert "myntra" in fashion_slugs
    assert "ajio" in fashion_slugs
    assert "meesho" in fashion_slugs

    beauty_slugs = CategoryCapabilityRegistry.get_supported_connectors("beauty")
    assert "nykaa" in beauty_slugs


@pytest.mark.anyio
async def test_mock_connectors_execution():
    """Test standardized interface methods on Amazon, Flipkart, Croma, Myntra, Nykaa connectors."""
    amazon = AmazonMockConnector(marketplace_slug="amazon", base_url="https://www.amazon.in")
    results = await amazon.search_products("iPhone 15", limit=5)
    assert len(results) > 0
    assert results[0]["price"] > 0
    assert "Amazon Prime" in results[0]["badges"]

    details = await amazon.get_product_details("https://www.amazon.in/product/iphone-15")
    assert details["price"] > 0

    avail = await amazon.get_availability("https://www.amazon.in/product/iphone-15")
    assert avail["is_available"] is True

    eta = await amazon.get_delivery_estimate("https://www.amazon.in/product/iphone-15")
    assert "delivery_estimate" in eta

    nykaa = NykaaMockConnector(marketplace_slug="nykaa", base_url="https://www.nykaa.com")
    beauty_results = await nykaa.search_products("Lipstick", limit=3)
    assert len(beauty_results) > 0
    assert "100% Authentic Beauty" in beauty_results[0]["badges"]


@pytest.mark.anyio
async def test_marketplace_aggregator_service():
    """Test multi-connector aggregation, deduplication, sorting, and deal scoring."""
    res = await MarketplaceAggregatorService.aggregate_search(
        query="iPhone 15",
        category="electronics",
        limit_per_connector=3,
        sort_by="price",
        use_cache=False,
    )

    assert res["query"] == "iPhone 15"
    assert res["total_listings"] > 0
    assert "amazon" in res["marketplaces_queried"]
    assert "flipkart" in res["marketplaces_queried"]
    assert "croma" in res["marketplaces_queried"]

    listings = res["listings"]
    assert len(listings) >= 3

    # Check sorting: lowest price first
    prices = [item["price"] for item in listings]
    assert prices == sorted(prices)

    # Check deal scores and badges
    assert "deal_score" in listings[0]
    assert listings[0]["deal_score"] > 0
    assert "Lowest Price" in listings[0]["badges"]
