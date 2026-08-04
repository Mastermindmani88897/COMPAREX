"""
COMPAREX Backend - Brand Pydantic Schemas
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BrandBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    logo_url: Optional[str] = None
    website_url: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    logo_url: Optional[str] = None
    website_url: Optional[str] = None


class BrandPublic(BrandBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
