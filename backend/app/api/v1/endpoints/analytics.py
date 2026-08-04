"""
COMPAREX Backend – Shopping Analytics API Endpoint

Provides user savings analytics, discount metrics, and recommendation accuracy stats.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.analytics import ShoppingAnalyticsResponse
from app.schemas.common import SuccessResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Shopping Analytics Dashboard"])


@router.get(
    "",
    response_model=SuccessResponse[ShoppingAnalyticsResponse],
    summary="Get User Shopping Analytics",
    description="Retrieve monthly and yearly savings stats and recommendation accuracy.",
)
async def get_analytics(
    month_year: Optional[str] = Query("2026-08", description="Month string e.g. 2026-08"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve analytics."""
    res = await AnalyticsService.get_user_analytics(db, current_user.id, month_year or "2026-08")
    return SuccessResponse(message="Shopping analytics retrieved successfully", data=res)
