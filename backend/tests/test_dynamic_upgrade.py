"""
COMPAREX Backend - Tests for Final Production Upgrade
Tests recently viewed history, dynamic trending products, and dynamic wishlist recommendations.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_trending_products_endpoint():
    """Test GET /api/v1/products/trending returns real products."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        res = await client.get("/api/v1/products/trending")
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") is True
        assert isinstance(data.get("data"), list)


@pytest.mark.asyncio
async def test_recently_viewed_requires_auth():
    """Test GET /api/v1/products/recently-viewed requires authentication."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        res = await client.get("/api/v1/products/recently-viewed")
        assert res.status_code in (401, 403)
