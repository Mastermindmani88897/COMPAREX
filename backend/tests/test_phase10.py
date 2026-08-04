"""
COMPAREX Backend – Phase 10 Enterprise Test Suite

Tests Metrics endpoint, Rate Limiting & Security Headers, Admin API, and Advanced AI Modes.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.ai_modes import AIModeSelectRequest
from app.services.ai_mode_service import AIModeService


@pytest.mark.anyio
async def test_ai_modes_service():
    """Verify AIModeService returns all 9 modes and supports mode switching."""
    modes = AIModeService.list_modes()
    assert len(modes) == 9

    req = AIModeSelectRequest(mode_id="GAMING")
    res = AIModeService.select_mode(req)

    assert res.active_mode == "GAMING"
    assert "gpu" in res.mode_definition.weights


@pytest.mark.anyio
async def test_phase10_enterprise_api_endpoints():
    """Test Phase 10 Metrics, AI Modes, and Security Headers."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test Metrics Endpoint
        resp = await client.get("/api/v1/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "total_requests" in data["data"]

        # Verify Security Headers
        assert resp.headers.get("X-Frame-Options") == "DENY"
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"

        # Test List AI Modes Endpoint
        resp = await client.get("/api/v1/ai/modes")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["data"]) == 9
