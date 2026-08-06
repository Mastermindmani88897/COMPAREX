"""
COMPAREX Backend – Product Repository
"""

import uuid
from typing import Optional
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repository for Product data access operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Product, db)

    async def get_with_relations(self, product_id: uuid.UUID) -> Optional[Product]:
        """Fetch a product by ID eagerly loading listings, specs, and images."""
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(
                selectinload(Product.listings),
                selectinload(Product.specifications),
                selectinload(Product.images),
            )
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_by_ean(self, ean: str) -> Optional[Product]:
        """Fetch a product by EAN barcode."""
        result = await self.db.execute(select(Product).where(Product.ean == ean))
        return result.scalar_one_or_none()

    async def search_by_name(self, query: str, limit: int = 50) -> list[Product]:
        """Full-text style search matching name, category, brand, or description."""
        terms = [t.strip() for t in query.split() if t.strip()]
        if not terms:
            result = await self.db.execute(select(Product).limit(limit))
            return list(result.scalars().all())

        # Match all terms across Product fields
        conditions = []
        for term in terms:
            pattern = f"%{term}%"
            conditions.append(
                or_(
                    Product.name.ilike(pattern),
                    Product.category.ilike(pattern),
                    Product.brand.ilike(pattern),
                    Product.description.ilike(pattern),
                )
            )

        stmt = select(Product).where(and_(*conditions)).limit(limit)
        result = await self.db.execute(stmt)
        products = list(result.scalars().all())

        if not products:
            # Fallback to matching ANY term if ALL terms match returns 0
            any_conditions = []
            for term in terms:
                pattern = f"%{term}%"
                any_conditions.append(
                    or_(
                        Product.name.ilike(pattern),
                        Product.category.ilike(pattern),
                        Product.brand.ilike(pattern),
                    )
                )
            stmt_any = select(Product).where(or_(*any_conditions)).limit(limit)
            res_any = await self.db.execute(stmt_any)
            products = list(res_any.scalars().all())

        return products
