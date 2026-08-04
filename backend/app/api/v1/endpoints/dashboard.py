"""
COMPAREX Backend – User Dashboard Summary API Endpoint

Aggregates wishlist, price alerts, coupon savings, and shopping statistics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Shopping Dashboard"])


@router.get(
    "/summary",
    response_model=SuccessResponse[DashboardSummaryResponse],
    summary="Get User Shopping Dashboard Summary",
    description="Retrieve aggregated shopping statistics, watchlist, active alerts, and savings.",
)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve complete user shopping dashboard overview."""
    res = await DashboardService.get_user_dashboard(db, current_user.id)
    return SuccessResponse(message="Dashboard summary retrieved successfully", data=res)
