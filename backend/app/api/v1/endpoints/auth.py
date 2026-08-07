"""
COMPAREX Backend – Authentication API Endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import oauth2_scheme
from app.db.session import get_db
from app.schemas.auth import (
    GoogleAuthRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.common import SuccessResponse
from app.schemas.user import UserPublic
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=SuccessResponse[UserPublic],
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Register a new user account with email, password, and name.",
)
async def register(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register user endpoint."""
    auth_service = AuthService(db)
    user_public = await auth_service.register(req)
    return SuccessResponse(
        message="User registered successfully",
        data=user_public,
    )


@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
    summary="User Login",
    description="Authenticate user with email and password. Returns access and refresh JWT tokens.",
)
async def login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Login user endpoint."""
    auth_service = AuthService(db)
    token_response = await auth_service.login(req)
    return SuccessResponse(
        message="Login successful",
        data=token_response,
    )


@router.post(
    "/logout",
    response_model=SuccessResponse[None],
    summary="User Logout",
    description="Logout current user and invalidate access token via Redis token blacklist.",
)
async def logout(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Logout endpoint."""
    auth_service = AuthService(db)
    await auth_service.logout(token)
    return SuccessResponse(
        message="Successfully logged out",
        data=None,
    )


@router.post(
    "/refresh",
    response_model=SuccessResponse[TokenResponse],
    summary="Refresh Access Token",
    description="Issue a new pair of access and refresh tokens using a valid refresh token.",
)
async def refresh_token(
    req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh token endpoint."""
    auth_service = AuthService(db)
    token_response = await auth_service.refresh_token(req.refresh_token)
    return SuccessResponse(
        message="Token refreshed successfully",
        data=token_response,
    )


@router.post(
    "/google",
    response_model=SuccessResponse[TokenResponse],
    summary="Google OAuth Authentication",
    description="Authenticate or auto-create account using Google OAuth ID token or user payload.",
)
async def google_auth(
    req: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """Google OAuth login/register endpoint."""
    auth_service = AuthService(db)
    token_response = await auth_service.google_authenticate(req)
    return SuccessResponse(
        message="Google authentication successful",
        data=token_response,
    )
