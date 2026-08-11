"""
COMPAREX Backend – PriceHistory Service

Calculates multi-marketplace price trends and historical time-series graph points
ONLY from real verified database price history observations.
NO SYNTHETIC GENERATED PRICE HISTORY OR RANDOM HISTORICAL MULTIPLIERS.
"""

from datetime import datetime, timezone, timedelta
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

# Minimum observations required to calculate a meaningful trend
TREND_MIN_OBSERVATIONS = 2

# Percentage threshold to classify a price movement as "dropping" or "rising"
TREND_CHANGE_THRESHOLD_PCT = 0.1  # 0.1% movement triggers direction classification


class DictAttributeWrapper(dict):
    """Dict supporting both item access res['key'] and dot notation res.key."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'DictAttributeWrapper' has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def _calculate_trend(
    observations: List[float],
    threshold_pct: float = TREND_CHANGE_THRESHOLD_PCT,
) -> Dict[str, Any]:
    """
    Calculate price trend from a chronologically ordered list of real price observations.

    Args:
        observations: Price values ordered oldest → newest from DB
        threshold_pct: Minimum percentage change to call a trend

    Returns:
        Dict with trend_status, trend_badge, price_change, price_change_percent, direction
    """
    if len(observations) < TREND_MIN_OBSERVATIONS:
        return {
            "trend_status": "INSUFFICIENT_DATA",
            "trend_badge": "⚠ Insufficient Data",
            "price_change": None,
            "price_change_percent": None,
            "direction": None,
        }

    first_price = observations[0]
    last_price = observations[-1]

    if first_price <= 0:
        return {
            "trend_status": "INSUFFICIENT_DATA",
            "trend_badge": "⚠ Insufficient Data",
            "price_change": None,
            "price_change_percent": None,
            "direction": None,
        }

    price_change = round(last_price - first_price, 2)
    price_change_pct = round((price_change / first_price) * 100, 2)

    if price_change_pct < -threshold_pct:
        status = "PRICE_DROPPING"
        badge = f"↓ Price Dropping ({abs(price_change_pct):.1f}%)"
        direction = "down"
    elif price_change_pct > threshold_pct:
        status = "PRICE_RISING"
        badge = f"↑ Price Rising ({price_change_pct:.1f}%)"
        direction = "up"
    else:
        status = "STABLE"
        badge = "➖ Stable"
        direction = "stable"

    return {
        "trend_status": status,
        "trend_badge": badge,
        "price_change": price_change,
        "price_change_percent": price_change_pct,
        "direction": direction,
    }


def _apply_time_filter(
    records: List[PriceHistory],
    time_range: str,
) -> List[PriceHistory]:
    """Filter price history records to the requested time window."""
    now = datetime.now(timezone.utc)
    cutoff_map = {
        "24h": now - timedelta(hours=24),
        "7d": now - timedelta(days=7),
        "30d": now - timedelta(days=30),
        "3m": now - timedelta(days=90),
        "6m": now - timedelta(days=180),
        "1y": now - timedelta(days=365),
        "all": None,
    }
    cutoff = cutoff_map.get(time_range)
    if cutoff is None:
        return records  # "all" — return everything

    filtered = []
    for r in records:
        ts = r.created_at
        if ts is not None:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= cutoff:
                filtered.append(r)
    return filtered


class PriceHistoryService:
    """Price history analytics engine enforcing zero-synthetic data integrity."""

    @classmethod
    async def get_price_history(
        cls,
        db: Optional[AsyncSession],
        product_id: UUID,
        product_name: Optional[str] = None,
        base_price: float = 0.0,
        time_range: str = "30d",
    ) -> DictAttributeWrapper:
        """Compute verified multi-store price history timeline from real DB observations only."""

        p_name = product_name or f"Product {str(product_id)[:8]}"
        db_history_records: List[PriceHistory] = []
        product_base_price: Optional[float] = None

        if db is not None:
            try:
                prod_obj = await db.get(Product, product_id)
                if prod_obj:
                    p_name = prod_obj.name
                    if prod_obj.base_price and float(prod_obj.base_price) > 0:
                        product_base_price = float(prod_obj.base_price)

                # Fetch all history with valid listing_id, chronological order
                stmt = (
                    select(PriceHistory)
                    .where(
                        PriceHistory.product_id == product_id,
                        PriceHistory.listing_id.isnot(None),
                    )
                    .order_by(PriceHistory.created_at.asc())
                    .limit(1000)
                )
                res = await db.execute(stmt)
                all_records = list(res.scalars().all())

                # Apply time window filter
                db_history_records = _apply_time_filter(all_records, time_range)

                logger.info(
                    "PRICE_HISTORY_FETCH | product_id=%s | total_records=%d | "
                    "after_filter(%s)=%d",
                    product_id,
                    len(all_records),
                    time_range,
                    len(db_history_records),
                )

            except Exception as exc:
                logger.warning("Error fetching PriceHistory from database: %s", exc)

        total_observations = len(db_history_records)
        has_sufficient_history = total_observations >= TREND_MIN_OBSERVATIONS

        # ── EMPTY STATE — 0 or 1 real observations ───────────────────────────────
        if not has_sufficient_history:
            single_price = None
            if total_observations == 1:
                single_price = float(db_history_records[0].price)

            return DictAttributeWrapper(
                {
                    "product_id": str(product_id),
                    "product_name": p_name,
                    "time_range": time_range,
                    # Current price stats: only from verified marketplace observations
                    # DO NOT fall back to base_price as a "current price" substitute.
                    "today_price": single_price,
                    "current_live_price": single_price,
                    "lowest_price": single_price,
                    "highest_price": single_price,
                    "lowest_recorded_price": single_price,
                    "highest_recorded_price": single_price,
                    "average_price": single_price,
                    # Trend — insufficient data
                    "price_trend": "INSUFFICIENT_DATA",
                    "trend_status": "INSUFFICIENT_DATA",
                    "trend_badge": "⚠ Insufficient Data",
                    "price_change": None,
                    "price_change_percent": None,
                    "direction": None,
                    # Status flags
                    "has_sufficient_history": False,
                    "total_points": total_observations,
                    "verified_observation_count": total_observations,
                    "message": (
                        f"Only {total_observations} verified price observation(s) available. "
                        "Price history graph requires at least 2 real observations. "
                        "CompareX will build this history as verified marketplace prices are collected."
                        if total_observations == 1
                        else (
                            "No verified price history yet. "
                            "CompareX will build price history as real marketplace prices are verified."
                        )
                    ),
                    # Analytics placeholders
                    "volatility_index": 0.0,
                    "ai_prediction": (
                        "Price history will appear after verified observations are collected."
                    ),
                    "best_time_to_buy_recommendation": "Monitor verified live marketplace matrix.",
                    "best_time_to_buy": "Insufficient Data",
                    "gemini_prediction": (
                        "Insufficient price history to make a reliable prediction. "
                        "Monitor the marketplace comparison for live verified prices."
                    ),
                    # Store/graph data
                    "available_stores": STORES,
                    "stores": STORES,
                    "store_stats": {},
                    "points": [],
                    "price_points": [],
                }
            )

        # ── SUFFICIENT HISTORY — build timeline from real observations ────────────
        date_points_map: Dict[str, Dict[str, Any]] = {}
        all_prices: List[float] = []
        chronological_prices: List[float] = []  # for trend direction

        for record in db_history_records:
            rec_date = (
                record.created_at.strftime("%Y-%m-%d")
                if record.created_at
                else datetime.now(timezone.utc).strftime("%Y-%m-%d")
            )
            price_val = float(record.price)
            slug = (record.marketplace_slug or "store").lower()

            all_prices.append(price_val)
            chronological_prices.append(price_val)

            if rec_date not in date_points_map:
                ts_str = (
                    record.created_at.isoformat()
                    if record.created_at
                    else datetime.now(timezone.utc).isoformat()
                )
                date_points_map[rec_date] = {"date": rec_date, "timestamp": ts_str}

            date_points_map[rec_date][slug] = price_val

        formatted_points = list(date_points_map.values())

        lowest_rec = min(all_prices)
        highest_rec = max(all_prices)
        avg_rec = round(sum(all_prices) / len(all_prices), 2)

        # Volatility index: normalized range vs average
        vol_idx = 0.0
        if avg_rec > 0:
            vol_idx = round(min(1.0, (highest_rec - lowest_rec) / avg_rec), 2)

        # Real trend from actual chronological observations
        trend_data = _calculate_trend(chronological_prices)

        # Current price = most recent real observation
        current_verified_price = float(db_history_records[-1].price)

        # ── Best time to buy recommendation (only if enough real history) ─────────
        if current_verified_price <= lowest_rec * 1.02:
            buy_recommendation = "BUY NOW — Current price is near the lowest recorded."
        elif current_verified_price >= highest_rec * 0.98:
            buy_recommendation = "WAIT — Price is near the historical high."
        else:
            buy_recommendation = "FAIR PRICE — Within normal historical range."

        # Trend explanation text using real DB values
        change = trend_data["price_change"]
        change_pct = trend_data["price_change_percent"]
        if change is not None:
            first_price = chronological_prices[0]
            if change < 0:
                gemini_text = (
                    f"Current verified price is ₹{current_verified_price:,.0f}, "
                    f"which is ₹{abs(change):,.0f} lower than the first verified observation "
                    f"of ₹{first_price:,.0f} ({abs(change_pct):.1f}% drop). "
                    "This is based on real marketplace observations only."
                )
            elif change > 0:
                gemini_text = (
                    f"Current verified price is ₹{current_verified_price:,.0f}, "
                    f"which is ₹{change:,.0f} higher than the first verified observation "
                    f"of ₹{first_price:,.0f} ({change_pct:.1f}% increase). "
                    "This is based on real marketplace observations only."
                )
            else:
                gemini_text = (
                    f"Price has remained stable at approximately ₹{current_verified_price:,.0f} "
                    "across all verified observations."
                )
        else:
            gemini_text = "Verified price observations collected from live marketplace index."

        return DictAttributeWrapper(
            {
                "product_id": str(product_id),
                "product_name": p_name,
                "time_range": time_range,
                # Current price — ONLY from verified observations, never from base_price
                "today_price": current_verified_price,
                "current_live_price": current_verified_price,
                # Historical stats — ONLY from verified observations
                "lowest_price": lowest_rec,
                "highest_price": highest_rec,
                "lowest_recorded_price": lowest_rec,
                "highest_recorded_price": highest_rec,
                "average_price": avg_rec,
                # Real trend calculation
                "price_trend": trend_data["trend_status"],
                "trend_status": trend_data["trend_status"],
                "trend_badge": trend_data["trend_badge"],
                "price_change": trend_data["price_change"],
                "price_change_percent": trend_data["price_change_percent"],
                "direction": trend_data["direction"],
                # Status
                "has_sufficient_history": True,
                "total_points": len(formatted_points),
                "verified_observation_count": total_observations,
                "message": (
                    f"Retrieved {total_observations} verified price observations "
                    f"across {len(formatted_points)} date(s)."
                ),
                # Analytics
                "volatility_index": vol_idx,
                "ai_prediction": gemini_text,
                "gemini_prediction": gemini_text,
                "best_time_to_buy_recommendation": buy_recommendation,
                "best_time_to_buy": buy_recommendation,
                # Store/graph data
                "available_stores": STORES,
                "stores": STORES,
                "store_stats": {},
                "points": formatted_points,
                "price_points": formatted_points,
                # Legacy aliases
                "lowest_recorded": lowest_rec,
                "highest_recorded": highest_rec,
                "average_recorded": avg_rec,
                "current_price": current_verified_price,
            }
        )
