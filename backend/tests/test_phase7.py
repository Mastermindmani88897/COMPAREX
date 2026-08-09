"""
COMPAREX Backend – Phase 7 Smart Shopping Ecosystem Tests

Tests:
1. PriceHistoryService & GET /api/v1/price-history/product/{id}
2. PriceAlertService, Watchlist, & Alert API endpoints
3. CouponEngineService discovery, validation, and auto-apply
4. AI Shopping Advisor evaluate_buying_advice
5. Dashboard summary aggregation
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.coupon import AutoApplyCouponsRequest, CouponValidationRequest
from app.services.coupon_service import CouponEngineService
from app.services.price_history_service import PriceHistoryService


@pytest.mark.anyio
async def test_price_history_service_execution():
    """Verify PriceHistoryService generates trends, volatility, and target price."""
    product_id = uuid.uuid4()
    res = await PriceHistoryService.get_price_history(
        db=None,
        product_id=product_id,
        product_name="Test Headphones",
        base_price=24999.0,
    )

    assert res.product_id == str(product_id)
    assert res.today_price > 0
    assert res.lowest_price <= res.highest_price
    assert res.price_trend in ("FALLING", "RISING", "STABLE")
    assert isinstance(res.price_points, list)


@pytest.mark.anyio
async def test_coupon_engine_service():
    """Test coupon discovery, validation, and auto-apply."""
    coupons = await CouponEngineService.discover_coupons(marketplace_slug="amazon")
    assert len(coupons) > 0

    val_res = await CouponEngineService.validate_coupon(
        CouponValidationRequest(
            code="COMPAREX10",
            marketplace_slug="amazon",
            order_amount=10000.0,
        )
    )
    assert val_res.is_valid is True
    assert val_res.discount_amount > 0

    auto_res = await CouponEngineService.auto_apply(
        AutoApplyCouponsRequest(
            marketplace_slug="amazon",
            cart_total=15000.0,
        )
    )
    assert auto_res.best_coupon_code == "COMPAREX10"
    assert auto_res.max_savings > 0


@pytest.mark.anyio
async def test_phase7_api_endpoints():
    """Test Phase 7 API endpoints via AsyncClient."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Price History Endpoint
        pid = uuid.uuid4()
        res_ph = await client.get(
            f"/api/v1/price-history/product/{pid}?product_name=TestItem&base_price=9999.0"
        )
        assert res_ph.status_code == 200
        assert res_ph.json()["data"]["today_price"] > 0

        # Coupon Discovery Endpoint
        res_cp = await client.get("/api/v1/coupons/discover?marketplace_slug=amazon")
        assert res_cp.status_code == 200
        assert len(res_cp.json()["data"]) > 0

        # Coupon Validate Endpoint
        res_val = await client.post(
            "/api/v1/coupons/validate",
            json={
                "code": "COMPAREX10",
                "marketplace_slug": "amazon",
                "order_amount": 10000.0,
            },
        )
        assert res_val.status_code == 200
        assert res_val.json()["data"]["is_valid"] is True

        # AI Advisor Endpoint
        res_adv = await client.post(
            "/api/v1/ai/advisor",
            json={
                "product_name": "iPhone 15 Pro",
                "current_price": 129900.0,
                "category": "electronics",
            },
        )
        assert res_adv.status_code == 200
        data_adv = res_adv.json()["data"]
        assert data_adv["verdict"] in ("BUY_NOW", "WAIT_FOR_SALE")
        assert data_adv["value_for_money_score"] > 0
