"""
COMPAREX Backend – ConversationManager Sub-Service

Handles multi-turn natural language planning edits (e.g. 'Replace monitor', 'Reduce cost by 8k').
"""

from typing import List

from app.schemas.planner import CategoryPlanItem, PlanConversationRequest, PlanGenerationResponse
from app.services.planner.budget_optimizer import BudgetOptimizer


class ConversationManager:
    """Follow-Up Conversational Shopping Planning Manager."""

    @classmethod
    def process_followup_message(
        cls,
        payload: PlanConversationRequest,
    ) -> PlanGenerationResponse:
        """Update existing shopping plan based on conversational user instruction."""
        text = payload.message.lower()
        plan = payload.current_plan.model_copy()
        items: List[CategoryPlanItem] = [item.model_copy() for item in plan.items]

        if "reduce" in text or "cheaper" in text or "cut" in text:
            for item in items:
                if item.requirement_level != "REQUIRED":
                    item.price = round(item.price * 0.85, 2)
        elif "amazon" in text:
            for item in items:
                item.marketplace_name = "Amazon India"
        elif "remove" in text:
            words = text.split()
            for item in items:
                if any(w in item.category_name.lower() for w in words):
                    item.is_selected = False

        opt_items, allocated, remaining = BudgetOptimizer.optimize_allocations(
            items, plan.total_budget
        )
        plan.items = opt_items
        plan.allocated_budget = allocated
        plan.remaining_budget = remaining

        return plan
