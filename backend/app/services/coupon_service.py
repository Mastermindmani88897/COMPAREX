"""
COMPAREX Backend – Smart Coupon Engine Service

Discovers, validates, and auto-applies marketplace coupons and bank/wallet offers.
"""

from typing import List, Optional

from app.schemas.coupon import (
    AutoApplyCouponsRequest,
    AutoApplyCouponsResponse,
    CouponResponse,
    CouponValidationRequest,
    CouponValidationResponse,
)


class CouponEngineService:
    """Smart Coupon & Offer Discovery Engine Service."""

    MOCK_COUPONS = [
        CouponResponse(
            code="COMPAREX10",
            marketplace_slug="amazon",
            title="10% Instant Discount on Electronics",
            description="Applicable on orders above ₹5,000",
            discount_type="PERCENTAGE",
            discount_value=10.0,
            min_order_value=5000.0,
            max_discount_amount=1500.0,
            offer_type="COUPON",
            confidence_score=0.98,
        ),
        CouponResponse(
            code="HDFC500",
            marketplace_slug="flipkart",
            title="₹500 Instant Cashback via HDFC Bank Cards",
            description="Flat discount on credit/debit card transactions",
            discount_type="FLAT",
            discount_value=500.0,
            min_order_value=2000.0,
            offer_type="BANK_OFFER",
            bank_name="HDFC Bank",
            confidence_score=0.95,
        ),
        CouponResponse(
            code="FASHION15",
            marketplace_slug="myntra",
            title="15% Off Fashion & Apparel",
            description="Valid on select Myntra catalog items",
            discount_type="PERCENTAGE",
            discount_value=15.0,
            min_order_value=1500.0,
            max_discount_amount=750.0,
            offer_type="COUPON",
            confidence_score=0.92,
        ),
        CouponResponse(
            code="PAYTM50",
            marketplace_slug="croma",
            title="₹50 Cashback on Paytm Wallet",
            description="Minimum transaction ₹999",
            discount_type="FLAT",
            discount_value=50.0,
            min_order_value=999.0,
            offer_type="WALLET_OFFER",
            confidence_score=0.90,
        ),
    ]

    @classmethod
    async def discover_coupons(
        cls,
        marketplace_slug: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[CouponResponse]:
        """Discover available marketplace promo coupons and offers."""
        if not marketplace_slug:
            return cls.MOCK_COUPONS

        filtered = [
            c for c in cls.MOCK_COUPONS if c.marketplace_slug.lower() == marketplace_slug.lower()
        ]
        return filtered if filtered else cls.MOCK_COUPONS[:2]

    @classmethod
    async def validate_coupon(
        cls,
        payload: CouponValidationRequest,
    ) -> CouponValidationResponse:
        """Validate coupon code against order amount."""
        code_upper = payload.code.upper().strip()
        matched = next((c for c in cls.MOCK_COUPONS if c.code.upper() == code_upper), None)

        if not matched:
            return CouponValidationResponse(
                code=payload.code,
                is_valid=False,
                discount_amount=0.0,
                final_price=payload.order_amount,
                savings_message="Invalid or expired coupon code.",
            )

        if payload.order_amount < matched.min_order_value:
            return CouponValidationResponse(
                code=payload.code,
                is_valid=False,
                discount_amount=0.0,
                final_price=payload.order_amount,
                savings_message=f"Minimum order value ₹{matched.min_order_value:,} required.",
            )

        if matched.discount_type == "PERCENTAGE":
            discount = (payload.order_amount * matched.discount_value) / 100.0
            if matched.max_discount_amount and discount > matched.max_discount_amount:
                discount = matched.max_discount_amount
        else:
            discount = matched.discount_value

        discount = round(discount, 2)
        final_price = round(max(0.0, payload.order_amount - discount), 2)

        return CouponValidationResponse(
            code=payload.code,
            is_valid=True,
            discount_amount=discount,
            final_price=final_price,
            savings_message=f"Success! You saved ₹{discount:,} with {matched.code}.",
        )

    @classmethod
    async def auto_apply(
        cls,
        payload: AutoApplyCouponsRequest,
    ) -> AutoApplyCouponsResponse:
        """Discover and auto-apply best available coupon for maximum savings."""
        coupons = await cls.discover_coupons(payload.marketplace_slug, payload.category)
        best_coupon: Optional[CouponResponse] = None
        max_savings = 0.0

        for c in coupons:
            if payload.cart_total >= c.min_order_value:
                if c.discount_type == "PERCENTAGE":
                    sav = (payload.cart_total * c.discount_value) / 100.0
                    if c.max_discount_amount and sav > c.max_discount_amount:
                        sav = c.max_discount_amount
                else:
                    sav = c.discount_value

                if sav > max_savings:
                    max_savings = sav
                    best_coupon = c

        max_savings = round(max_savings, 2)
        final_price = round(payload.cart_total - max_savings, 2)

        return AutoApplyCouponsResponse(
            marketplace_slug=payload.marketplace_slug,
            original_price=payload.cart_total,
            best_coupon_code=best_coupon.code if best_coupon else None,
            max_savings=max_savings,
            final_price=final_price,
            applied_coupons=[best_coupon] if best_coupon else [],
            cashback_available="5% Extra Cashback via COMPAREX Rewards",
            bank_offers=[
                "HDFC Bank: 10% Instant Discount up to ₹1,500",
                "ICICI Bank: Flat ₹750 off on Credit EMI",
            ],
            wallet_offers=[
                "Paytm Wallet: Flat ₹50 Cashback",
                "Mobikwik: Up to ₹250 SuperCash",
            ],
        )
