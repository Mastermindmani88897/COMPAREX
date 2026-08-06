"""
COMPAREX Backend – Product Service
"""

from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductPublic, ProductUpdate

logger = get_logger(__name__)


class ProductService:
    """Service handling Product business operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ProductRepository(db)

    async def list_products(
        self,
        skip: int = 0,
        limit: int = 100,
        query: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> list[ProductPublic]:
        """List products with optional search query, category, brand, and price filter."""
        products = await self.repo.get_all(skip=skip, limit=limit)
        
        filtered = []
        for p in products:
            if query and query.strip():
                q = query.lower().strip()
                p_name = p.name.lower()
                p_brand = (p.brand or "").lower()
                p_cat = (p.category or "").lower()
                if q not in p_name and q not in p_brand and q not in p_cat:
                    continue
            if category and category.lower() != "all":
                if not p.category or category.lower() not in p.category.lower():
                    continue
            if brand and brand.strip():
                if not p.brand or brand.lower() not in p.brand.lower():
                    continue
            if min_price is not None and p.base_price and float(p.base_price) < min_price:
                continue
            if max_price is not None and p.base_price and float(p.base_price) > max_price:
                continue

            filtered.append(p)

        return [ProductPublic.model_validate(p) for p in filtered]

    async def autocomplete_suggestions(self, query: str, limit: int = 8) -> list[dict]:
        """Generate fast search autocomplete suggestions for search bar."""
        if not query or not query.strip():
            return []
        q = query.lower().strip()
        products = await self.repo.get_all(skip=0, limit=100)
        
        suggestions = []
        seen = set()
        for p in products:
            name = p.name
            brand = p.brand or ""
            cat = p.category or ""
            if q in name.lower() or q in brand.lower() or q in cat.lower():
                if name not in seen:
                    seen.add(name)
                    suggestions.append({
                        "id": str(p.id),
                        "name": name,
                        "brand": brand,
                        "category": cat,
                        "base_price": float(p.base_price) if p.base_price else None,
                        "image_url": p.image_url,
                    })
                    if len(suggestions) >= limit:
                        break

        # Fallback default suggestions for common queries
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
        """Get product by ID."""
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
