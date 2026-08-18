"""
COMPAREX Backend - Google Profile & OAuth Name Resolution Tests
"""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_google_auth_name_resolution_full_name():
    """Test that Google OAuth authentication with full_name returns full_name and not
    'Google User'."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        req_payload = {
            "google_id": "google_test_profile_101",
            "email": "manikanta.g@example.com",
            "full_name": "Manikanta Gangiredla",
            "avatar_url": "https://lh3.googleusercontent.com/photo.jpg",
        }
        response = await ac.post("/api/v1/auth/google", json=req_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        user = data["data"]["user"]
        assert user["name"] == "Manikanta Gangiredla"
        assert user["email"] == "manikanta.g@example.com"
        assert user["login_provider"] == "google"
        assert user["avatar_url"] == "https://lh3.googleusercontent.com/photo.jpg"


@pytest.mark.asyncio
async def test_google_auth_name_resolution_email_prefix_fallback():
    """Test that Google OAuth without name falls back to capitalized email prefix and
    NEVER 'Google User'."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        req_payload = {
            "google_id": "google_test_profile_102",
            "email": "manikanta@gmail.com",
            "name": "Google User",  # Generic client placeholder
        }
        response = await ac.post("/api/v1/auth/google", json=req_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        user = data["data"]["user"]
        assert user["name"] == "Manikanta"
        assert user["name"] != "Google User"
        assert user["login_provider"] == "google"
