"""
COMPAREX Backend – SimulationEngine Sub-Service

Instantly re-simulates shopping plan setups based on user budget adjustments and filter parameters.
"""

from typing import List

from app.schemas.planner import CategoryPlanItem, PlanGenerationResponse, PlanSimulationRequest
from app.services.planner.budget_optimizer import BudgetOptimizer
from app.services.planner.compatibility_engine import CompatibilityEngine


class SimulationEngine:
    """Real-Time Shopping Simulation & Recalculation Engine."""

    @classmethod
    def re_simulate_plan(
        cls,
        payload: PlanSimulationRequest,
    ) -> PlanGenerationResponse:
        """Recalculate plan setup for user target budget or marketplace filter."""
        items: List[CategoryPlanItem] = [item.model_copy() for item in payload.items]

        if payload.filter_marketplace:
            for item in items:
                item.marketplace_name = payload.filter_marketplace

        if payload.optimize_mode == "PREMIUM":
            for item in items:
                item.price = round(item.price * 1.15, 2)
                item.deal_score = 9.5
        elif payload.optimize_mode == "BEST_VALUE":
            for item in items:
                item.price = round(item.price * 0.88, 2)
                item.deal_score = 9.8

        opt_items, allocated, remaining = BudgetOptimizer.optimize_allocations(
            items, payload.target_budget
        )
        comp_score, _ = CompatibilityEngine.evaluate_compatibility(opt_items)

        return PlanGenerationResponse(
            goal_title="Simulated Shopping Setup",
            scenario_type="SIMULATED",
            total_budget=payload.target_budget,
            allocated_budget=allocated,
            remaining_budget=remaining,
            compatibility_score=comp_score,
            items=opt_items,
        )
