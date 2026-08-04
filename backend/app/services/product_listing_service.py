"""
COMPAREX Backend - ProductListing Service

Handles business logic for creating, updating, and fetching product
price listings per marketplace, including price comparison aggregation
and automatic price history recording.
"""

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.price_history_repository import PriceHistoryRepository
from app.repositories.product_listing_repository import ProductListingRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product_listing import (
    PriceCompareResult,
    ProductListingCreate,
    ProductListingPublic,
    ProductListingUpdate,
)
from app.services.comparison_engine import ComparisonEngineService

logger = get_logger(__name__)


class ProductListingService:
    """Service handling ProductListing business operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.listing_repo = ProductListingRepository(db)
        self.product_repo = ProductRepository(db)
        self.history_repo = PriceHistoryRepository(db)

    async def get_compare_result(self, product_id: UUID) -> PriceCompareResult:
        """Fetch all marketplace listings for a product and compute comparison stats.

        Delegates to ComparisonEngineService for badge assignment and
        weighted deal-score calculation.
        """
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        listings = await self.listing_repo.get_by_product_id(product_id)

        # Build raw listing dicts for ComparisonEngineService
        raw_listings = []
        for lst in listings:
            m = lst.marketplace
            raw_listings.append(
                {
                    "id": str(lst.id),
                    "product_id": str(lst.product_id),
                    "marketplace_id": str(lst.marketplace_id),
                    "price": float(lst.price),
                    "original_price": float(lst.original_price) if lst.original_price else None,
                    "discount_percent": (
                        float(lst.discount_percent) if lst.discount_percent else None
                    ),
                    "currency": lst.currency,
                    "listing_url": lst.listing_url,
                    "marketplace_product_id": lst.marketplace_product_id,
                    "seller_name": lst.seller_name,
                    "is_available": lst.is_available,
                    "is_prime": lst.is_prime,
                    "stock_status": lst.stock_status,
                    "delivery_estimate": lst.delivery_estimate,
                    "rating": float(lst.rating) if lst.rating else None,
                    "review_count": lst.review_count,
                    "marketplace": (
                        {
                            "id": str(m.id),
                            "name": m.name,
                            "slug": m.slug,
                            "logo_url": m.logo_url,
                            "base_url": m.base_url,
                        }
                        if m
                        else None
                    ),
                    "created_at": lst.created_at,
                    "updated_at": lst.updated_at,
                }
            )

        matrix = ComparisonEngineService.calculate_comparison_matrix(
            product_id=str(product.id),
            product_name=product.name,
            listings=raw_listings,
        )
        return PriceCompareResult(**matrix)

    async def _record_price_history(self, listing_id: UUID, price: Decimal, currency: str) -> None:
        """Write a PriceHistory record if we have a new price point."""
        try:
            await self.history_repo.create(
                {
                    "listing_id": listing_id,
                    "price": price,
                    "currency": currency,
                }
            )
        except Exception as exc:
            # Non-critical: log and continue — do not let history write fail the listing op
            logger.warning("Failed to write price history for listing %s: %s", listing_id, exc)

    async def create_listing(self, req: ProductListingCreate) -> ProductListingPublic:
        """Create or update a marketplace listing for a product.

        If a listing already exists for this product+marketplace combination,
        it will be updated (upsert behaviour). When a price change occurs, a
        PriceHistory record is automatically written.
        """
        existing = await self.listing_repo.get_by_product_and_marketplace(
            req.product_id, req.marketplace_id
        )
        if existing:
            old_price = existing.price
            update_data = req.model_dump(exclude={"product_id", "marketplace_id"})
            updated = await self.listing_repo.update(existing, update_data)
            logger.info(
                "Updated listing for product=%s marketplace=%s price=%s",
                req.product_id,
                req.marketplace_id,
                req.price,
            )
            # Record price history if price changed
            if Decimal(str(req.price)) != old_price:
                await self._record_price_history(updated.id, updated.price, updated.currency)
            return ProductListingPublic.model_validate(updated)

        listing = await self.listing_repo.create(req.model_dump())
        logger.info(
            "Created listing for product=%s marketplace=%s price=%s",
            req.product_id,
            req.marketplace_id,
            req.price,
        )
        # Record the initial price as first history point
        await self._record_price_history(listing.id, listing.price, listing.currency)
        return ProductListingPublic.model_validate(listing)

    async def update_listing(
        self, listing_id: UUID, req: ProductListingUpdate
    ) -> ProductListingPublic:
        """Update an existing product listing. Records price history on price change."""
        listing = await self.listing_repo.get_by_id(listing_id)
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found",
            )
        old_price = listing.price
        update_data = req.model_dump(exclude_unset=True)
        updated = await self.listing_repo.update(listing, update_data)

        # Record price history if price changed
        new_price = update_data.get("price")
        if new_price is not None and Decimal(str(new_price)) != old_price:
            await self._record_price_history(updated.id, updated.price, updated.currency)

        return ProductListingPublic.model_validate(updated)

    async def delete_listing(self, listing_id: UUID) -> None:
        """Delete a product listing."""
        listing = await self.listing_repo.get_by_id(listing_id)
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found",
            )
        await self.listing_repo.delete(listing)
        logger.info("Deleted listing %s", listing_id)
