"""
COMPAREX Backend – Product Repository
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repository for Product data access operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Product, db)

    async def get_by_ean(self, ean: str) -> Optional[Product]:
        """Fetch a product by EAN barcode."""
        result = await self.db.execute(
            select(Product).where(Product.ean == ean)
        )
        return result.scalar_one_or_none()

    async def search_by_name(self, query: str, limit: int = 20) -> list[Product]:
        """Full-text-style name search (basic ILIKE — Phase 2 will use proper FTS)."""
        result = await self.db.execute(
            select(Product)
            .where(Product.name.ilike(f"%{query}%"))
            .limit(limit)
        )
        return list(result.scalars().all())
