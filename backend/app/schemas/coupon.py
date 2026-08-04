"""
COMPAREX Backend – Coupon Schemas

Pydantic models for coupon discovery, validation, auto-apply, and offer details.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CouponResponse(BaseModel):
    """Public coupon item response schema."""

    id: Optional[UUID] = None
    code: str
    marketplace_slug: str
    title: str
    description: Optional[str] = None
    discount_type: str = "PERCENTAGE"
    discount_value: float
    min_order_value: float = 0.0
    max_discount_amount: Optional[float] = None
    offer_type: str = "COUPON"
    bank_name: Optional[str] = None
    confidence_score: float = 0.95
    is_active: bool = True
    model_config = ConfigDict(from_attributes=True)


class CouponValidationRequest(BaseModel):
    """Payload to validate a coupon against product cart."""

    code: str
    marketplace_slug: str
    order_amount: float = Field(gt=0)


class CouponValidationResponse(BaseModel):
    """Validation response for promo coupon code."""

    code: str
    is_valid: bool
    discount_amount: float
    final_price: float
    savings_message: str


class AutoApplyCouponsRequest(BaseModel):
    """Request payload to discover and test best coupons."""

    marketplace_slug: str
    cart_total: float = Field(gt=0)
    category: Optional[str] = None


class AutoApplyCouponsResponse(BaseModel):
    """Summary response for auto-applied best coupons."""

    marketplace_slug: str
    original_price: float
    best_coupon_code: Optional[str] = None
    max_savings: float
    final_price: float
    applied_coupons: List[CouponResponse] = Field(default_factory=list)
    cashback_available: Optional[str] = None
    bank_offers: List[str] = Field(default_factory=list)
    wallet_offers: List[str] = Field(default_factory=list)
