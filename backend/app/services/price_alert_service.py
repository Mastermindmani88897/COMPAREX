"""
COMPAREX Backend – PriceAlert & Watchlist Service

Manages user price drop alerts, target thresholds, and watchlist bookmarks.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal

from fastapi import HTTPException, status
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
    ) -> Dict[str, Any]:
        """Create new target price drop alert."""
        product = await db.get(Product, payload.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        prod_name = product.name or "Product Item"
        init_price = float(product.base_price) if product.base_price else float(payload.target_price)

        alert = PriceAlert(
            user_id=user_id,
            product_id=payload.product_id,
            target_price=Decimal(str(payload.target_price)),
            initial_price=Decimal(str(init_price)),
            marketplace=getattr(payload, "marketplace", "All Marketplaces") or "All Marketplaces",
            notification_method=getattr(payload, "notification_method", "both") or "both",
            notification_channel=getattr(payload, "notification_channel", "email") or "email",
            is_active=True,
            triggered=False,
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)

        return {
            "id": str(alert.id),
            "user_id": str(alert.user_id),
            "product_id": str(alert.product_id),
            "product_name": prod_name,
            "product_image": product.image_url,
            "target_price": float(alert.target_price),
            "initial_price": float(alert.initial_price),
            "current_price": init_price,
            "lowest_price": init_price,
            "marketplace": alert.marketplace,
            "notification_method": alert.notification_method,
            "is_active": alert.is_active,
            "triggered": alert.triggered,
            "created_at": alert.created_at.isoformat() if hasattr(alert, "created_at") and alert.created_at else None,
        }

    @classmethod
    async def update_alert(
        cls,
        db: AsyncSession,
        user_id: UUID,
        alert_id: UUID,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update existing price alert configuration."""
        alert = await db.get(PriceAlert, alert_id)
        if not alert or alert.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Price alert not found",
            )

        if "target_price" in data and data["target_price"] is not None:
            alert.target_price = Decimal(str(data["target_price"]))
        if "marketplace" in data and data["marketplace"] is not None:
            alert.marketplace = str(data["marketplace"])
        if "notification_method" in data and data["notification_method"] is not None:
            alert.notification_method = str(data["notification_method"])
        if "is_active" in data and data["is_active"] is not None:
            alert.is_active = bool(data["is_active"])

        await db.commit()
        await db.refresh(alert)

        product = await db.get(Product, alert.product_id)
        p_name = product.name if product else "Saved Product"
        p_price = float(product.base_price) if (product and product.base_price) else float(alert.target_price)

        return {
            "id": str(alert.id),
            "user_id": str(alert.user_id),
            "product_id": str(alert.product_id),
            "product_name": p_name,
            "product_image": product.image_url if product else None,
            "target_price": float(alert.target_price),
            "initial_price": float(alert.initial_price),
            "current_price": p_price,
            "lowest_price": p_price,
            "marketplace": alert.marketplace,
            "notification_method": alert.notification_method,
            "is_active": alert.is_active,
            "triggered": alert.triggered,
            "created_at": alert.created_at.isoformat() if hasattr(alert, "created_at") and alert.created_at else None,
        }

    @classmethod
    async def delete_alert(
        cls,
        db: AsyncSession,
        user_id: UUID,
        alert_id: UUID,
    ) -> bool:
        """Delete a price alert."""
        alert = await db.get(PriceAlert, alert_id)
        if not alert or alert.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Price alert not found",
            )
        await db.delete(alert)
        await db.commit()
        return True

    @classmethod
    async def list_user_alerts(
        cls,
        db: AsyncSession,
        user_id: UUID,
    ) -> List[Dict[str, Any]]:
        """List active price alerts for user."""
        stmt = select(PriceAlert).where(PriceAlert.user_id == user_id)
        res = await db.execute(stmt)
        alerts = res.scalars().all()

        output: List[Dict[str, Any]] = []
        for a in alerts:
            product = await db.get(Product, a.product_id)
            p_name = product.name if product else "Saved Product"
            p_price = float(product.base_price) if (product and product.base_price) else float(a.target_price)
            output.append(
                {
                    "id": str(a.id),
                    "user_id": str(a.user_id),
                    "product_id": str(a.product_id),
                    "product_name": p_name,
                    "product_image": product.image_url if product else None,
                    "target_price": float(a.target_price),
                    "initial_price": float(a.initial_price),
                    "current_price": p_price,
                    "lowest_price": p_price,
                    "marketplace": getattr(a, "marketplace", "All Marketplaces") or "All Marketplaces",
                    "notification_method": getattr(a, "notification_method", "both") or "both",
                    "is_active": a.is_active,
                    "triggered": a.triggered,
                    "created_at": a.created_at.isoformat() if hasattr(a, "created_at") and a.created_at else None,
                }
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
        p_name = product.name if product else "Watchlist Item"
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
            p_name = product.name if product else "Saved Product"
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
