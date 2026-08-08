"""COMPAREX Backend - Automated Tests for Registration, Error Handling, and Username Setup."""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_email_registration_valid():
    """Test valid user email registration."""
    transport = ASGITransport(app=app)
    uid = uuid.uuid4().hex[:8]
    email = f"mahesh_reg_{uid}@gmail.com"
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/auth/register", json={
            "name": "Mahesh",
            "email": email,
            "password": "ValidPassword123!",
            "confirm_password": "ValidPassword123!"
        })
        assert res.status_code == 201
        data = res.json()
        assert data["success"] is True
        assert data["data"]["email"] == email
        assert data["data"]["name"] == "Mahesh"
        assert data["data"]["username"] is not None


@pytest.mark.asyncio
async def test_email_registration_duplicate_email():
    """Test duplicate email registration returns 409 with clear message."""
    transport = ASGITransport(app=app)
    uid = uuid.uuid4().hex[:8]
    email = f"duplicate_{uid}@gmail.com"
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First registration
        await client.post("/api/v1/auth/register", json={
            "name": "First User",
            "email": email,
            "password": "ValidPassword123!",
            "confirm_password": "ValidPassword123!"
        })
        # Second registration with same email
        res = await client.post("/api/v1/auth/register", json={
            "name": "Second User",
            "email": email,
            "password": "ValidPassword123!",
            "confirm_password": "ValidPassword123!"
        })
        assert res.status_code == 409
        data = res.json()
        assert "already registered" in data["message"].lower()


@pytest.mark.asyncio
async def test_email_registration_invalid_email():
    """Test invalid email format returns 422 with clear message."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/auth/register", json={
            "name": "Mahesh",
            "email": "notanemail",
            "password": "ValidPassword123!",
            "confirm_password": "ValidPassword123!"
        })
        assert res.status_code == 422
        data = res.json()
        assert "invalid email" in data["message"].lower()


@pytest.mark.asyncio
async def test_email_registration_short_password():
    """Test short password returns 422 with clear message."""
    transport = ASGITransport(app=app)
    uid = uuid.uuid4().hex[:8]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/auth/register", json={
            "name": "Mahesh",
            "email": f"shortpw_{uid}@gmail.com",
            "password": "short",
            "confirm_password": "short"
        })
        assert res.status_code == 422
        data = res.json()
        assert "at least 8 characters" in data["message"].lower()


@pytest.mark.asyncio
async def test_google_auth_name_preservation_and_username_setup():
    """Test Google OAuth login preserves Google profile name and supports custom username setup."""
    transport = ASGITransport(app=app)
    uid = uuid.uuid4().hex[:8]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Google Auth Login
        res_g = await client.post("/api/v1/auth/google", json={
            "google_id": f"google_sub_{uid}",
            "email": f"mahesh.g_{uid}@gmail.com",
            "name": "Mahesh Gangiredla",
            "full_name": "Mahesh Gangiredla",
            "avatar_url": "https://lh3.googleusercontent.com/a/test"
        })
        assert res_g.status_code == 200
        g_data = res_g.json()
        token = g_data["data"]["access_token"]
        assert g_data["data"]["user"]["name"] == "Mahesh Gangiredla"
        assert g_data["data"]["user"]["needs_username_setup"] is True

        headers = {"Authorization": f"Bearer {token}"}

        # 2. Setup custom username
        custom_un = f"Mahesh_{uid}"
        res_u = await client.post("/api/v1/users/me/username", headers=headers, json={
            "username": custom_un
        })
        assert res_u.status_code == 200
        u_data = res_u.json()
        assert u_data["data"]["username"] == custom_un
        assert u_data["data"]["needs_username_setup"] is False


@pytest.mark.asyncio
async def test_username_collision_case_insensitive():
    """Test case-insensitive username uniqueness constraint."""
    transport = ASGITransport(app=app)
    uid = uuid.uuid4().hex[:8]
    target_un = f"Mahesh_Coll_{uid}"

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # User 1 registers with username target_un
        res1 = await client.post("/api/v1/auth/register", json={
            "name": "User One",
            "username": target_un,
            "email": f"u1_{uid}@gmail.com",
            "password": "ValidPassword123!",
            "confirm_password": "ValidPassword123!"
        })
        assert res1.status_code == 201

        # User 2 logs in via Google and attempts to set lower version of target_un
        res_g = await client.post("/api/v1/auth/google", json={
            "google_id": f"google_u2_{uid}",
            "email": f"u2_{uid}@gmail.com",
            "name": "User Two"
        })
        token2 = res_g.json()["data"]["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Attempt to claim target_un in lowercase (case insensitive collision)
        res_un = await client.post("/api/v1/users/me/username", headers=headers2, json={
            "username": target_un.lower()
        })
        assert res_un.status_code == 409
        assert "already taken" in res_un.json()["message"].lower()
