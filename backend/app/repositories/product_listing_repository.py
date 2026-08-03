"""
COMPAREX Backend – ProductListing Repository
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product_listing import ProductListing
from app.repositories.base import BaseRepository


class ProductListingRepository(BaseRepository[ProductListing]):
    """Repository for ProductListing data access operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(ProductListing, db)

    async def get_by_product_id(self, product_id: UUID) -> list[ProductListing]:
        """Fetch all marketplace listings for a given product, with marketplace eagerly loaded."""
        result = await self.db.execute(
            select(ProductListing)
            .where(ProductListing.product_id == product_id)
            .options(selectinload(ProductListing.marketplace))
            .order_by(ProductListing.price.asc())
        )
        return list(result.scalars().all())

    async def get_by_product_and_marketplace(
        self, product_id: UUID, marketplace_id: UUID
    ) -> Optional[ProductListing]:
        """Fetch a specific listing by product + marketplace combination."""
        result = await self.db.execute(
            select(ProductListing)
            .where(
                ProductListing.product_id == product_id,
                ProductListing.marketplace_id == marketplace_id,
            )
            .options(selectinload(ProductListing.marketplace))
        )
        return result.scalar_one_or_none()
