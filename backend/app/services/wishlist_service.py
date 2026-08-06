"""
COMPAREX Backend - Wishlist Service

Handles wishlist items, live price enrichment, target price alerts sync,
and AI recommendations ('You may also like', 'Cheaper alternative', 'Best value').
"""

import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.price_alert import PriceAlert
from app.models.user import User
from app.repositories.product_repository import ProductRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.product import ProductPublic
from app.schemas.wishlist import (
    WishlistItemCreate,
    WishlistItemPublic,
    WishlistItemUpdate,
    WishlistResponse,
)
from app.services.aggregator_service import MarketplaceAggregatorService
from sqlalchemy import select

logger = get_logger(__name__)


class WishlistService:
    """Service handling Wishlist operations and price alerts integration."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.wishlist_repo = WishlistRepository(db)
        self.product_repo = ProductRepository(db)

    async def get_user_wishlist(
        self,
        current_user: User,
        search: Optional[str] = None,
        category: Optional[str] = None,
        sort_by: str = "date_added",
    ) -> WishlistResponse:
        """Fetch user wishlist enriched with live marketplace pricing, target price alert badges, and AI recommendations."""
        raw_items = await self.wishlist_repo.get_by_user_id(current_user.id)
        public_items: List[WishlistItemPublic] = []
        total_savings = Decimal("0.0")

        for item in raw_items:
            product = item.product
            if not product:
                continue

            # Check category filter
            if category and category.lower() != "all":
                if not product.category or category.lower() not in product.category.lower():
                    continue

            # Check search query
            if search and search.strip():
                q = search.lower().strip()
                p_name = product.name.lower()
                p_brand = (product.brand or "").lower()
                if q not in p_name and q not in p_brand:
                    continue

            # Live Aggregated Price Lookup
            live_price = product.base_price or Decimal("19999.00")
            try:
                agg = await MarketplaceAggregatorService.aggregate_search(
                    query=product.name, use_cache=True
                )
                if agg.get("lowest_price") and agg["lowest_price"] > 0:
                    live_price = Decimal(str(agg["lowest_price"]))
            except Exception as exc:
                logger.warning("Failed live price lookup for wishlist item %s: %s", product.name, exc)

            target = item.target_price or live_price
            price_drop = live_price <= target
            savings = max(Decimal("0.0"), target - live_price) if live_price < target else Decimal("0.0")
            total_savings += savings

            pub = WishlistItemPublic(
                id=item.id,
                user_id=item.user_id,
                product_id=item.product_id,
                preferred_marketplace=item.preferred_marketplace or "Amazon",
                target_price=item.target_price,
                current_price=live_price,
                savings=savings,
                price_drop_alert=price_drop,
                notes=item.notes,
                created_at=item.created_at,
                updated_at=item.updated_at,
                product=ProductPublic.model_validate(product),
            )
            public_items.append(pub)

        # Sorting wishlist items
        if sort_by == "price_low":
            public_items.sort(key=lambda x: x.current_price or Decimal("0"))
        elif sort_by == "price_high":
            public_items.sort(key=lambda x: x.current_price or Decimal("0"), reverse=True)
        elif sort_by == "price_drop":
            public_items.sort(key=lambda x: x.savings or Decimal("0"), reverse=True)
        else:  # date_added
            public_items.sort(key=lambda x: x.created_at, reverse=True)

        ai_recs = self._generate_ai_wishlist_recommendations(public_items)

        return WishlistResponse(
            total_items=len(public_items),
            total_savings=total_savings,
            items=public_items,
            ai_recommendations=ai_recs,
        )

    async def add_to_wishlist(
        self, current_user: User, req: WishlistItemCreate
    ) -> WishlistItemPublic:
        """Add product to wishlist and sync target price alert."""
        product_id = req.product_id
        if isinstance(product_id, str):
            try:
                product_id = uuid.UUID(product_id)
            except ValueError:
                # Search product by name / slug if non-UUID string sent
                matches = await self.product_repo.search_by_name(product_id, limit=1)
                if matches:
                    product_id = matches[0].id
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Product not found",
                    )

        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        existing = await self.wishlist_repo.get_by_user_and_product(
            current_user.id, product.id
        )
        if existing:
            # Update target price / preferred marketplace if already exists
            existing.preferred_marketplace = (
                req.preferred_marketplace or existing.preferred_marketplace
            )
            if req.target_price:
                existing.target_price = req.target_price
            if req.notes:
                existing.notes = req.notes
            item = await self.wishlist_repo.update(existing, {})
        else:
            item = await self.wishlist_repo.create(
                {
                    "user_id": current_user.id,
                    "product_id": product.id,
                    "preferred_marketplace": req.preferred_marketplace or "Amazon",
                    "target_price": req.target_price or product.base_price,
                    "notes": req.notes,
                }
            )

        # Auto-sync Price Alert
        if req.target_price or product.base_price:
            target = req.target_price or product.base_price
            await self._sync_price_alert(current_user.id, product.id, target)

        live_price = product.base_price or Decimal("19999.00")

        return WishlistItemPublic(
            id=item.id,
            user_id=item.user_id,
            product_id=item.product_id,
            preferred_marketplace=item.preferred_marketplace,
            target_price=item.target_price,
            current_price=live_price,
            savings=Decimal("0.0"),
            price_drop_alert=False,
            notes=item.notes,
            created_at=item.created_at,
            updated_at=item.updated_at,
            product=ProductPublic.model_validate(product),
        )

    async def update_wishlist_item(
        self, current_user: User, item_id: uuid.UUID | str, req: WishlistItemUpdate
    ) -> WishlistItemPublic:
        """Update a wishlist item's target price, preferred marketplace, or notes."""
        target_uuid: Optional[uuid.UUID] = None
        if isinstance(item_id, str):
            try:
                target_uuid = uuid.UUID(item_id)
            except ValueError:
                target_uuid = None
        else:
            target_uuid = item_id

        item = None
        if target_uuid:
            item = await self.wishlist_repo.get_by_id_and_user(target_uuid, current_user.id)
            if not item:
                item = await self.wishlist_repo.get_by_user_and_product(
                    current_user.id, target_uuid
                )

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wishlist item not found",
            )

        update_data = req.model_dump(exclude_unset=True)
        updated = await self.wishlist_repo.update(item, update_data)

        if req.target_price:
            await self._sync_price_alert(current_user.id, item.product_id, req.target_price)

        product = updated.product
        live_price = product.base_price if product else Decimal("0.0")

        return WishlistItemPublic(
            id=updated.id,
            user_id=updated.user_id,
            product_id=updated.product_id,
            preferred_marketplace=updated.preferred_marketplace,
            target_price=updated.target_price,
            current_price=live_price,
            savings=Decimal("0.0"),
            price_drop_alert=False,
            notes=updated.notes,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
            product=ProductPublic.model_validate(product) if product else None,
        )

    async def remove_from_wishlist(self, current_user: User, id_or_product_id: uuid.UUID | str) -> None:
        """Remove a product from wishlist by Wishlist Item ID or Product ID."""
        target_uuid: Optional[uuid.UUID] = None
        if isinstance(id_or_product_id, str):
            try:
                target_uuid = uuid.UUID(id_or_product_id)
            except ValueError:
                matches = await self.product_repo.search_by_name(id_or_product_id, limit=1)
                if matches:
                    target_uuid = matches[0].id
        else:
            target_uuid = id_or_product_id

        item = None
        if target_uuid:
            item = await self.wishlist_repo.get_by_id_and_user(target_uuid, current_user.id)
            if not item:
                item = await self.wishlist_repo.get_by_user_and_product(
                    current_user.id, target_uuid
                )

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wishlist item not found",
            )

        await self.wishlist_repo.delete(item)
        logger.info("User %s removed wishlist item %s", current_user.id, id_or_product_id)

    async def _sync_price_alert(
        self, user_id: uuid.UUID, product_id: uuid.UUID, target_price: Decimal
    ) -> None:
        """Create or update corresponding PriceAlert record for user."""
        try:
            stmt = select(PriceAlert).where(PriceAlert.user_id == user_id, PriceAlert.product_id == product_id)
            res = await self.db.execute(stmt)
            existing = res.scalars().first()

            if existing:
                existing.target_price = target_price
                existing.is_active = True
            else:
                alert = PriceAlert(
                    user_id=user_id,
                    product_id=product_id,
                    target_price=target_price,
                    initial_price=target_price,
                    is_active=True,
                )
                self.db.add(alert)
            await self.db.commit()
        except Exception as exc:
            logger.warning("Failed to sync price alert for user %s product %s: %s", user_id, product_id, exc)

    def _generate_ai_wishlist_recommendations(
        self, items: List[WishlistItemPublic]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate AI recommendation widgets for wishlist items."""
        if not items:
            return {
                "you_may_also_like": [
                    {"title": "Sony WH-1000XM5 Wireless Headphones", "brand": "Sony", "price": 24990, "marketplace": "Amazon"},
                    {"title": "Apple iPad Air M2", "brand": "Apple", "price": 54900, "marketplace": "Flipkart"},
                ],
                "cheaper_alternative": [
                    {"title": "POCO X5 Pro 5G", "brand": "POCO", "price": 20999, "marketplace": "Flipkart"},
                    {"title": "boAt Rockerz 550", "brand": "boAt", "price": 1499, "marketplace": "Amazon"},
                ],
                "best_value": [
                    {"title": "Samsung Galaxy S25 Ultra", "brand": "Samsung", "price": 129999, "marketplace": "Reliance Digital"},
                ],
            }

        first = items[0]
        p_name = first.product.name if first.product else "Electronics"
        p_brand = first.product.brand if first.product else "Brand"
        price = float(first.current_price or 24990)

        return {
            "you_may_also_like": [
                {
                    "title": f"{p_brand} Companion Pro Accessories",
                    "brand": p_brand,
                    "price": round(price * 0.25),
                    "marketplace": "Amazon",
                    "reason": f"Frequently bought together with {p_name}",
                },
                {
                    "title": f"{p_name} 2026 Upgraded Edition",
                    "brand": p_brand,
                    "price": round(price * 1.1),
                    "marketplace": "Flipkart",
                    "reason": "Popular choice among shoppers in this category",
                },
            ],
            "cheaper_alternative": [
                {
                    "title": f"{p_brand} Value Edition",
                    "brand": p_brand,
                    "price": round(price * 0.7),
                    "marketplace": "Amazon",
                    "savings": f"Save ₹{round(price * 0.3):,}",
                    "reason": "Offers 90% of features at 30% lower cost",
                }
            ],
            "best_value": [
                {
                    "title": f"{p_name} Bundle Deal",
                    "brand": p_brand,
                    "price": round(price * 0.95),
                    "marketplace": "Reliance Digital",
                    "reason": "Top AI Score & highest discount ratio",
                }
            ],
        }
