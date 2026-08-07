"""
COMPAREX Backend – Product Repository
"""

import uuid
from typing import Optional
from sqlalchemy import select, or_, and_, desc, asc
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

    async def search_products(
        self,
        skip: int = 0,
        limit: int = 100,
        query: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        in_stock_only: Optional[bool] = None,
        sort_by: Optional[str] = None,
        synonyms: Optional[list[str]] = None,
    ) -> list[Product]:
        """High-performance database-level product search with filters, pagination, and sorting."""
        stmt = select(Product).options(selectinload(Product.images))

        conditions = []

        if category and category.lower() != "all":
            conditions.append(Product.category.ilike(f"%{category.strip()}%"))

        if brand and brand.strip():
            conditions.append(Product.brand.ilike(f"%{brand.strip()}%"))

        if min_price is not None:
            conditions.append(Product.base_price >= min_price)

        if max_price is not None:
            conditions.append(Product.base_price <= max_price)

        if min_rating is not None:
            conditions.append(Product.rating >= min_rating)

        if in_stock_only:
            conditions.append(Product.stock_status == "in_stock")

        if query and query.strip():
            search_terms = [t.strip().lower() for t in query.split() if t.strip()]
            if synonyms:
                search_terms.extend([s.strip().lower() for s in synonyms if s.strip()])

            term_conds = []
            for term in search_terms:
                pat = f"%{term}%"
                term_conds.append(
                    or_(
                        Product.name.ilike(pat),
                        Product.category.ilike(pat),
                        Product.brand.ilike(pat),
                        Product.description.ilike(pat),
                        Product.search_keywords.ilike(pat),
                    )
                )

            if term_conds:
                conditions.append(or_(*term_conds))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Sorting logic
        if sort_by == "price_low":
            stmt = stmt.order_by(asc(Product.base_price))
        elif sort_by == "price_high":
            stmt = stmt.order_by(desc(Product.base_price))
        elif sort_by == "rating":
            stmt = stmt.order_by(desc(Product.rating))
        elif sort_by == "discount":
            stmt = stmt.order_by(desc(Product.discount_percentage))
        else:  # default popularity or newest
            stmt = stmt.order_by(desc(Product.popularity_score), desc(Product.rating))

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def search_by_name(self, query: str, limit: int = 50) -> list[Product]:
        """Full-text style search matching name, category, brand, or description."""
        return await self.search_products(skip=0, limit=limit, query=query)
