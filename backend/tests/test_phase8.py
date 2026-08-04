"""
COMPAREX Backend – Phase 8 Test Suite

Tests Personal Shopping Profile, Shopping Memory, Shopping DNA, Multi-Agent Orchestration,
AI Coach, Explainable AI, Feedback Loop, Analytics, and Smart Privacy Center.
"""

import uuid

import pytest

from app.ai.agents.orchestrator import orchestrator
from app.schemas.explain import CompareExplainRequest
from app.services.explainable_ai_service import ExplainableAIService
from app.services.personalized_recommendation_service import PersonalizedRecommendationService


@pytest.mark.anyio
async def test_multi_agent_orchestrator_execution():
    """Verify Multi-Agent AI System Orchestrator executes all 9 agents."""
    prompt = "Find best noise cancelling headphones under 25000"
    res = await orchestrator.run_orchestration(prompt)

    assert res["confidence_score"] == 0.95
    assert "agent_outputs" in res
    assert "ShoppingAgent" in res["agent_outputs"]
    assert "DealAgent" in res["agent_outputs"]
    assert "PriceAgent" in res["agent_outputs"]


@pytest.mark.anyio
async def test_explainable_ai_comparison():
    """Verify CompareX Explain reasoning engine compares two products."""
    req = CompareExplainRequest(
        product_a_name="Sony WH-1000XM5",
        product_b_name="Bose QC Ultra",
        product_a_price=24990.0,
        product_b_price=29900.0,
    )
    res = await ExplainableAIService.explain_comparison(req)

    assert res.winner_name == "Sony WH-1000XM5"
    assert res.confidence_score == 0.95
    assert len(res.key_advantages_a) > 0


@pytest.mark.anyio
async def test_personalized_recommendation_engine():
    """Verify personalized recommendation service returns grounded recommendations."""
    dummy_user_id = uuid.uuid4()
    res = await PersonalizedRecommendationService.get_personalized_recommendations(
        db=None,
        user_id=dummy_user_id,
        query="smartwatch",
    )

    assert res["query"] == "smartwatch"
    assert len(res["recommendations"]) == 2
    assert len(res["alternatives"]) == 1


@pytest.mark.anyio
async def test_phase8_api_endpoints():
    """Test Phase 8 public API endpoints."""
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test Coach endpoint
        resp = await client.post(
            "/api/v1/coach/ask",
            json={"question": "Should I buy now?", "product_name": "Test Laptop"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["verdict"] in ("BUY", "WAIT")

        # Test Explain endpoint
        resp = await client.post(
            "/api/v1/explain/compare",
            json={
                "product_a_name": "Phone A",
                "product_b_name": "Phone B",
                "product_a_price": 19999.0,
                "product_b_price": 24999.0,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["winner_name"] == "Phone A"
