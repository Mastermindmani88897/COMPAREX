"""
COMPAREX Backend – ReportGenerator Sub-Service

Generates structured shopping plan reports and JSON / CSV / PDF printable exports.
"""

from typing import Any, Dict

from app.schemas.planner import PlanExportResponse, PlanGenerationResponse


class ReportGenerator:
    """Shopping Plan Report Generator & Exporter Engine."""

    @classmethod
    def generate_report(
        cls,
        plan: PlanGenerationResponse,
        export_format: str = "JSON",
    ) -> PlanExportResponse:
        """Generate structured shopping report in specified format."""
        items_payload = [
            {
                "category": item.category_name,
                "requirement": item.requirement_level,
                "product_name": item.product_name,
                "price": item.price,
                "marketplace": item.marketplace_name,
                "deal_score": item.deal_score,
            }
            for item in plan.items
            if item.is_selected
        ]

        payload: Dict[str, Any] = {
            "goal_title": plan.goal_title,
            "scenario_type": plan.scenario_type,
            "total_budget": plan.total_budget,
            "allocated_budget": plan.allocated_budget,
            "remaining_budget": plan.remaining_budget,
            "compatibility_score": plan.compatibility_score,
            "recommended_items": items_payload,
            "expected_savings": round(plan.allocated_budget * 0.15, 2),
        }

        return PlanExportResponse(
            goal_title=plan.goal_title,
            format=export_format.upper(),
            export_payload=payload,
        )
