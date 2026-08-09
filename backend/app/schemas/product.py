"""
COMPAREX Backend – Product Pydantic Schemas
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import inspect as sa_inspect


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    ean: Optional[str] = None
    base_price: Optional[float] = Field(None, ge=0)
    rating: Optional[float] = Field(4.5, ge=0, le=5)
    review_count: Optional[int] = Field(0, ge=0)
    popularity_score: Optional[float] = Field(0.0, ge=0)
    search_keywords: Optional[str] = None
    stock_status: Optional[str] = "in_stock"
    discount_percentage: Optional[float] = 0.0
    is_quarantined: Optional[bool] = False
    is_verified: Optional[bool] = True


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
    rating: Optional[float] = None
    review_count: Optional[int] = None
    popularity_score: Optional[float] = None
    search_keywords: Optional[str] = None
    stock_status: Optional[str] = None
    discount_percentage: Optional[float] = None


class ProductImageSchema(BaseModel):
    id: Optional[uuid.UUID] = None
    url: str
    alt_text: Optional[str] = None
    is_primary: bool = False

    model_config = {"from_attributes": True}


class ProductPublic(ProductBase):
    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    images: Optional[list[ProductImageSchema]] = []

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def prepare_orm(cls, data: Any) -> Any:
        if hasattr(data, "__table__"):
            try:
                state = sa_inspect(data)
                d = {}
                for c in state.mapper.column_attrs:
                    try:
                        d[c.key] = getattr(data, c.key)
                    except Exception:
                        d[c.key] = None

                if hasattr(state, "unloaded") and "images" in state.unloaded:
                    d["images"] = []
                else:
                    try:
                        imgs = getattr(data, "images", [])
                        d["images"] = (
                            [ProductImageSchema.model_validate(img) for img in imgs] if imgs else []
                        )
                    except Exception:
                        d["images"] = []
                return d
            except Exception:
                pass
        return data
