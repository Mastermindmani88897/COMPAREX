"""
COMPAREX Backend - Automated Unit & Integration Tests for Autocomplete & Search
"""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_autocomplete_and_search_filters(async_client: AsyncClient):
    """Test GET /api/v1/products/autocomplete and advanced search filters."""
    random_id = str(uuid.uuid4())[:8]
    test_email = f"auto_{random_id}@example.com"
    test_password = "SecurePassword123!"

    # 1. Register user
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": test_email,
            "name": "Autocomplete Tester",
            "password": test_password,
            "confirm_password": test_password,
        },
    )
    assert reg_res.status_code == 201

    # 2. Login to get access token
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": test_email, "password": test_password},
    )
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    prod_res = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Autocomplete POCO Phone 5G",
            "category": "Mobiles",
            "brand": "POCO",
            "base_price": 21999.00,
        },
        headers=headers,
    )
    assert prod_res.status_code == 201

    # 3. Test Autocomplete endpoint
    auto_res = await async_client.get("/api/v1/products/autocomplete?q=poco")
    assert auto_res.status_code == 200
    suggestions = auto_res.json()["data"]
    assert len(suggestions) > 0
    assert any("POCO" in item["name"] or "POCO" in item["brand"] for item in suggestions)

    # 4. Test Advanced Filtering
    list_res = await async_client.get("/api/v1/products?query=poco&category=mobiles&brand=poco")
    assert list_res.status_code == 200
    products = list_res.json()["data"]
    assert len(products) > 0
    assert products[0]["brand"].lower() == "poco"
