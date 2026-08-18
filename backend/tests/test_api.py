"""
COMPAREX Backend – Integration & Unit Test Suite

Tests Health Check, Authentication, User Profile, Category, Product, and Marketplace APIs.
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check API returns status 200 and connected status."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "ok"
        assert data["data"]["database"] == "connected"
        assert data["data"]["redis"] == "connected"


@pytest.mark.asyncio
async def test_full_auth_and_user_flow():
    """Test register, login, profile get/update, refresh, and logout flow."""
    random_id = str(uuid.uuid4())[:8]
    test_email = f"testuser_{random_id}@comparex.io"
    test_password = "SecurePassword123!"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Register
        reg_payload = {
            "email": test_email,
            "name": "Test User",
            "password": test_password,
            "confirm_password": test_password,
        }
        reg_res = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert reg_res.status_code == 201, reg_res.text
        assert reg_res.json()["data"]["email"] == test_email

        # Duplicate registration error
        dup_res = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert dup_res.status_code == 409

        # 2. Login
        login_payload = {"email": test_email, "password": test_password}
        login_res = await ac.post("/api/v1/auth/login", json=login_payload)
        assert login_res.status_code == 200
        tokens = login_res.json()["data"]
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        assert access_token is not None

        headers = {"Authorization": f"Bearer {access_token}"}

        # 3. Get Profile
        profile_res = await ac.get("/api/v1/users/me", headers=headers)
        assert profile_res.status_code == 200
        assert profile_res.json()["data"]["email"] == test_email

        # 4. Update Profile
        update_res = await ac.patch(
            "/api/v1/users/me",
            json={"name": "Updated Name"},
            headers=headers,
        )
        assert update_res.status_code == 200
        assert update_res.json()["data"]["name"] == "Updated Name"

        # 5. Refresh Token
        ref_res = await ac.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert ref_res.status_code == 200
        assert ref_res.json()["data"]["access_token"] is not None

        # 6. Logout
        logout_res = await ac.post("/api/v1/auth/logout", headers=headers)
        assert logout_res.status_code == 200

        # 7. Post-logout access fails
        fail_res = await ac.get("/api/v1/users/me", headers=headers)
        assert fail_res.status_code == 401


@pytest.mark.asyncio
async def test_category_crud():
    """Test Category CRUD API endpoints."""
    cid = str(uuid.uuid4())[:8]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Register user for auth header
        email = f"cat_user_{cid}@comparex.io"
        await ac.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "name": "Cat User",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
        )
        login_res = await ac.post(
            "/api/v1/auth/login", json={"email": email, "password": "Password123!"}
        )
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create Category
        cat_payload = {
            "name": f"Electronics_{cid}",
            "slug": f"electronics-{cid}",
            "description": "Gadgets & Electronics",
        }
        create_res = await ac.post("/api/v1/categories", json=cat_payload, headers=headers)
        assert create_res.status_code == 201
        cat_id = create_res.json()["data"]["id"]

        # List Categories
        list_res = await ac.get("/api/v1/categories")
        assert list_res.status_code == 200
        assert len(list_res.json()["data"]) >= 1

        # Get Category by ID
        get_res = await ac.get(f"/api/v1/categories/{cat_id}")
        assert get_res.status_code == 200
        assert get_res.json()["data"]["slug"] == f"electronics-{cid}"

        # Update Category
        up_res = await ac.put(
            f"/api/v1/categories/{cat_id}", json={"name": f"Tech_{cid}"}, headers=headers
        )
        assert up_res.status_code == 200
        assert up_res.json()["data"]["name"] == f"Tech_{cid}"

        # Delete Category
        del_res = await ac.delete(f"/api/v1/categories/{cat_id}", headers=headers)
        assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_product_crud():
    """Test Product CRUD API endpoints."""
    pid = str(uuid.uuid4())[:8]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        email = f"prod_user_{pid}@comparex.io"
        await ac.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "name": "Prod User",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
        )
        login_res = await ac.post(
            "/api/v1/auth/login", json={"email": email, "password": "Password123!"}
        )
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create Product
        prod_payload = {
            "name": f"Smart Laptop_{pid}",
            "brand": "TechCorp",
            "base_price": 999.99,
            "ean": f"EAN{pid}",
        }
        create_res = await ac.post("/api/v1/products", json=prod_payload, headers=headers)
        assert create_res.status_code == 201
        product_id = create_res.json()["data"]["id"]

        # List & Search Products
        search_res = await ac.get("/api/v1/products?query=Smart")
        assert search_res.status_code == 200
        assert len(search_res.json()["data"]) >= 1

        # Get Product Details
        get_res = await ac.get(f"/api/v1/products/{product_id}")
        assert get_res.status_code == 200
        assert get_res.json()["data"]["brand"] == "TechCorp"

        # Delete Product
        del_res = await ac.delete(f"/api/v1/products/{product_id}", headers=headers)
        assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_marketplace_crud():
    """Test Marketplace CRUD API endpoints."""
    mid = str(uuid.uuid4())[:8]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        email = f"market_user_{mid}@comparex.io"
        await ac.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "name": "Market User",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
        )
        login_res = await ac.post(
            "/api/v1/auth/login", json={"email": email, "password": "Password123!"}
        )
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create Marketplace
        market_payload = {
            "name": f"ShopVerse_{mid}",
            "slug": f"shopverse-{mid}",
            "base_url": "https://shopverse.example.com",
        }
        create_res = await ac.post("/api/v1/marketplaces", json=market_payload, headers=headers)
        assert create_res.status_code == 201
        m_id = create_res.json()["data"]["id"]

        # Get Marketplace Details
        get_res = await ac.get(f"/api/v1/marketplaces/{m_id}")
        assert get_res.status_code == 200

        # Delete Marketplace
        del_res = await ac.delete(f"/api/v1/marketplaces/{m_id}", headers=headers)
        assert del_res.status_code == 200
