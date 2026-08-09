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
        """Product search with multi-stage relevance scoring and accessory filtering."""
        from app.services.search_engine import SearchEngineService

        stmt = select(Product).options(selectinload(Product.images))

        conditions = [Product.is_quarantined.is_(False)]

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

        intent = SearchEngineService.parse_intent(query) if query and query.strip() else None

        if intent and intent.normalized_query:
            term_conds = []
            for term in intent.tokens:
                if len(term) >= 2:
                    pat = f"%{term}%"
                    term_conds.append(
                        or_(
                            Product.name.ilike(pat),
                            Product.category.ilike(pat),
                            Product.brand.ilike(pat),
                            Product.search_keywords.ilike(pat),
                        )
                    )
            if intent.brand:
                term_conds.append(Product.brand.ilike(f"%{intent.brand}%"))
            if intent.model:
                term_conds.append(Product.name.ilike(f"%{intent.model}%"))

            if term_conds:
                conditions.append(or_(*term_conds))

            # If explicit brand intent was detected (e.g. Apple), prioritize matching brand
            if intent.brand:
                conditions.append(
                    or_(
                        Product.brand.ilike(f"%{intent.brand}%"),
                        Product.name.ilike(f"%{intent.brand}%"),
                    )
                )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Default sorting by DB if no query provided
        if not query or not query.strip():
            if sort_by == "price_low":
                stmt = stmt.order_by(asc(Product.base_price))
            elif sort_by == "price_high":
                stmt = stmt.order_by(desc(Product.base_price))
            elif sort_by == "rating":
                stmt = stmt.order_by(desc(Product.rating))
            elif sort_by == "discount":
                stmt = stmt.order_by(desc(Product.discount_percentage))
            else:
                stmt = stmt.order_by(desc(Product.popularity_score), desc(Product.rating))

            stmt = stmt.offset(skip).limit(limit)
            result = await self.db.execute(stmt)
            return list(result.scalars().all())

        # If query IS provided: fetch candidate pool (limit 250) and score/filter strictly
        stmt = stmt.limit(300)
        result = await self.db.execute(stmt)
        candidates = list(result.scalars().all())

        # Stage 3, 4, 5: Filter, score, rank candidates using SearchEngineService
        ranked = SearchEngineService.filter_and_rank_products(
            products=candidates,
            raw_query=query,
            min_threshold=35.0,
        )

        # Apply user sort override if requested
        if sort_by == "price_low":
            ranked.sort(key=lambda p: float(p.base_price or 0))
        elif sort_by == "price_high":
            ranked.sort(key=lambda p: float(p.base_price or 0), reverse=True)
        elif sort_by == "rating":
            ranked.sort(key=lambda p: float(p.rating or 0), reverse=True)

        return ranked[skip : skip + limit]

    async def search_by_name(self, query: str, limit: int = 50) -> list[Product]:
        """Full-text style search matching name, category, brand, or description."""
        return await self.search_products(skip=0, limit=limit, query=query)
