"""
COMPAREX Backend – Product Pydantic Schemas
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    ean: Optional[str] = None
    base_price: Optional[float] = Field(None, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    ean: Optional[str] = None
    base_price: Optional[float] = Field(None, ge=0)


class ProductPublic(ProductBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
