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
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str
    role: Optional[str] = Field(default="user", pattern="^(user|admin)$")


class RefreshTokenRequest(BaseModel):
    """Token Refresh Request."""

    refresh_token: str
