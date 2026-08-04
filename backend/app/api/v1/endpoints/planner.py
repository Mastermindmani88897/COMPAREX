"""
COMPAREX Backend – AI Marketplace Planner API Endpoints

Endpoints for parsing shopping goals, generating plans, simulating, follow-up, and exporting.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.planner import (
    GoalParseRequest,
    GoalParseResponse,
    PlanConversationRequest,
    PlanExportResponse,
    PlanGenerationRequest,
    PlanGenerationResponse,
    PlanSimulationRequest,
)
from app.services.planner.planner_orchestrator import PlannerOrchestrator

router = APIRouter(prefix="/planner", tags=["Flagship AI Marketplace Planner"])


@router.post(
    "/parse-goal",
    response_model=SuccessResponse[GoalParseResponse],
    summary="Parse Natural Language Shopping Goal",
    description="Extract goal title, scenario, budget, and priorities from prompt.",
)
async def parse_goal(payload: GoalParseRequest):
    """Parse shopping goal prompt."""
    res = await PlannerOrchestrator.parse_goal_prompt(payload)
    return SuccessResponse(message="Goal prompt parsed successfully", data=res)


@router.post(
    "/generate-plan",
    response_model=SuccessResponse[PlanGenerationResponse],
    summary="Generate Full Multi-Category Shopping Setup Plan",
    description="Generate goal-driven shopping setup plan with category budget allocation.",
)
async def generate_plan(
    payload: PlanGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate shopping plan."""
    res = await PlannerOrchestrator.generate_shopping_plan(
        payload=payload,
        db=db,
        user_id=current_user.id,
    )
    return SuccessResponse(message="Shopping setup plan generated successfully", data=res)


@router.post(
    "/simulate",
    response_model=SuccessResponse[PlanGenerationResponse],
    summary="Re-Simulate Shopping Plan Setup",
    description="Recalculate plan setup for user target budget or marketplace filter.",
)
async def simulate_plan(payload: PlanSimulationRequest):
    """Simulate plan setup."""
    res = await PlannerOrchestrator.simulate_plan(payload)
    return SuccessResponse(message="Plan re-simulated successfully", data=res)


@router.post(
    "/conversation",
    response_model=SuccessResponse[PlanGenerationResponse],
    summary="Conversational Plan Editing",
    description="Process follow-up natural language plan edits e.g. 'Replace monitor'.",
)
async def process_conversation(payload: PlanConversationRequest):
    """Process follow-up conversational edit."""
    res = await PlannerOrchestrator.process_conversation(payload)
    return SuccessResponse(message="Plan updated from conversation", data=res)


@router.post(
    "/export",
    response_model=SuccessResponse[PlanExportResponse],
    summary="Export Shopping Plan Report",
    description="Export shopping plan report in JSON, CSV, or printable PDF HTML formats.",
)
async def export_plan(
    plan: PlanGenerationResponse,
    export_format: Optional[str] = Query("JSON", description="JSON, CSV, PDF_HTML"),
):
    """Export plan report."""
    res = await PlannerOrchestrator.export_plan_report(plan, export_format or "JSON")
    return SuccessResponse(message="Plan report exported successfully", data=res)
