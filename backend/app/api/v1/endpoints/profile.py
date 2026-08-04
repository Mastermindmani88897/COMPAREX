"""
COMPAREX Backend – Shopping Profile & Preferences API Endpoints

Opt-in learning consent configuration, budget bounds, and profile controls.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.profile import ShoppingProfileCreate, ShoppingProfileResponse
from app.services.profile_service import ShoppingProfileService

router = APIRouter(tags=["Personal Shopping Profile"])


@router.get(
    "/profile",
    response_model=SuccessResponse[ShoppingProfileResponse],
    summary="Get User Shopping Profile",
    description="Retrieve user opt-in learning consent and shopping preferences.",
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve shopping profile."""
    res = await ShoppingProfileService.get_or_create_profile(db, current_user.id)
    return SuccessResponse(message="Shopping profile retrieved successfully", data=res)


@router.put(
    "/profile",
    response_model=SuccessResponse[ShoppingProfileResponse],
    summary="Update User Shopping Profile",
    description="Configure opt-in learning consent, preferred brands, and budget bounds.",
)
async def update_profile(
    payload: ShoppingProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update shopping profile."""
    res = await ShoppingProfileService.update_profile(db, current_user.id, payload)
    return SuccessResponse(message="Shopping profile updated successfully", data=res)


@router.post(
    "/preferences/reset",
    response_model=SuccessResponse[ShoppingProfileResponse],
    summary="Reset Preferences",
    description="Reset profile to default non-personalized state.",
)
async def reset_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reset shopping preferences."""
    res = await ShoppingProfileService.reset_profile(db, current_user.id)
    return SuccessResponse(message="Shopping preferences reset successfully", data=res)
