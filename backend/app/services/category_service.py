"""
COMPAREX Backend – Category Service
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryPublic, CategoryUpdate

logger = get_logger(__name__)


class CategoryService:
    """Service handling Category operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = CategoryRepository(db)

    async def list_categories(
        self, skip: int = 0, limit: int = 100
    ) -> list[CategoryPublic]:
        """Fetch all categories with pagination."""
        categories = await self.repo.get_all(skip=skip, limit=limit)
        return [CategoryPublic.model_validate(c) for c in categories]

    async def get_category_by_id(self, category_id: UUID) -> CategoryPublic:
        """Fetch a single category by ID."""
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        return CategoryPublic.model_validate(category)

    async def create_category(self, req: CategoryCreate) -> CategoryPublic:
        """Create a new product category."""
        if await self.repo.get_by_slug(req.slug):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category slug '{req.slug}' already exists",
            )

        if await self.repo.get_by_name(req.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category name '{req.name}' already exists",
            )

        category = await self.repo.create(req.model_dump())
        logger.info("Category created: %s (%s)", category.name, category.id)
        return CategoryPublic.model_validate(category)

    async def update_category(
        self, category_id: UUID, req: CategoryUpdate
    ) -> CategoryPublic:
        """Update an existing category."""
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        update_data = req.model_dump(exclude_unset=True)

        if "slug" in update_data and update_data["slug"] != category.slug:
            if await self.repo.get_by_slug(update_data["slug"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category slug '{update_data['slug']}' already exists",
                )

        updated = await self.repo.update(category, update_data)
        return CategoryPublic.model_validate(updated)

    async def delete_category(self, category_id: UUID) -> None:
        """Delete a category by ID."""
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        await self.repo.delete(category)
        logger.info("Category deleted: %s", category_id)
