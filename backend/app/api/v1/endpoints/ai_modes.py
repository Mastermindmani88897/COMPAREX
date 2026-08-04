"""
COMPAREX Backend – Advanced AI Modes API Endpoint

Exposes endpoints for listing and selecting the 9 specialized AI mode profiles.
"""

from typing import List

from fastapi import APIRouter

from app.schemas.ai_modes import AIModeDefinition, AIModeSelectRequest, AIModeSelectResponse
from app.schemas.common import SuccessResponse
from app.services.ai_mode_service import AIModeService

router = APIRouter(prefix="/ai/modes", tags=["Advanced AI Modes"])


@router.get(
    "",
    response_model=SuccessResponse[List[AIModeDefinition]],
    summary="List All 9 Advanced AI Modes",
    description="Lists all 9 specialized AI modes (Budget, Performance, Premium, Gaming, etc.).",
)
async def list_ai_modes():
    """List AI mode profiles."""
    res = AIModeService.list_modes()
    return SuccessResponse(message="AI modes retrieved successfully", data=res)


@router.post(
    "/select",
    response_model=SuccessResponse[AIModeSelectResponse],
    summary="Select Active AI Mode",
    description="Select or switch active AI mode profile for recommendation tuning.",
)
async def select_ai_mode(payload: AIModeSelectRequest):
    """Select active AI mode."""
    res = AIModeService.select_mode(payload)
    return SuccessResponse(message="AI mode updated successfully", data=res)
