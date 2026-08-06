"""
COMPAREX Backend - Wishlist Pydantic Schemas
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.product import ProductPublic


class WishlistItemCreate(BaseModel):
    """Payload to add a product to wishlist."""

    product_id: uuid.UUID | str
    preferred_marketplace: Optional[str] = "Amazon"
    target_price: Optional[Decimal] = None
    notes: Optional[str] = None


class WishlistItemUpdate(BaseModel):
    """Payload to update an existing wishlist item."""

    preferred_marketplace: Optional[str] = None
    target_price: Optional[Decimal] = None
    notes: Optional[str] = None


class WishlistItemPublic(BaseModel):
    """Public Wishlist item response."""

    id: uuid.UUID
    user_id: uuid.UUID
    product_id: uuid.UUID
    preferred_marketplace: Optional[str] = "Amazon"
    target_price: Optional[Decimal] = None
    current_price: Optional[Decimal] = None
    savings: Optional[Decimal] = None
    price_drop_alert: bool = False
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    product: Optional[ProductPublic] = None

    model_config = {"from_attributes": True}


class WishlistResponse(BaseModel):
    """Aggregated Wishlist payload with items & AI recommendations."""

    total_items: int
    total_savings: Decimal
    items: List[WishlistItemPublic]
    ai_recommendations: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=lambda: {
            "you_may_also_like": [],
            "cheaper_alternative": [],
            "best_value": [],
        }
    )
