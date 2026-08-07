"""
COMPAREX Backend - Module 2 Prioritized Marketplace Connector Test Suite

Tests Priority 1 (Official API), Priority 2 (Third-Party Provider),
and Priority 3 (Graceful Fallback & Cache).
"""

import pytest
from app.adapters.factory import MarketplaceFactory
from app.adapters.priority_connector import PrioritizedMarketplaceConnector
from app.core.config import settings


@pytest.mark.asyncio
async def test_priority_3_default_fallback():
    """Test default Priority 3 fallback when no API keys are set."""
    # Ensure keys are clear
    settings.AMAZON_PAAPI_KEY = None
    settings.THIRD_PARTY_SHOPPING_API_KEY = None

    connector = MarketplaceFactory.get_adapter("amazon")
    assert isinstance(connector, PrioritizedMarketplaceConnector)
    assert connector.get_active_priority() == 3

    # Execute search
    results = await connector.search_products("iPhone 16", limit=5)
    assert isinstance(results, list)
    assert len(results) > 0

    # Verify normalized format
    normalized = connector.normalize_listing(results[0])
    assert "price" in normalized
    assert "listing_url" in normalized
    assert normalized["marketplace_slug"] == "amazon"


@pytest.mark.asyncio
async def test_priority_2_third_party_provider():
    """Test Priority 2 activation when third-party provider key is set."""
    settings.AMAZON_PAAPI_KEY = None
    settings.THIRD_PARTY_SHOPPING_API_KEY = "test_tp_key_123"

    connector = PrioritizedMarketplaceConnector(marketplace_slug="amazon")
    assert connector.get_active_priority() == 2

    results = await connector.search_products("Samsung Galaxy", limit=3)
    assert len(results) > 0
    assert results[0].get("data_priority") == 2

    # Clean up setting
    settings.THIRD_PARTY_SHOPPING_API_KEY = None


@pytest.mark.asyncio
async def test_priority_1_official_api():
    """Test Priority 1 activation when official API credentials are set."""
    settings.AMAZON_PAAPI_KEY = "test_paapi_key"
    settings.AMAZON_PAAPI_SECRET = "test_paapi_secret"

    connector = PrioritizedMarketplaceConnector(marketplace_slug="amazon")
    assert connector.get_active_priority() == 1

    results = await connector.search_products("MacBook Air", limit=3)
    assert len(results) > 0
    assert results[0].get("data_priority") == 1

    # Clean up settings
    settings.AMAZON_PAAPI_KEY = None
    settings.AMAZON_PAAPI_SECRET = None


@pytest.mark.asyncio
async def test_connector_never_crashes_on_error():
    """Test that connector catches priority errors gracefully and returns fallback data."""
    connector = PrioritizedMarketplaceConnector(marketplace_slug="flipkart")

    # Details & price check should return valid payload without raising exceptions
    details = await connector.fetch_product_details("https://www.flipkart.com/item/123")
    assert "price" in details
    assert "title" in details

    price_data = await connector.fetch_latest_price("https://www.flipkart.com/item/123")
    assert "price" in price_data
