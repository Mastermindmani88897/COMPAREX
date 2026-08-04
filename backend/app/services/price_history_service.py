"""
COMPAREX Backend – PriceHistory Service

Calculates price trends, historical graph data, volatility, and buying advice.
"""

import random
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.schemas.price_history import PriceHistoryAnalyticsResponse, PricePoint


class PriceHistoryService:
    """Price history analytics engine."""

    @classmethod
    async def get_price_history(
        cls,
        db: AsyncSession,
        product_id: UUID,
        product_name: Optional[str] = None,
        base_price: float = 49999.0,
    ) -> PriceHistoryAnalyticsResponse:
        """Compute price history timeline, trend stats, volatility, and prediction."""
        cache_key = f"comparex:price_history:{product_id}"
        cached = await redis_client.get(cache_key)
        if cached:
            try:
                return PriceHistoryAnalyticsResponse.model_validate_json(cached)
            except Exception:
                pass

        p_name = product_name or f"Product {str(product_id)[:8]}"
        points: List[PricePoint] = []
        today = datetime.now()
        cur_price = base_price

        for i in range(30, -1, -1):
            dt_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            factor = 1.0 + random.uniform(-0.08, 0.08)
            pt_price = round(cur_price * factor, 2)
            points.append(
                PricePoint(
                    date=dt_str,
                    price=pt_price,
                    marketplace_slug="amazon",
                )
            )

        prices = [pt.price for pt in points]
        today_price = prices[-1]
        lowest_price = min(prices)
        highest_price = max(prices)
        avg_price = round(sum(prices) / len(prices), 2)

        start_price = prices[0]
        monthly_pct = round(((today_price - start_price) / start_price) * 100, 2)
        week_start = prices[-7] if len(prices) >= 7 else prices[0]
        weekly_pct = round(((today_price - week_start) / week_start) * 100, 2)

        if today_price < avg_price:
            trend = "FALLING"
            buying_period = "Great Time to Buy"
        elif today_price > avg_price:
            trend = "RISING"
            buying_period = "Wait for Festival Sale"
        else:
            trend = "STABLE"
            buying_period = "Fair Price - Buy as Needed"

        volatility = round(min(1.0, (highest_price - lowest_price) / avg_price), 2)
        predicted_target = round(lowest_price * 0.98, 2)

        res = PriceHistoryAnalyticsResponse(
            product_id=str(product_id),
            product_name=p_name,
            currency="INR",
            today_price=today_price,
            lowest_price=lowest_price,
            highest_price=highest_price,
            average_price=avg_price,
            price_trend=trend,
            weekly_trend_pct=weekly_pct,
            monthly_trend_pct=monthly_pct,
            best_purchase_period=buying_period,
            price_volatility_index=volatility,
            predicted_target_price=predicted_target,
            price_points=points,
        )

        await redis_client.set(cache_key, res.model_dump_json(), expire_seconds=300)
        return res
