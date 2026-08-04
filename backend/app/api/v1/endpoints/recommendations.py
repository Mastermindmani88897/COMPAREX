"""
COMPAREX Backend – Personalized Recommendations API Endpoint

Combines verified database data, profile bounds, DNA, and deal scores.
"""

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.services.personalized_recommendation_service import PersonalizedRecommendationService

router = APIRouter(prefix="/recommendations", tags=["Personalized Recommendation Engine"])


@router.get(
    "/personalized",
    response_model=SuccessResponse[Any],
    summary="Get Personalized Product Recommendations",
    description="Generate grounded product recommendations combining profile and DNA.",
)
async def get_personalized_recommendations(
    query: str = Query(..., description="Product query string"),
    category: Optional[str] = Query(None, description="Category filter"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve personalized product recommendations."""
    res = await PersonalizedRecommendationService.get_personalized_recommendations(
        db=db,
        user_id=current_user.id,
        query=query,
        category=category,
    )
    return SuccessResponse(message="Personalized recommendations generated", data=res)
