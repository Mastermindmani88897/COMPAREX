"""
COMPAREX Backend – Auth Service

Orchestrates user registration, authentication, token issuance, token refresh, and logout.
"""

import time
from uuid import UUID

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.core.redis import redis_client
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserPublic

logger = get_logger(__name__)


class AuthService:
    """Service handling user authentication & token management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, req: RegisterRequest) -> UserPublic:
        """Register a new user account."""
        if req.password != req.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match",
            )

        if await self.user_repo.email_exists(req.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address is already registered",
            )

        hashed_pw = hash_password(req.password)
        user_data = {
            "email": req.email.lower(),
            "name": req.name,
            "hashed_password": hashed_pw,
            "role": req.role or "user",
            "is_active": True,
            "is_verified": False,
        }

        user = await self.user_repo.create(user_data)
        logger.info("New user registered: %s (ID: %s)", user.email, user.id)
        return UserPublic.model_validate(user)

    async def login(self, req: LoginRequest) -> TokenResponse:
        """Authenticate user credentials and issue access/refresh tokens."""
        user = await self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive",
            )

        access_token = create_access_token(subject=str(user.id), role=user.role)
        refresh_token = create_refresh_token(subject=str(user.id), role=user.role)

        logger.info("User logged in: %s", user.email)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserPublic.model_validate(user),
        )

    async def logout(self, token: str) -> None:
        """Logout user by adding current access token to Redis blacklist."""
        try:
            payload = decode_token(token)
            exp = payload.get("exp")
            if exp:
                remaining = int(exp - time.time())
                if remaining > 0:
                    await redis_client.set(
                        f"token_blacklist:{token}", "1", expire_seconds=remaining
                    )
            else:
                await redis_client.set(f"token_blacklist:{token}", "1", expire_seconds=86400)
        except JWTError:
            pass

    async def refresh_token(self, refresh_token_str: str) -> TokenResponse:
        """Validate refresh token and issue new token pair."""
        try:
            payload = decode_token(refresh_token_str)
            user_id_str = payload.get("sub")
            token_type = payload.get("type")

            if not user_id_str or token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired or invalid refresh token",
            )

        user = await self.user_repo.get_by_id(UUID(user_id_str))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        new_access_token = create_access_token(subject=str(user.id), role=user.role)
        new_refresh_token = create_refresh_token(subject=str(user.id), role=user.role)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserPublic.model_validate(user),
        )
