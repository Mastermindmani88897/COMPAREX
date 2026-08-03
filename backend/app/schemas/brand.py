"""
COMPAREX Backend – Brand DTO Schemas
"""

import uuid
from pydantic import BaseModel, ConfigDict


class BrandBase(BaseModel):
    name: str
    slug: str
    logo_url: str | None = None
    website_url: str | None = None


class BrandCreate(BrandBase):
    pass


class BrandPublic(BrandBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
