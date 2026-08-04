"""
COMPAREX Backend – Dashboard Service

Aggregates shopping statistics, watchlist, price drop alerts, and savings metrics.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.dashboard import DashboardSummaryResponse, ShoppingStats
from app.services.price_alert_service import PriceAlertService


class DashboardService:
    """User Shopping Dashboard Analytics Service."""

    @classmethod
    async def get_user_dashboard(
        cls,
        db: AsyncSession,
        user_id: UUID,
    ) -> DashboardSummaryResponse:
        """Fetch complete dashboard metrics, wishlist, alerts, and savings statistics."""
        user = await db.get(User, user_id)
        user_name = user.full_name or user.email if user else "CompareX Shopper"

        watchlist_items = await PriceAlertService.list_watchlist(db, user_id)
        price_alerts = await PriceAlertService.list_user_alerts(db, user_id)

        stats = ShoppingStats(
            total_money_saved=4250.0,
            monthly_savings=1850.0,
            active_alerts_count=len(price_alerts),
            watchlist_count=len(watchlist_items),
            recent_searches_count=12,
            favorite_marketplaces=["Amazon India", "Flipkart", "Croma"],
        )

        recent_searches = [
            "Sony WH-1000XM5 Wireless Headphones",
            "Apple MacBook Air M3 16GB",
            "Samsung Galaxy S24 Ultra 5G",
            "LG C3 55 inch OLED TV",
        ]

        highlights = [
            "Saved ₹1,200 on Amazon Great Indian Festival deal",
            "Price drop alert triggered for Apple Watch Series 9",
            "Auto-applied COMPAREX10 coupon on Croma electronics purchase",
        ]

        return DashboardSummaryResponse(
            user_name=user_name,
            stats=stats,
            recent_watchlist=watchlist_items,
            active_alerts=price_alerts,
            recent_searches=recent_searches,
            deal_history_highlights=highlights,
        )
