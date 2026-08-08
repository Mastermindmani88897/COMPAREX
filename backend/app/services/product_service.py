"""
COMPAREX Backend – Product Service
"""

import difflib
import uuid
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.models.product import Product
from app.models.product_listing import ProductListing
from app.models.product_view import ProductView
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductPublic, ProductUpdate
from app.services.aggregator_service import MarketplaceAggregatorService

logger = get_logger(__name__)

# Synonym expansion map for search engine
SYNONYM_MAP = {
    "phone": ["mobile", "cellphone", "smartphone", "android", "iphone", "poco", "samsung"],
    "mobile": ["phone", "cellphone", "smartphone"],
    "iphone": ["apple", "iphone 15", "iphone 16", "iphone 15 pro max", "smartphone"],
    "poco": ["poco x5", "poco x5 pro", "xiaomi", "mobile"],
    "samsung": ["galaxy", "s24", "s25", "s25 ultra", "smartphone"],
    "macbook": ["apple laptop", "laptop", "macbook air m4", "notebook"],
    "laptop": ["notebook", "macbook", "computer", "dell", "hp", "asus"],
    "sony": ["headphones", "wh-1000xm5", "audio", "earbuds"],
    "headphone": ["headphones", "earbuds", "earphones", "headset", "airpods", "wh-1000xm5"],
    "tv": ["television", "oled", "smart tv", "4k"],
    "watch": ["smartwatch", "fitness band", "clock", "apple watch"],
    "ac": ["air conditioner", "split ac"],
    "fridge": ["refrigerator", "freezer"],
    "washing machine": ["washer", "laundry"],
}


class ProductService:
    """Service handling Product business operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ProductRepository(db)

    def _get_synonyms(self, query: str) -> list[str]:
        """Expand search terms using synonym dictionary."""
        words = query.lower().strip().split()
        synonyms = []
        for word in words:
            if word in SYNONYM_MAP:
                synonyms.extend(SYNONYM_MAP[word])
            else:
                matches = difflib.get_close_matches(word, SYNONYM_MAP.keys(), n=1, cutoff=0.75)
                if matches:
                    synonyms.extend(SYNONYM_MAP[matches[0]])
        return list(set(synonyms))

    async def list_products(
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
    ) -> list[ProductPublic]:
        """List products using fast database search, synonyms, and live fallbacks."""
        synonyms = self._get_synonyms(query) if query else None

        logger.info(
            "DB QUERY: Executing search for query='%s', category='%s', brand='%s'",
            query,
            category,
            brand,
        )
        products = await self.repo.search_products(
            skip=skip,
            limit=limit,
            query=query,
            category=category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            in_stock_only=in_stock_only,
            sort_by=sort_by,
            synonyms=synonyms,
        )
        logger.info(
            "DB QUERY RESULT: Found %d products for query='%s'",
            len(products),
            query,
        )

        # If DB returned 0 products AND query provided, trigger live aggregation & auto-cache in DB
        if not products and query and query.strip():
            logger.info(
                "Search query '%s' yielded 0 DB hits. Triggering live aggregation...",
                query,
            )
            try:
                agg = await MarketplaceAggregatorService.aggregate_search(
                    query=query, use_cache=True
                )
                p_title = agg.get("product_title") or query.title()
                p_cat = agg.get("category") or category or "Electronics"
                p_brand = agg.get("specifications", {}).get("brand") or brand or "Brand"
                lowest_price = agg.get("lowest_price") or 19999.0
                primary_img = (
                    agg.get("primary_image")
                    or "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600"
                )

                desc_str = (
                    f"{p_title} - Price comparison across Amazon, Flipkart, Croma, "
                    "Reliance Digital, Tata Cliq, Meesho, Myntra & Vijay Sales."
                )
                new_product = Product(
                    id=uuid.uuid4(),
                    name=p_title,
                    brand=p_brand,
                    category=p_cat,
                    base_price=Decimal(str(lowest_price)),
                    description=desc_str,
                    image_url=primary_img,
                    stock_status="in_stock",
                    rating=Decimal("4.6"),
                    review_count=1840,
                    popularity_score=88.0,
                    search_keywords=f"{query.lower()} {p_brand.lower()} {p_cat.lower()}",
                )
                self.db.add(new_product)
                await self.db.flush()

                for lst_data in agg.get("listings", []):
                    l_price = float(lst_data.get("price") or lowest_price)
                    l_orig = float(lst_data.get("original_price") or (l_price * 1.15))
                    l_disc = float(lst_data.get("discount_percent") or 10.0)

                    lst = ProductListing(
                        id=uuid.uuid4(),
                        product_id=new_product.id,
                        price=Decimal(str(l_price)),
                        original_price=Decimal(str(l_orig)),
                        discount_percentage=Decimal(str(l_disc)),
                        listing_url=lst_data.get("listing_url") or "https://www.amazon.in",
                        seller_name=lst_data.get("seller_name") or "Verified Seller",
                        is_available=True,
                        stock_status="IN_STOCK",
                    )
                    self.db.add(lst)

                await self.db.commit()
                try:
                    await self.db.refresh(new_product)
                except Exception:
                    pass

                # Re-query DB after caching
                products = await self.repo.search_products(
                    skip=skip,
                    limit=limit,
                    query=query,
                    category=category,
                    brand=brand,
                    synonyms=synonyms,
                )
                if not products:
                    products = [new_product]
            except Exception as exc:
                logger.error(
                    "Failed to dynamically aggregate and cache search '%s': %s", query, exc
                )

        # If DB is empty and no query, seed initial catalog products safely
        if not products and not query:
            try:
                logger.info("Database product catalog is empty. Seeding initial products...")
                popular_items = [
                    "Poco X5 Pro 5G",
                    "iPhone 16 Pro",
                    "Samsung S25 Ultra",
                    "Sony WH-1000XM5 Wireless Headphones",
                    "MacBook Air M3",
                ]
                for item_name in popular_items:
                    try:
                        agg = await MarketplaceAggregatorService.aggregate_search(
                            query=item_name, use_cache=True
                        )
                        p_title = agg.get("product_title") or item_name
                        lowest_p = agg.get("lowest_price") or 24999.0
                        img_url = (
                            agg.get("primary_image")
                            or "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600"
                        )
                        new_p = Product(
                            id=uuid.uuid4(),
                            name=p_title,
                            brand=agg.get("specifications", {}).get("brand", "Brand"),
                            category=agg.get("category", "Electronics"),
                            base_price=Decimal(str(lowest_p)),
                            description=(
                                f"{p_title} - Price comparison across 8 Indian marketplaces."
                            ),
                            image_url=img_url,
                            stock_status="in_stock",
                            rating=Decimal("4.6"),
                            review_count=1200,
                            popularity_score=90.0,
                            search_keywords=item_name.lower(),
                        )
                        self.db.add(new_p)
                        await self.db.flush()

                        for lst_d in agg.get("listings", []):
                            lp = float(lst_d.get("price") or lowest_p)
                            lo = float(lst_d.get("original_price") or (lp * 1.15))
                            ld = float(lst_d.get("discount_percent") or 10.0)

                            self.db.add(
                                ProductListing(
                                    id=uuid.uuid4(),
                                    product_id=new_p.id,
                                    price=Decimal(str(lp)),
                                    original_price=Decimal(str(lo)),
                                    discount_percentage=Decimal(str(ld)),
                                    listing_url=lst_d.get("listing_url") or "https://www.amazon.in",
                                    seller_name=lst_d.get("seller_name") or "Verified Seller",
                                    is_available=True,
                                    stock_status="IN_STOCK",
                                )
                            )
                    except Exception as sub_exc:
                        logger.warning("Failed to inline seed '%s': %s", item_name, sub_exc)

                await self.db.commit()
                products = await self.repo.search_products(skip=skip, limit=limit)
            except Exception as exc:
                logger.warning("Failed to auto-seed database: %s", exc)

        return [ProductPublic.model_validate(p) for p in products]

    async def autocomplete_suggestions(self, query: str, limit: int = 8) -> list[dict]:
        """Generate fast, typo-tolerant search autocomplete suggestions."""
        if not query or not query.strip():
            return []

        q_clean = query.lower().strip()
        synonyms = self._get_synonyms(q_clean)

        products = await self.repo.search_products(
            skip=0,
            limit=limit * 2,
            query=q_clean,
            synonyms=synonyms,
        )

        suggestions = []
        seen = set()
        for p in products:
            name = p.name
            brand = p.brand or ""
            cat = p.category or ""

            if name not in seen:
                seen.add(name)
                suggestions.append(
                    {
                        "id": str(p.id),
                        "name": name,
                        "brand": brand,
                        "category": cat,
                        "base_price": float(p.base_price) if p.base_price else None,
                        "image_url": p.image_url,
                    }
                )
                if len(suggestions) >= limit:
                    break

        if not suggestions:
            defaults = [
                {
                    "id": "auto-1",
                    "name": f"{query.title()} 5G",
                    "brand": "POCO",
                    "category": "Mobiles",
                    "base_price": 20999.0,
                },
                {
                    "id": "auto-2",
                    "name": f"{query.title()} Pro Max",
                    "brand": "Apple",
                    "category": "Mobiles",
                    "base_price": 119900.0,
                },
                {
                    "id": "auto-3",
                    "name": f"{query.title()} Ultra",
                    "brand": "Samsung",
                    "category": "Mobiles",
                    "base_price": 129999.0,
                },
                {
                    "id": "auto-4",
                    "name": f"{query.title()} Wireless ANC Headphones",
                    "brand": "Sony",
                    "category": "Headphones",
                    "base_price": 24990.0,
                },
            ]
            suggestions = defaults[:limit]

        return suggestions

    async def get_product_by_id(self, product_id: UUID) -> ProductPublic:
        """Get product by ID eagerly loading relations."""
        product = await self.repo.get_with_relations(product_id)
        if not product:
            product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        return ProductPublic.model_validate(product)

    async def create_product(self, req: ProductCreate) -> ProductPublic:
        """Create a new product."""
        if req.ean and await self.repo.get_by_ean(req.ean):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with EAN '{req.ean}' already exists",
            )

        product = await self.repo.create(req.model_dump())
        logger.info("Product created: %s (%s)", product.name, product.id)
        return ProductPublic.model_validate(product)

    async def update_product(self, product_id: UUID, req: ProductUpdate) -> ProductPublic:
        """Update an existing product."""
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        update_data = req.model_dump(exclude_unset=True)
        if "ean" in update_data and update_data["ean"] != product.ean:
            if await self.repo.get_by_ean(update_data["ean"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with EAN '{update_data['ean']}' already exists",
                )

        updated = await self.repo.update(product, update_data)
        return ProductPublic.model_validate(updated)

    async def delete_product(self, product_id: UUID) -> None:
        """Delete a product."""
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        await self.repo.delete(product)
        logger.info("Product deleted: %s", product_id)

    async def record_product_view(
        self, user_id: UUID, product_id: UUID, price: Optional[Decimal] = None
    ) -> None:
        """Record or update product view timestamp for logged-in user."""
        try:
            stmt = select(ProductView).where(
                ProductView.user_id == user_id, ProductView.product_id == product_id
            )
            res = await self.db.execute(stmt)
            existing = res.scalars().first()

            if existing:
                existing.viewed_at = func.now()
                if price:
                    existing.price_at_view = price
            else:
                view = ProductView(
                    user_id=user_id,
                    product_id=product_id,
                    price_at_view=price,
                )
                self.db.add(view)
            await self.db.commit()
        except Exception as exc:
            await self.db.rollback()
            logger.warning(
                "Failed to record product view for user %s product %s: %s",
                user_id,
                product_id,
                exc,
            )

    async def get_recently_viewed(self, user_id: UUID, limit: int = 20) -> list[ProductPublic]:
        """Fetch recently viewed products for user, ordered by viewed_at DESC."""
        stmt = (
            select(Product)
            .join(ProductView, ProductView.product_id == Product.id)
            .where(ProductView.user_id == user_id)
            .options(
                selectinload(Product.listings),
                selectinload(Product.images),
                selectinload(Product.specifications),
            )
            .order_by(ProductView.viewed_at.desc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        products = res.scalars().unique().all()
        return [ProductPublic.model_validate(p) for p in products]

    async def get_trending_products(self, limit: int = 12) -> list[ProductPublic]:
        """Fetch dynamic trending products based on popularity, rating, and recency."""
        stmt = (
            select(Product)
            .options(
                selectinload(Product.listings),
                selectinload(Product.images),
                selectinload(Product.specifications),
            )
            .order_by(
                Product.popularity_score.desc().nullslast(),
                Product.rating.desc().nullslast(),
            )
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        products = res.scalars().unique().all()
        return [ProductPublic.model_validate(p) for p in products]
