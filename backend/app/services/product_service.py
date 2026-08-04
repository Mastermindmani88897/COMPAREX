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
    ) -> list[ProductPublic]:
        """List products with optional search query."""
        if query:
            products = await self.repo.search_by_name(query=query, limit=limit)
        else:
            products = await self.repo.get_all(skip=skip, limit=limit)
        return [ProductPublic.model_validate(p) for p in products]

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
