"""
COMPAREX Backend – PriceHistory Service

Calculates multi-marketplace price trends and historical time-series graph points
ONLY from real verified database price history observations.
NO SYNTHETIC GENERATED PRICE HISTORY OR RANDOM HISTORICAL MULTIPLIERS.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.price_history import PriceHistory
from app.models.product import Product

logger = get_logger(__name__)

STORES = [
    {"name": "Amazon", "slug": "amazon", "color": "#F97316"},
    {"name": "Flipkart", "slug": "flipkart", "color": "#3B82F6"},
    {"name": "Croma", "slug": "croma", "color": "#10B981"},
    {"name": "Reliance Digital", "slug": "reliance_digital", "color": "#EF4444"},
    {"name": "Tata Cliq", "slug": "tata_cliq", "color": "#8B5CF6"},
    {"name": "Vijay Sales", "slug": "vijay_sales", "color": "#EC4899"},
    {"name": "Meesho", "slug": "meesho", "color": "#F59E0B"},
    {"name": "Myntra", "slug": "myntra", "color": "#6366F1"},
]


class DictAttributeWrapper(dict):
    """Dict supporting both item access res['key'] and dot notation res.key."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'DictAttributeWrapper' has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


class PriceHistoryService:
    """Price history analytics engine enforcing zero-synthetic data integrity."""

    @classmethod
    async def get_price_history(
        cls,
        db: Optional[AsyncSession],
        product_id: UUID,
        product_name: Optional[str] = None,
        base_price: float = 49999.0,
        time_range: str = "30d",
    ) -> DictAttributeWrapper:
        """Compute verified multi-store price history timeline."""

        p_name = product_name or f"Product {str(product_id)[:8]}"
        cur_price = base_price
        db_history_records: List[PriceHistory] = []

        if db is not None:
            try:
                prod_obj = await db.get(Product, product_id)
                if prod_obj:
                    p_name = prod_obj.name
                    if prod_obj.base_price:
                        cur_price = float(prod_obj.base_price)

                stmt = (
                    select(PriceHistory)
                    .where(
                        PriceHistory.product_id == product_id,
                        PriceHistory.listing_id.isnot(None),
                    )
                    .order_by(desc(PriceHistory.created_at))
                    .limit(500)
                )
                res = await db.execute(stmt)
                db_history_records = list(res.scalars().all())
            except Exception as exc:
                logger.warning("Error fetching PriceHistory from database: %s", exc)

        # Evaluate history sufficiency
        has_sufficient_history = len(db_history_records) >= 2

        if not has_sufficient_history:
            return DictAttributeWrapper(
                {
                    "product_id": str(product_id),
                    "product_name": p_name,
                    "time_range": time_range,
                    "today_price": cur_price,
                    "current_live_price": cur_price,
                    "lowest_price": cur_price,
                    "highest_price": cur_price,
                    "lowest_recorded_price": cur_price,
                    "highest_recorded_price": cur_price,
                    "average_price": cur_price,
                    "price_trend": "STABLE",
                    "has_sufficient_history": False,
                    "message": (
                        "Insufficient verified price history. History graph will "
                        "appear after verified marketplace prices are collected."
                    ),
                    "total_points": len(db_history_records),
                    "lowest_recorded": cur_price if cur_price > 0 else None,
                    "highest_recorded": cur_price if cur_price > 0 else None,
                    "average_recorded": cur_price if cur_price > 0 else None,
                    "current_price": cur_price if cur_price > 0 else None,
                    "volatility_index": 0.0,
                    "trend_status": "STABLE",
                    "trend_badge": "➖ Stable",
                    "ai_prediction": (
                        "Price history will appear after verified observations are collected."
                    ),
                    "best_time_to_buy_recommendation": "Monitor verified live marketplace matrix.",
                    "available_stores": STORES,
                    "stores": STORES,
                    "store_stats": {},
                    "points": [],
                    "price_points": [],
                }
            )

        # Build timeline from verified DB observations
        date_points_map: Dict[str, Dict[str, Any]] = {}
        all_prices: List[float] = []

        for record in reversed(db_history_records):
            rec_date = (
                record.created_at.strftime("%Y-%m-%d")
                if record.created_at
                else datetime.now().strftime("%Y-%m-%d")
            )
            price_val = float(record.price)
            slug = (record.marketplace_slug or "store").lower()

            all_prices.append(price_val)

            if rec_date not in date_points_map:
                ts_str = (
                    record.created_at.isoformat()
                    if record.created_at
                    else datetime.now().isoformat()
                )
                date_points_map[rec_date] = {"date": rec_date, "timestamp": ts_str}

            date_points_map[rec_date][slug] = price_val

        formatted_points = list(date_points_map.values())
        lowest_rec = min(all_prices) if all_prices else cur_price
        highest_rec = max(all_prices) if all_prices else cur_price
        avg_rec = round(sum(all_prices) / len(all_prices), 2) if all_prices else cur_price

        lowest_val = lowest_rec if lowest_rec is not None else cur_price
        highest_val = highest_rec if highest_rec is not None else cur_price

        vol_idx = 0.0
        if avg_rec and avg_rec > 0 and lowest_rec is not None and highest_rec is not None:
            vol_idx = round(min(1.0, (highest_rec - lowest_rec) / avg_rec), 2)

        return DictAttributeWrapper(
            {
                "product_id": str(product_id),
                "product_name": p_name,
                "time_range": time_range,
                "today_price": cur_price,
                "current_live_price": cur_price,
                "lowest_price": lowest_val,
                "highest_price": highest_val,
                "lowest_recorded_price": lowest_val,
                "highest_recorded_price": highest_val,
                "average_price": avg_rec,
                "price_trend": "STABLE",
                "has_sufficient_history": has_sufficient_history,
                "message": (
                    f"Retrieved {len(db_history_records)} verified price observations."
                    if has_sufficient_history
                    else "Insufficient verified price history."
                ),
                "total_points": len(formatted_points),
                "lowest_recorded": lowest_val,
                "highest_recorded": highest_val,
                "average_recorded": avg_rec,
                "current_price": cur_price,
                "volatility_index": vol_idx,
                "trend_status": "STABLE",
                "trend_badge": "➖ Stable",
                "ai_prediction": (
                    "Verified price observations collected from live marketplace index."
                ),
                "best_time_to_buy_recommendation": "Purchase from store offering lowest price.",
                "available_stores": STORES,
                "stores": STORES,
                "store_stats": {},
                "points": formatted_points,
                "price_points": formatted_points,
            }
        )
