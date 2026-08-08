"""
COMPAREX Backend – User Management API Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.user import UserPublic, UserUpdate, UsernameSetupRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=SuccessResponse[UserPublic],
    summary="Get Current User Profile",
    description="Retrieve profile details for current user.",
)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get profile endpoint."""
    service = UserService(db)
    profile = await service.get_profile(current_user)
    return SuccessResponse(
        message="User profile retrieved",
        data=profile,
    )


@router.patch(
    "/me",
    response_model=SuccessResponse[UserPublic],
    summary="Update Profile",
    description="Update profile information for current user.",
)
async def update_my_profile(
    req: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile endpoint."""
    service = UserService(db)
    updated_profile = await service.update_profile(current_user, req)
    return SuccessResponse(
        message="Profile updated successfully",
        data=updated_profile,
    )


@router.post(
    "/me/username",
    response_model=SuccessResponse[UserPublic],
    summary="Setup / Update Username",
    description="Set or update the user's unique username.",
)
async def setup_username(
    req: UsernameSetupRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Setup username endpoint."""
    from app.services.auth_service import AuthService
    auth_service = AuthService(db)
    updated_user = await auth_service.setup_username(current_user, req.username)
    return SuccessResponse(
        message="Username updated successfully",
        data=updated_user,
    )


@router.delete(
    "/me",
    response_model=SuccessResponse[None],
    summary="Delete User Account",
    description="Delete account for the currently authenticated user.",
)
async def delete_my_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete account endpoint."""
    service = UserService(db)
    await service.delete_account(current_user)
    return SuccessResponse(
        message="Account deleted successfully",
        data=None,
    )
