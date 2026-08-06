"""
COMPAREX Backend - Automated Unit & Integration Tests for Wishlist REST APIs
"""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_wishlist_full_crud_flow(async_client: AsyncClient):
    """Test full wishlist CRUD lifecycle: add, get, patch, delete, and price alert sync."""
    random_id = str(uuid.uuid4())[:8]
    test_email = f"wishlist_{random_id}@example.com"
    test_password = "SecurePassword123!"

    # 1. Register user
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": test_email,
            "name": "Wishlist User",
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

    # 3. Create product with auth
    prod_res = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Wishlist Test Smartphone 5G",
            "category": "Mobiles",
            "brand": "TestBrand",
            "base_price": 49999.00,
        },
        headers=headers,
    )
    assert prod_res.status_code == 201
    product_id = prod_res.json()["data"]["id"]

    # 4. POST /api/v1/wishlist (Add product to wishlist)
    add_payload = {
        "product_id": product_id,
        "preferred_marketplace": "Amazon",
        "target_price": 45000.00,
        "notes": "Buying on sale event",
    }
    response = await async_client.post("/api/v1/wishlist", json=add_payload, headers=headers)
    assert response.status_code == 201
    data = response.json()["data"]
    wishlist_id = data["id"]
    assert data["product_id"] == product_id
    assert float(data["target_price"]) == 45000.00

    # 5. GET /api/v1/wishlist (Fetch user wishlist)
    get_res = await async_client.get("/api/v1/wishlist", headers=headers)
    assert get_res.status_code == 200
    w_data = get_res.json()["data"]
    assert w_data["total_items"] >= 1
    assert len(w_data["items"]) >= 1
    assert "ai_recommendations" in w_data

    # 6. PATCH /api/v1/wishlist/{id} (Update target price)
    patch_payload = {"target_price": 42000.00, "notes": "Updated target"}
    patch_res = await async_client.patch(f"/api/v1/wishlist/{wishlist_id}", json=patch_payload, headers=headers)
    assert patch_res.status_code == 200
    assert float(patch_res.json()["data"]["target_price"]) == 42000.00

    # 7. DELETE /api/v1/wishlist/{id} (Remove item)
    del_res = await async_client.delete(f"/api/v1/wishlist/{wishlist_id}", headers=headers)
    assert del_res.status_code == 200

    # Verify empty wishlist
    final_res = await async_client.get("/api/v1/wishlist", headers=headers)
    assert final_res.status_code == 200
    assert final_res.json()["data"]["total_items"] == 0
