"""
COMPAREX Backend – BudgetOptimizer Sub-Service

Intelligently allocates target budget across required and recommended product categories.
"""

from typing import List, Tuple

from app.schemas.planner import CategoryPlanItem


class BudgetOptimizer:
    """Intelligent Budget Allocation Engine."""

    @classmethod
    def optimize_allocations(
        cls,
        items: List[CategoryPlanItem],
        total_budget: float,
    ) -> Tuple[List[CategoryPlanItem], float, float]:
        """Distribute budget intelligently and return updated items, allocated, and buffer."""
        current_sum = sum(item.price for item in items if item.is_selected)

        if current_sum > total_budget and total_budget > 0:
            scale_factor = total_budget / current_sum
            for item in items:
                if item.is_selected and item.requirement_level != "REQUIRED":
                    item.price = round(item.price * scale_factor, 2)

        allocated = sum(item.price for item in items if item.is_selected)
        remaining = max(0.0, total_budget - allocated)

        return items, round(allocated, 2), round(remaining, 2)
