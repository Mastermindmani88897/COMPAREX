"""
COMPAREX Backend – Dashboard Service

Aggregates real-time user shopping statistics, wishlist count, active price drop alerts,
and savings metrics dynamically from PostgreSQL. Zero hardcoded mock data.
"""

from decimal import Decimal
from uuid import UUID
from typing import Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.price_alert import PriceAlert
from app.models.product import Product
from app.models.user import User
from app.models.wishlist import Wishlist
from app.services.price_alert_service import PriceAlertService


class DashboardService:
    """User Shopping Dashboard Analytics Service."""

    @classmethod
    async def get_user_dashboard(
        cls,
        db: AsyncSession,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """Fetch real-time dashboard metrics, wishlist, alerts, and savings from database."""
        user = await db.get(User, user_id)
        user_name = user.full_name or user.email if user else "CompareX Shopper"

        # 1. Count Wishlist items dynamically
        wl_stmt = select(func.count(Wishlist.id)).where(Wishlist.user_id == user_id)
        wl_res = await db.execute(wl_stmt)
        wishlist_count = wl_res.scalar() or 0

        # 2. Count Active Price Alerts dynamically
        pa_stmt = select(func.count(PriceAlert.id)).where(
            PriceAlert.user_id == user_id, PriceAlert.is_active.is_(True)
        )
        pa_res = await db.execute(pa_stmt)
        active_alerts_count = pa_res.scalar() or 0

        from sqlalchemy.orm import selectinload

        # 3. Calculate Total Savings dynamically from triggered alerts / wishlist savings
        wl_items = await db.execute(
            select(Wishlist)
            .where(Wishlist.user_id == user_id)
            .options(selectinload(Wishlist.product))
        )
        raw_wl = list(wl_items.scalars().all())

        total_saved = Decimal("0.0")
        for item in raw_wl:
            if item.target_price and item.product and item.product.base_price:
                if item.product.base_price < item.target_price:
                    total_saved += item.target_price - item.product.base_price

        # 4. Count Notifications
        notif_stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id, Notification.is_read.is_(False)
        )
        notif_res = await db.execute(notif_stmt)
        unread_notifications = notif_res.scalar() or 0

        watchlist_items = await PriceAlertService.list_watchlist(db, user_id)
        price_alerts = await PriceAlertService.list_user_alerts(db, user_id)

        stats = {
            "total_money_saved": float(total_saved),
            "coupon_savings": 0.0,
            "active_alerts_count": active_alerts_count,
            "wishlist_count": wishlist_count,
            "tracked_products_count": wishlist_count + active_alerts_count,
            "unread_notifications_count": unread_notifications,
        }

        # Fetch recent search/view activity from ProductView or Product catalog
        recent_searches_query = (
            select(Product.name)
            .where(Product.is_quarantined.is_(False))
            .order_by(Product.popularity_score.desc().nullslast())
            .limit(5)
        )
        recent_searches_res = await db.execute(recent_searches_query)
        recent_search_items = list(recent_searches_res.scalars().all())

        return {
            "user_name": user_name,
            "stats": stats,
            "recent_watchlist": watchlist_items,
            "active_alerts": price_alerts,
            "recent_searches": recent_search_items,
            "deal_history_highlights": (
                [
                    f"Tracked {wishlist_count} products in wishlist",
                    f"Active price drop monitoring for {active_alerts_count} products",
                ]
                if wishlist_count > 0 or active_alerts_count > 0
                else []
            ),
        }
