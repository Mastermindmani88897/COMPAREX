"""
COMPAREX Backend – Auth Service

Orchestrates user registration, authentication, token issuance, token refresh, and logout.
"""

import re
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
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import GoogleAuthRequest, LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserPublic

logger = get_logger(__name__)


class AuthService:
    """Service handling user authentication & token management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    def _build_user_public(self, user: User, force_needs_setup: bool = False) -> UserPublic:
        """Construct UserPublic DTO with needs_username_setup state."""
        u = UserPublic.model_validate(user)
        is_legacy = bool(
            user.username
            and user.username.lower().startswith("user1")
            and len(user.username) > 10
        )
        u.needs_username_setup = force_needs_setup or not user.username or is_legacy
        return u

    async def register(self, req: RegisterRequest) -> UserPublic:
        """Register a new user account."""
        display_name = (req.name or req.full_name or "").strip()
        if not display_name:
            display_name = req.email.split("@")[0].capitalize()

        confirm_pw = req.confirm_password or req.confirmPassword or req.password
        if req.password != confirm_pw:
            logger.warning("Registration failed for %s: Passwords do not match", req.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match.",
            )

        if await self.user_repo.email_exists(req.email):
            logger.warning(
                "Registration failed for %s: Email address already registered", req.email
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already registered.",
            )

        # Username generation / validation
        target_username = (req.username or display_name).strip()
        if req.username:
            if await self.user_repo.username_exists(target_username):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="That username is already taken. Please choose another.",
                )
        else:
            # Auto-generate unique username fallback
            base_un = re.sub(r"[^A-Za-z0-9_]", "_", target_username).strip("_") or "user"
            candidate_un = base_un
            counter = 1
            while await self.user_repo.username_exists(candidate_un):
                candidate_un = f"{base_un}_{counter}"
                counter += 1
            target_username = candidate_un

        try:
            hashed_pw = hash_password(req.password)
            user_data = {
                "email": req.email.lower(),
                "name": display_name,
                "username": target_username,
                "hashed_password": hashed_pw,
                "role": req.role or "user",
                "is_active": True,
                "is_verified": False,
            }

            user = await self.user_repo.create(user_data)
            logger.info("New user registered successfully: %s (ID: %s)", user.email, user.id)
            return self._build_user_public(user)
        except Exception as exc:
            await self.db.rollback()
            logger.error("Database error during user registration for %s: %s", req.email, exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed due to a server error. Please try again.",
            )

    async def login(self, req: LoginRequest) -> TokenResponse:
        """Authenticate user credentials and issue access/refresh tokens."""
        user = await self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            logger.warning("Login failed for %s: Invalid credentials", req.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.warning("Login failed for %s: Account inactive", req.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive.",
            )

        access_token = create_access_token(subject=str(user.id), role=user.role)
        refresh_token = create_refresh_token(subject=str(user.id), role=user.role)

        logger.info("User logged in: %s", user.email)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=self._build_user_public(user),
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
            user=self._build_user_public(user),
        )

    async def google_authenticate(self, req: GoogleAuthRequest) -> TokenResponse:
        """Authenticate user via Google OAuth using stable identity sub/google_id."""
        email = (req.email or "").lower().strip()
        google_id = req.google_id or f"google_{hash(email)}"

        # Extract Google profile name
        # Priority: full_name/name -> given_name + family_name -> email prefix
        raw_name = (req.full_name or req.name or "").strip()
        if not raw_name and (req.given_name or req.family_name):
            raw_name = f"{req.given_name or ''} {req.family_name or ''}".strip()

        if raw_name and raw_name.lower() != "google user":
            display_name = raw_name
        elif email and "@" in email:
            display_name = email.split("@")[0].capitalize()
        else:
            display_name = "User"

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required for Google OAuth authentication",
            )

        # 1. Check if user exists by google_id or email
        user = await self.user_repo.get_by_google_id(google_id)
        if not user:
            user = await self.user_repo.get_by_email(email)

        is_new_user = False
        if user:
            update_fields = {}
            if not user.google_id:
                update_fields["google_id"] = google_id
            if req.avatar_url and not user.avatar_url:
                update_fields["avatar_url"] = req.avatar_url
            if user.login_provider != "google":
                update_fields["login_provider"] = "google"
            if display_name and (user.name.lower() == "google user" or user.name == "User"):
                update_fields["name"] = display_name
            if not user.username:
                # Derive clean initial username from display name
                base_un = re.sub(r"[^A-Za-z0-9_]", "_", display_name).strip("_") or "user"
                candidate = base_un
                cnt = 1
                while await self.user_repo.username_exists(candidate):
                    candidate = f"{base_un}_{cnt}"
                    cnt += 1
                update_fields["username"] = candidate

            if update_fields:
                user = await self.user_repo.update(user, update_fields)
            logger.info("Existing user logged in via Google OAuth: %s", user.email)
        else:
            # 2. Auto-create new user for Google OAuth
            is_new_user = True
            base_un = re.sub(r"[^A-Za-z0-9_]", "_", display_name).strip("_") or "user"
            candidate = base_un
            cnt = 1
            while await self.user_repo.username_exists(candidate):
                candidate = f"{base_un}_{cnt}"
                cnt += 1

            user_data = {
                "email": email,
                "name": display_name,
                "username": candidate,
                "google_id": google_id,
                "login_provider": "google",
                "avatar_url": req.avatar_url,
                "hashed_password": None,
                "role": "user",
                "is_active": True,
                "is_verified": True,
            }
            user = await self.user_repo.create(user_data)
            logger.info(
                "New account created via Google OAuth: %s (ID: %s)", user.email, user.id
            )

        access_token = create_access_token(subject=str(user.id), role=user.role)
        refresh_token = create_refresh_token(subject=str(user.id), role=user.role)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=self._build_user_public(user, force_needs_setup=is_new_user),
        )

    async def setup_username(self, user: User, new_username: str) -> UserPublic:
        """Validate and set a user's unique username."""
        clean_un = (new_username or "").strip()
        if len(clean_un) < 3 or len(clean_un) > 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be between 3 and 30 characters.",
            )

        if not re.match(r"^[A-Za-z0-9_ -]+$", clean_un):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Username can only contain letters, numbers, spaces, underscores, or hyphens."
                ),
            )

        reserved_names = {
            "admin",
            "administrator",
            "system",
            "root",
            "api",
            "auth",
            "support",
            "comparex",
            "null",
            "undefined",
        }
        if clean_un.lower() in reserved_names:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This username is reserved. Please choose another.",
            )

        existing = await self.user_repo.get_by_username(clean_un)
        if existing and existing.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="That username is already taken. Please choose another.",
            )

        updated_user = await self.user_repo.update(user, {"username": clean_un, "name": clean_un})
        logger.info("Username updated for user %s: %s", user.id, clean_un)
        return self._build_user_public(updated_user, force_needs_setup=False)
