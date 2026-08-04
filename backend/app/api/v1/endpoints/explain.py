"""
COMPAREX Backend – Explainable AI & CompareX Explain API Endpoint

Provides transparent AI reasoning breakdowns and 'Why not Product B?' comparisons.
"""

from fastapi import APIRouter

from app.schemas.common import SuccessResponse
from app.schemas.explain import CompareExplainRequest, CompareExplainResponse
from app.services.explainable_ai_service import ExplainableAIService

router = APIRouter(prefix="/explain", tags=["Explainable AI Engine"])


@router.post(
    "/compare",
    response_model=SuccessResponse[CompareExplainResponse],
    summary="CompareX Explain - Why Product A over Product B?",
    description="Explains why Product A was ranked higher than Product B with attribute analysis.",
)
async def explain_comparison(payload: CompareExplainRequest):
    """Explain comparison ranking between Product A and Product B."""
    res = await ExplainableAIService.explain_comparison(payload)
    return SuccessResponse(message="Comparison explanation generated", data=res)
