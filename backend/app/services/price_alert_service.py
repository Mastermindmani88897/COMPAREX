"""
COMPAREX Backend – PriceAlert & Watchlist Service

Manages user price drop alerts, target thresholds, and watchlist bookmarks.
"""

from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_alert import PriceAlert
from app.models.product import Product
from app.models.watchlist import Watchlist
from app.schemas.price_alert import (
    PriceAlertCreate,
    PriceAlertResponse,
    WatchlistCreate,
    WatchlistResponse,
)


class PriceAlertService:
    """Price alert and watchlist management service."""

    @classmethod
    async def create_alert(
        cls,
        db: AsyncSession,
        user_id: UUID,
        payload: PriceAlertCreate,
    ) -> PriceAlertResponse:
        """Create new target price drop alert."""
        product = await db.get(Product, payload.product_id)
        prod_name = product.title if product else "Product Item"
        init_price = float(product.base_price) if (product and product.base_price) else 10000.0

        alert = PriceAlert(
            user_id=user_id,
            product_id=payload.product_id,
            target_price=payload.target_price,
            initial_price=init_price,
            notification_channel=payload.notification_channel,
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)

        return PriceAlertResponse(
            id=alert.id,
            user_id=alert.user_id,
            product_id=alert.product_id,
            target_price=float(alert.target_price),
            initial_price=float(alert.initial_price),
            notification_channel=alert.notification_channel,
            is_active=alert.is_active,
            triggered=alert.triggered,
            product_name=prod_name,
            current_price=init_price,
        )

    @classmethod
    async def list_user_alerts(
        cls,
        db: AsyncSession,
        user_id: UUID,
    ) -> List[PriceAlertResponse]:
        """List active price alerts for user."""
        stmt = select(PriceAlert).where(PriceAlert.user_id == user_id)
        res = await db.execute(stmt)
        alerts = res.scalars().all()

        output: List[PriceAlertResponse] = []
        for a in alerts:
            product = await db.get(Product, a.product_id)
            p_name = product.title if product else "Saved Product"
            p_price = float(product.base_price) if (product and product.base_price) else 9999.0
            output.append(
                PriceAlertResponse(
                    id=a.id,
                    user_id=a.user_id,
                    product_id=a.product_id,
                    target_price=float(a.target_price),
                    initial_price=float(a.initial_price),
                    notification_channel=a.notification_channel,
                    is_active=a.is_active,
                    triggered=a.triggered,
                    product_name=p_name,
                    current_price=p_price,
                )
            )
        return output

    @classmethod
    async def add_to_watchlist(
        cls,
        db: AsyncSession,
        user_id: UUID,
        payload: WatchlistCreate,
    ) -> WatchlistResponse:
        """Add product to user watchlist."""
        existing = await db.execute(
            select(Watchlist).where(
                Watchlist.user_id == user_id,
                Watchlist.product_id == payload.product_id,
            )
        )
        item = existing.scalars().first()
        if not item:
            item = Watchlist(user_id=user_id, product_id=payload.product_id)
            db.add(item)
            await db.commit()
            await db.refresh(item)

        product = await db.get(Product, payload.product_id)
        p_name = product.title if product else "Watchlist Item"
        p_price = float(product.base_price) if (product and product.base_price) else 4999.0

        return WatchlistResponse(
            id=item.id,
            user_id=item.user_id,
            product_id=item.product_id,
            product_name=p_name,
            current_lowest_price=p_price,
        )

    @classmethod
    async def list_watchlist(
        cls,
        db: AsyncSession,
        user_id: UUID,
    ) -> List[WatchlistResponse]:
        """List user watchlist items."""
        stmt = select(Watchlist).where(Watchlist.user_id == user_id)
        res = await db.execute(stmt)
        items = res.scalars().all()

        output: List[WatchlistResponse] = []
        for w in items:
            product = await db.get(Product, w.product_id)
            p_name = product.title if product else "Saved Product"
            p_price = float(product.base_price) if (product and product.base_price) else 4999.0
            output.append(
                WatchlistResponse(
                    id=w.id,
                    user_id=w.user_id,
                    product_id=w.product_id,
                    product_name=p_name,
                    current_lowest_price=p_price,
                )
            )
        return output
