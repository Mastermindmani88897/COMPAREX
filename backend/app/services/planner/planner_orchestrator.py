"""
COMPAREX Backend – PlannerOrchestrator Unified Service

Orchestrates GoalParser, ShoppingPlanner, BudgetOptimizer, CompatibilityEngine,
SimulationEngine, ConversationManager, and ReportGenerator sub-services.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.planner import (
    GoalParseRequest,
    GoalParseResponse,
    PlanConversationRequest,
    PlanExportResponse,
    PlanGenerationRequest,
    PlanGenerationResponse,
    PlanSimulationRequest,
)
from app.services.planner.budget_optimizer import BudgetOptimizer
from app.services.planner.compatibility_engine import CompatibilityEngine
from app.services.planner.conversation_manager import ConversationManager
from app.services.planner.goal_parser import GoalParser
from app.services.planner.report_generator import ReportGenerator
from app.services.planner.shopping_planner import ShoppingPlanner
from app.services.planner.simulation_engine import SimulationEngine


class PlannerOrchestrator:
    """Unified Orchestrator for COMPAREX AI Marketplace Planner."""

    @classmethod
    async def parse_goal_prompt(cls, payload: GoalParseRequest) -> GoalParseResponse:
        """Parse natural language shopping prompt."""
        return GoalParser.parse_goal(payload)

    @classmethod
    async def generate_shopping_plan(
        cls,
        payload: PlanGenerationRequest,
        db: Optional[AsyncSession] = None,
        user_id: Optional[UUID] = None,
    ) -> PlanGenerationResponse:
        """Generate complete goal-driven shopping setup plan."""
        parsed = GoalParser.parse_goal(GoalParseRequest(prompt=payload.prompt))
        target_budget = payload.budget or parsed.extracted_budget
        scenario = payload.scenario_type or parsed.scenario_type

        raw_items = ShoppingPlanner.generate_category_items(scenario, target_budget)
        opt_items, allocated, remaining = BudgetOptimizer.optimize_allocations(
            raw_items, target_budget
        )
        comp_score, _ = CompatibilityEngine.evaluate_compatibility(opt_items)

        return PlanGenerationResponse(
            goal_title=parsed.goal_title,
            scenario_type=scenario,
            total_budget=target_budget,
            allocated_budget=allocated,
            remaining_budget=remaining,
            compatibility_score=comp_score,
            items=opt_items,
        )

    @classmethod
    async def simulate_plan(
        cls,
        payload: PlanSimulationRequest,
    ) -> PlanGenerationResponse:
        """Re-simulate shopping plan setup."""
        return SimulationEngine.re_simulate_plan(payload)

    @classmethod
    async def process_conversation(
        cls,
        payload: PlanConversationRequest,
    ) -> PlanGenerationResponse:
        """Process conversational follow-up modification."""
        return ConversationManager.process_followup_message(payload)

    @classmethod
    async def export_plan_report(
        cls,
        plan: PlanGenerationResponse,
        export_format: str = "JSON",
    ) -> PlanExportResponse:
        """Export plan report."""
        return ReportGenerator.generate_report(plan, export_format)
