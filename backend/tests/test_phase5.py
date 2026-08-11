"""
COMPAREX Backend - Phase 5 Extension Gateway Automated Tests

Tests:
1. GET /api/v1/extension/status
2. GET /api/v1/extension/version
3. POST /api/v1/extension/product (Product Ingestion & Live Comparison)
4. POST /api/v1/extension/compare (Quick Overlay Comparison)
5. Request Validation & Gateway Security
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_extension_status_endpoint():
    """Test Extension Gateway health and status check endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/extension/status")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "online"
        assert data["active_connectors_count"] >= 9
        assert "amazon" in data["supported_marketplaces"]
        assert "flipkart" in data["supported_marketplaces"]


@pytest.mark.anyio
async def test_extension_version_check():
    """Test Extension client version compatibility validation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/extension/version?v=1.0.0")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["client_version"] == "1.0.0"
        assert data["is_compatible"] is True
        assert data["update_required"] is False


@pytest.mark.anyio
async def test_extension_product_ingest():
    """Test product ingestion from extension content script."""
    payload = {
        "title": "iPhone 15 (128GB) - Black",
        "price": 69990.0,
        "currency": "INR",
        "url": "https://www.amazon.in/dp/B0CHX1W1XY",
        "image_url": "https://images.amazon.com/iphone15.jpg",
        "seller_name": "Appario Retail",
        "rating": 4.6,
        "marketplace_slug": "amazon",
        "extension_version": "1.0.0",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/extension/product", json=payload)
        assert response.status_code == 200
        data = response.json()["data"]
        assert "detected_product" in data
        assert data["detected_product"]["title"] == payload["title"]
        assert "comparison_matrix" in data
        assert data["comparison_matrix"]["total_listings"] >= 0


@pytest.mark.anyio
async def test_extension_quick_compare():
    """Test quick overlay comparison search API."""
    payload = {
        "product_title": "MacBook Air M2",
        "category": "electronics",
        "current_price": 99990.0,
        "marketplace_slug": "flipkart",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/extension/compare", json=payload)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["query"] == payload["product_title"]
        assert data["total_listings"] >= 0
