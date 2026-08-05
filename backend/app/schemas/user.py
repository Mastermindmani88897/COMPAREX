"""
COMPAREX Backend – User Pydantic Schemas
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str
    role: Optional[str] = Field(default="user", pattern="^(user|admin)$")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar_url: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(user|admin)$")


class UserPublic(UserBase):
    """User data safe to expose in API responses."""

    id: uuid.UUID
    avatar_url: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    is_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserInDB(UserPublic):
    """User data including sensitive fields (internal use only)."""

    hashed_password: str
    is_superuser: bool
