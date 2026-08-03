"""
COMPAREX Backend – ProductListing Service

Handles business logic for creating, updating, and fetching product
price listings per marketplace, including price comparison aggregation.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.product_listing_repository import ProductListingRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product_listing import (
    PriceCompareResult,
    ProductListingCreate,
    ProductListingPublic,
    ProductListingUpdate,
)

logger = get_logger(__name__)


class ProductListingService:
    """Service handling ProductListing business operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.listing_repo = ProductListingRepository(db)
        self.product_repo = ProductRepository(db)

    async def get_compare_result(self, product_id: UUID) -> PriceCompareResult:
        """Fetch all marketplace listings for a product and compute comparison stats."""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        listings = await self.listing_repo.get_by_product_id(product_id)
        listing_schemas = [ProductListingPublic.model_validate(lst) for lst in listings]

        available = [lst.price for lst in listing_schemas if lst.is_available]

        lowest = min(available) if available else None
        highest = max(available) if available else None
        avg = (
            Decimal(sum(available) / len(available)).quantize(Decimal("0.01"))
            if available
            else None
        )

        best_listing_id: Optional[UUID] = None
        if available and listing_schemas:
            for ls in listing_schemas:
                if ls.is_available and ls.price == lowest:
                    best_listing_id = ls.id
                    break

        return PriceCompareResult(
            product_id=product_id,
            product_name=product.name,
            listings=listing_schemas,
            lowest_price=lowest,
            highest_price=highest,
            average_price=avg,
            best_listing_id=best_listing_id,
        )

    async def create_listing(self, req: ProductListingCreate) -> ProductListingPublic:
        """Create or update a marketplace listing for a product."""

        existing = await self.listing_repo.get_by_product_and_marketplace(
            req.product_id, req.marketplace_id
        )
        if existing:
            update_data = req.model_dump(exclude={"product_id", "marketplace_id"})
            updated = await self.listing_repo.update(existing, update_data)
            logger.info(
                "Updated listing for product=%s marketplace=%s price=%s",
                req.product_id,
                req.marketplace_id,
                req.price,
            )
            return ProductListingPublic.model_validate(updated)

        listing = await self.listing_repo.create(req.model_dump())
        logger.info(
            "Created listing for product=%s marketplace=%s price=%s",
            req.product_id,
            req.marketplace_id,
            req.price,
        )
        return ProductListingPublic.model_validate(listing)

    async def update_listing(
        self, listing_id: UUID, req: ProductListingUpdate
    ) -> ProductListingPublic:
        """Update an existing product listing."""
        listing = await self.listing_repo.get_by_id(listing_id)
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found",
            )
        updated = await self.listing_repo.update(
            listing, req.model_dump(exclude_unset=True)
        )
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
