"""
COMPAREX Backend – Automatic Price Monitor Background Worker

Executes background periodic price monitor jobs every 30-60 minutes:
1. Queries all active PriceAlert records in PostgreSQL database.
2. Fetches latest marketplace prices using MarketplaceAggregatorService.
3. Appends new PriceHistory record with product_id, marketplace, price, timestamp.
4. Triggers In-App & Email Notifications if Current Price <= Target Price.
"""

import asyncio
from decimal import Decimal
from typing import List

from sqlalchemy import select
from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.models.price_alert import PriceAlert
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.services.aggregator_service import MarketplaceAggregatorService
from app.services.notification_service import NotificationService

logger = get_logger(__name__)


class PriceMonitorService:
    """Service executing automatic price drop monitoring across all active alerts."""

    @classmethod
    async def check_all_active_alerts(cls) -> int:
        """Fetch all active price alerts and check current marketplace prices."""
        logger.info("BACKGROUND JOB: Automatic Price Monitor job starting...")

        alerts_checked = 0
        notifications_triggered = 0

        async with AsyncSessionLocal() as session:
            try:
                stmt = select(PriceAlert).where(PriceAlert.is_active.is_(True))
                res = await session.execute(stmt)
                alerts: List[PriceAlert] = list(res.scalars().all())
                logger.info("Found %d active price alerts to monitor.", len(alerts))

                for alert in alerts:
                    alerts_checked += 1
                    product = await session.get(Product, alert.product_id)
                    if not product:
                        continue

                    target_price = alert.target_price
                    query_name = product.name

                    # 1. Fetch live marketplace aggregation
                    agg_data = await MarketplaceAggregatorService.aggregate_search(
                        query=query_name, use_cache=False
                    )

                    lowest_price = agg_data.get("lowest_price") or float(product.base_price or 0)
                    listings = agg_data.get("listings", [])

                    # 2. Append new price history records for each store
                    for lst in listings:
                        store_price = lst.get("price")
                        if store_price and store_price > 0:
                            ph = PriceHistory(
                                product_id=product.id,
                                marketplace_slug=lst.get("marketplace_slug", "store"),
                                price=Decimal(str(store_price)),
                                currency="INR",
                            )
                            session.add(ph)

                    await session.commit()

                    # 3. Check if price drop threshold reached
                    if lowest_price > 0 and Decimal(str(lowest_price)) <= target_price:
                        notifications_triggered += 1
                        logger.info(
                            "ALERT TRIGGERED! Product '%s' price dropped to ₹%.2f (Target: ₹%.2f)",
                            product.name,
                            lowest_price,
                            target_price,
                        )

                        # Create Notification
                        notif_service = NotificationService(session)
                        best_store = (
                            listings[0].get("marketplace_name", "Retailer")
                            if listings
                            else "Amazon"
                        )
                        target_val = float(target_price)
                        notif_msg = (
                            f"{product.name} price dropped on {best_store}! "
                            f"Current Price: ₹{lowest_price:,.0f} (Target: ₹{target_val:,.0f})."
                        )
                        await notif_service.create_notification(
                            user_id=alert.user_id,
                            product_id=product.id,
                            title="🔔 Great News! Price Dropped!",
                            message=notif_msg,
                            type="price_drop",
                            target_price=target_price,
                            current_price=Decimal(str(lowest_price)),
                            marketplace=best_store,
                        )

                        alert.triggered = True
                        await session.commit()

            except Exception as exc:
                logger.error("Error running Price Monitor background job: %s", exc)

        logger.info(
            "BACKGROUND JOB FINISHED: Checked %d alerts, triggered %d notifications.",
            alerts_checked,
            notifications_triggered,
        )
        return notifications_triggered


async def start_periodic_price_monitor(interval_seconds: int = 1800):
    """Periodic loop running price monitor every N seconds (default: 30 minutes)."""
    logger.info("Initializing Periodic Price Monitor Task (Interval: %ds)", interval_seconds)
    # Initial delay to allow DB startup
    await asyncio.sleep(10)

    while True:
        try:
            await PriceMonitorService.check_all_active_alerts()
        except asyncio.CancelledError:
            logger.info("Price Monitor background task cancelled.")
            break
        except Exception as exc:
            logger.error("Price Monitor background task loop error: %s", exc)

        await asyncio.sleep(interval_seconds)
