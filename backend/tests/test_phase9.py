"""
COMPAREX Backend – Phase 9 Test Suite

Tests GoalParser, ShoppingPlanner, BudgetOptimizer, CompatibilityEngine,
SimulationEngine, ConversationManager, ReportGenerator, and Flagship Planner APIs.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.planner import GoalParseRequest, PlanGenerationRequest, PlanSimulationRequest
from app.services.planner.planner_orchestrator import PlannerOrchestrator


@pytest.mark.anyio
async def test_goal_parser_execution():
    """Verify GoalParser parses natural language shopping goal prompt."""
    req = GoalParseRequest(prompt="I am starting engineering next month with ₹90,000. Build setup.")
    res = await PlannerOrchestrator.parse_goal_prompt(req)

    assert res.extracted_budget == 90000.0
    assert res.scenario_type == "ENGINEERING_STUDENT"
    assert len(res.priorities) > 0


@pytest.mark.anyio
async def test_generate_shopping_plan_execution():
    """Verify PlannerOrchestrator generates full multi-category shopping plan setup."""
    req = PlanGenerationRequest(
        prompt="Gaming setup with ₹1,20,000 budget",
        budget=120000.0,
        scenario_type="GAMING_SETUP",
    )
    plan = await PlannerOrchestrator.generate_shopping_plan(req)

    assert plan.scenario_type == "GAMING_SETUP"
    assert plan.total_budget == 120000.0
    assert plan.allocated_budget <= plan.total_budget
    assert len(plan.items) >= 4
    assert plan.compatibility_score >= 0.90


@pytest.mark.anyio
async def test_simulation_engine():
    """Verify SimulationEngine recalculates setup when budget changes."""
    req = PlanGenerationRequest(
        prompt="WFH Office Setup",
        budget=100000.0,
        scenario_type="WFH_OFFICE",
    )
    plan = await PlannerOrchestrator.generate_shopping_plan(req)

    sim_req = PlanSimulationRequest(
        items=plan.items,
        target_budget=120000.0,
        filter_marketplace="Amazon India",
        optimize_mode="PREMIUM",
    )
    sim_res = await PlannerOrchestrator.simulate_plan(sim_req)

    assert sim_res.total_budget == 120000.0
    assert all(item.marketplace_name == "Amazon India" for item in sim_res.items)


@pytest.mark.anyio
async def test_phase9_planner_api_endpoints():
    """Test Phase 9 public AI Marketplace Planner API endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test Parse Goal endpoint
        resp = await client.post(
            "/api/v1/planner/parse-goal",
            json={"prompt": "Engineering student setup under ₹90,000"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["extracted_budget"] == 90000.0

        # Test Export endpoint
        gen_req = PlanGenerationRequest(
            prompt="Photography kit",
            budget=120000.0,
        )
        plan_res = await PlannerOrchestrator.generate_shopping_plan(gen_req)

        resp = await client.post(
            "/api/v1/planner/export",
            json=plan_res.model_dump(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["format"] == "JSON"
