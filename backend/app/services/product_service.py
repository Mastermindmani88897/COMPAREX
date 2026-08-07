"""
COMPAREX Backend – Product Service
"""

import difflib
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductPublic, ProductUpdate

logger = get_logger(__name__)

# Synonym expansion map for search engine
SYNONYM_MAP = {
    "phone": ["mobile", "cellphone", "smartphone", "android", "iphone"],
    "mobile": ["phone", "cellphone", "smartphone"],
    "laptop": ["notebook", "macbook", "computer"],
    "macbook": ["apple laptop", "laptop"],
    "tv": ["television", "oled", "smart tv", "4k"],
    "television": ["tv", "smart tv"],
    "headphone": ["headphones", "earbuds", "earphones", "headset", "airpods"],
    "earbuds": ["headphones", "tws", "earphones"],
    "watch": ["smartwatch", "fitness band", "clock"],
    "smartwatch": ["watch", "fitness tracker"],
    "shoe": ["shoes", "sneakers", "footwear"],
    "sneakers": ["shoes", "running shoes", "footwear"],
    "ac": ["air conditioner", "split ac"],
    "fridge": ["refrigerator", "freezer"],
    "washing machine": ["washer", "laundry"],
    "vacuum": ["cleaner", "cordless vacuum"],
    "serum": ["skincare", "moisturizer"],
    "chair": ["office chair", "furniture"],
    "bed": ["queen bed", "furniture"],
    "sofa": ["couch", "furniture"],
    "dal": ["pulses", "groceries"],
    "oil": ["olive oil", "sunflower oil"],
    "book": ["novel", "paperback"],
    "toy": ["lego", "doll", "kids"],
    "racket": ["badminton", "sports"],
    "tyre": ["car tyre", "automotive"],
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
                # Fuzzy match against synonym keys for typo correction
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
        """List products using fast database-level search, synonyms, and filters."""
        synonyms = self._get_synonyms(query) if query else None

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
                {"id": "auto-1", "name": f"{query.title()} 5G", "brand": "POCO", "category": "Mobiles", "base_price": 20999.0},
                {"id": "auto-2", "name": f"{query.title()} Pro Max", "brand": "Apple", "category": "Mobiles", "base_price": 119900.0},
                {"id": "auto-3", "name": f"{query.title()} Ultra", "brand": "Samsung", "category": "Mobiles", "base_price": 129999.0},
                {"id": "auto-4", "name": f"{query.title()} Wireless ANC Headphones", "brand": "Sony", "category": "Headphones", "base_price": 24990.0},
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
