"""
COMPAREX Backend – Automatic Price Monitor Background Worker

Executes background periodic price monitor jobs every 30-60 minutes:
1. Queries all active PriceAlert records in PostgreSQL database.
2. Fetches latest marketplace prices using MarketplaceAggregatorService.
3. Resolves/creates canonical ProductListing to obtain a valid, non-null listing_id.
4. Appends new PriceHistory record with listing_id, product_id, marketplace, price, timestamp.
5. Triggers In-App & Email Notifications if Current Price <= Target Price.
"""

import asyncio
import uuid
from decimal import Decimal
from typing import List

from sqlalchemy import or_, select

from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.models.marketplace import Marketplace
from app.models.price_alert import PriceAlert
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.models.product_listing import ProductListing
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
        skipped_listings = 0

        async with AsyncSessionLocal() as session:
            try:
                stmt = select(PriceAlert).where(PriceAlert.is_active.is_(True))
                res = await session.execute(stmt)
                alerts: List[PriceAlert] = list(res.scalars().all())
                logger.info("Found %d active price alerts to monitor.", len(alerts))

                # Collect scalar data to avoid ORM expiration issues across transactions
                alert_data = [
                    (
                        str(a.id),
                        a.user_id,
                        a.product_id,
                        a.target_price,
                    )
                    for a in alerts
                ]

                for alert_id_str, user_id, product_id, target_price in alert_data:
                    alerts_checked += 1
                    try:
                        product = await session.get(Product, product_id)
                        if not product:
                            logger.warning(
                                "Product ID %s for alert %s not found. Skipping.",
                                product_id,
                                alert_id_str,
                            )
                            continue

                        product_name = product.name
                        product_base_price = product.base_price

                        # 1. Fetch live marketplace aggregation safely
                        try:
                            agg_data = await MarketplaceAggregatorService.aggregate_search(
                                query=product_name, use_cache=False
                            )
                        except Exception as agg_exc:
                            logger.warning(
                                "Failed marketplace aggregation for query '%s' (alert %s): %s",
                                product_name,
                                alert_id_str,
                                agg_exc,
                            )
                            continue

                        lowest_price = agg_data.get("lowest_price") or float(
                            product_base_price or 0
                        )
                        listings = agg_data.get("listings", [])

                        # 2. Safely resolve/create ProductListing & append PriceHistory per store
                        for lst in listings:
                            try:
                                store_price = lst.get("price")
                                if not store_price or float(store_price) <= 0:
                                    skipped_listings += 1
                                    continue

                                mp_slug = (lst.get("marketplace_slug") or "amazon").lower()
                                mp_name = lst.get("marketplace_name") or mp_slug.title()
                                listing_url = (
                                    lst.get("listing_url") or f"https://www.{mp_slug}.com"
                                )

                                # A. Resolve or Create Marketplace by slug OR name
                                mp_stmt = select(Marketplace).where(
                                    or_(
                                        Marketplace.slug == mp_slug,
                                        Marketplace.name.ilike(mp_name),
                                    )
                                )
                                mp_res = await session.execute(mp_stmt)
                                marketplace = mp_res.scalars().first()

                                if not marketplace:
                                    try:
                                        marketplace = Marketplace(
                                            id=uuid.uuid4(),
                                            name=mp_name,
                                            slug=mp_slug,
                                            base_url=f"https://www.{mp_slug}.com",
                                            logo_url=lst.get("marketplace_logo"),
                                        )
                                        session.add(marketplace)
                                        await session.flush()
                                    except Exception:
                                        await session.rollback()
                                        mp_res = await session.execute(mp_stmt)
                                        marketplace = mp_res.scalars().first()

                                if not marketplace:
                                    skipped_listings += 1
                                    continue

                                # B. Resolve or Upsert ProductListing
                                lst_stmt = select(ProductListing).where(
                                    ProductListing.product_id == product_id,
                                    ProductListing.marketplace_id == marketplace.id,
                                )
                                lst_res = await session.execute(lst_stmt)
                                listing_obj = lst_res.scalar_one_or_none()

                                dec_price = Decimal(str(store_price))

                                if listing_obj:
                                    listing_obj.price = dec_price
                                    if lst.get("original_price"):
                                        listing_obj.original_price = Decimal(
                                            str(lst["original_price"])
                                        )
                                    if lst.get("discount_percent"):
                                        listing_obj.discount_percent = Decimal(
                                            str(lst["discount_percent"])
                                        )
                                    if listing_url and "http" in listing_url:
                                        listing_obj.listing_url = listing_url
                                else:
                                    mp_pid = (
                                        lst.get("marketplace_product_id")
                                        or f"{mp_slug.upper()}-{uuid.uuid4().hex[:8]}"
                                    )
                                    orig_price_val = lst.get("original_price") or (
                                        float(dec_price) * 1.15
                                    )
                                    disc_pct_val = lst.get("discount_percent") or 10.0

                                    listing_obj = ProductListing(
                                        id=uuid.uuid4(),
                                        product_id=product_id,
                                        marketplace_id=marketplace.id,
                                        marketplace_product_id=mp_pid,
                                        price=dec_price,
                                        original_price=Decimal(str(orig_price_val)),
                                        discount_percent=Decimal(str(disc_pct_val)),
                                        currency="INR",
                                        listing_url=listing_url,
                                        seller_name=lst.get("seller_name")
                                        or f"{marketplace.name} Retailer",
                                        is_available=bool(lst.get("is_available", True)),
                                        stock_status=lst.get("stock_status", "IN_STOCK"),
                                    )
                                    session.add(listing_obj)
                                    await session.flush()

                                # C. Insert PriceHistory with GUARANTEED VALID NON-NULL listing_id
                                if not listing_obj or not listing_obj.id:
                                    skipped_listings += 1
                                    logger.warning(
                                        "Could not resolve listing ID for product '%s' store '%s'",
                                        product_name,
                                        mp_name,
                                    )
                                    continue

                                ph = PriceHistory(
                                    id=uuid.uuid4(),
                                    listing_id=listing_obj.id,
                                    product_id=product_id,
                                    marketplace_slug=mp_slug,
                                    price=dec_price,
                                    currency="INR",
                                )
                                session.add(ph)

                            except Exception as lst_exc:
                                await session.rollback()
                                skipped_listings += 1
                                logger.warning(
                                    "Failed to process listing record for product '%s' (%s): %s",
                                    product_name,
                                    lst.get("marketplace_name", "Unknown"),
                                    lst_exc,
                                )

                        await session.commit()

                        # 3. Check if target price threshold reached for notification
                        if lowest_price > 0 and Decimal(str(lowest_price)) <= target_price:
                            notifications_triggered += 1
                            logger.info(
                                "ALERT TRIGGERED! Product '%s' price dropped to ₹%.2f "
                                "(Target: ₹%.2f)",
                                product_name,
                                lowest_price,
                                target_price,
                            )

                            notif_service = NotificationService(session)
                            best_store = (
                                listings[0].get("marketplace_name", "Retailer")
                                if listings
                                else "Amazon"
                            )
                            target_val = float(target_price)
                            notif_msg = (
                                f"{product_name} price dropped on {best_store}! "
                                f"Current Price: ₹{lowest_price:,.0f} "
                                f"(Target: ₹{target_val:,.0f})."
                            )
                            await notif_service.create_notification(
                                user_id=user_id,
                                product_id=product_id,
                                title="🔔 Great News! Price Dropped!",
                                message=notif_msg,
                                type="price_drop",
                                target_price=target_price,
                                current_price=Decimal(str(lowest_price)),
                                marketplace=best_store,
                            )

                            # Re-fetch alert to update triggered state
                            cur_alert = await session.get(PriceAlert, uuid.UUID(alert_id_str))
                            if cur_alert:
                                cur_alert.triggered = True
                                await session.commit()

                    except Exception as alert_exc:
                        await session.rollback()
                        logger.error(
                            "Error monitoring alert ID %s (product %s): %s",
                            alert_id_str,
                            str(product_id),
                            alert_exc,
                        )

            except Exception as exc:
                await session.rollback()
                logger.error("Error executing Price Monitor background job loop: %s", exc)

        logger.info(
            "BACKGROUND JOB FINISHED: Checked %d alerts, triggered %d notifications, "
            "skipped %d invalid marketplace results.",
            alerts_checked,
            notifications_triggered,
            skipped_listings,
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
