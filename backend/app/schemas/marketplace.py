"""
COMPAREX Backend – Marketplace Pydantic Schemas
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MarketplaceBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    base_url: str
    logo_url: Optional[str] = None
    is_active: bool = True
    country_code: str = Field(default="IN", max_length=10)


class MarketplaceCreate(MarketplaceBase):
    pass


class MarketplaceUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None


class MarketplacePublic(MarketplaceBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
