"""
COMPAREX Backend – Smart Coupon API Endpoints

Offers discovery, coupon validation, auto-apply, and bank/wallet deals.
"""

from typing import List, Optional

from fastapi import APIRouter, Query

from app.schemas.common import SuccessResponse
from app.schemas.coupon import (
    AutoApplyCouponsRequest,
    AutoApplyCouponsResponse,
    CouponResponse,
    CouponValidationRequest,
    CouponValidationResponse,
)
from app.services.coupon_service import CouponEngineService

router = APIRouter(prefix="/coupons", tags=["Smart Coupon Engine"])


@router.get(
    "/discover",
    response_model=SuccessResponse[List[CouponResponse]],
    summary="Discover Active Marketplace Coupons",
    description="Discover active coupons and bank offers filtered by marketplace and category.",
)
async def discover_coupons(
    marketplace_slug: Optional[str] = Query(None, description="Filter by marketplace"),
    category: Optional[str] = Query(None, description="Filter by product category"),
):
    """Discover available coupons and cashback offers."""
    res = await CouponEngineService.discover_coupons(marketplace_slug, category)
    return SuccessResponse(message="Available coupons retrieved successfully", data=res)


@router.post(
    "/validate",
    response_model=SuccessResponse[CouponValidationResponse],
    summary="Validate Coupon Code",
    description="Validate promo coupon code against cart amount and constraints.",
)
async def validate_coupon(payload: CouponValidationRequest):
    """Validate coupon code."""
    res = await CouponEngineService.validate_coupon(payload)
    return SuccessResponse(message="Coupon validation completed", data=res)


@router.post(
    "/auto-apply",
    response_model=SuccessResponse[AutoApplyCouponsResponse],
    summary="Auto-Apply Best Coupons for Max Savings",
    description="Finds and auto-applies best available coupon for maximum discount savings.",
)
async def auto_apply_coupons(payload: AutoApplyCouponsRequest):
    """Auto-apply best coupon and bank offers."""
    res = await CouponEngineService.auto_apply(payload)
    return SuccessResponse(message="Auto-apply coupon execution completed", data=res)
