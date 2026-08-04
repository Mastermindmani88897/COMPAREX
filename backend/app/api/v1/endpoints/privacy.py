"""
COMPAREX Backend – Smart Privacy Center API Endpoints

Export user data, purge AI memories, and manage opt-in learning consent.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.services.privacy_service import SmartPrivacyService

router = APIRouter(prefix="/privacy", tags=["Smart Privacy Center"])


@router.get(
    "/export",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="Export All User Personal Data",
    description="Export user profile preferences and memories as JSON.",
)
async def export_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export all user data."""
    res = await SmartPrivacyService.export_all_user_data(db, current_user.id)
    return SuccessResponse(message="Personal data exported successfully", data=res)


@router.delete(
    "/purge",
    response_model=SuccessResponse[Dict[str, str]],
    summary="Purge All AI Memory & Learned Context",
    description="Permanently delete all AI interaction memories and preferences.",
)
async def purge_ai_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Purge all user AI data."""
    res = await SmartPrivacyService.purge_all_ai_data(db, current_user.id)
    return SuccessResponse(message="AI memory and preferences purged", data=res)
