"""
COMPAREX Backend – Authentication Pydantic Schemas
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserPublic


class TokenResponse(BaseModel):
    """JWT Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds
    user: UserPublic


class LoginRequest(BaseModel):
    """User Login Request."""

    email: EmailStr
    password: str = Field(min_length=1)


class RegisterRequest(BaseModel):
    """User Registration Request."""

    email: EmailStr
    name: Optional[str] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: Optional[str] = None
    confirmPassword: Optional[str] = None
    role: Optional[str] = Field(default="user", pattern="^(user|admin)$")


class RefreshTokenRequest(BaseModel):
    """Token Refresh Request."""

    refresh_token: str


class GoogleAuthRequest(BaseModel):
    """Google OAuth Request Schema."""

    id_token: Optional[str] = None
    access_token: Optional[str] = None
    google_id: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    full_name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    avatar_url: Optional[str] = None
