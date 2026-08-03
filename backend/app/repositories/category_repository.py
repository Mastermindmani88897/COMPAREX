"""
COMPAREX Backend – Category Repository
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Repository for Category data access operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Category, db)

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        """Fetch category by unique slug."""
        result = await self.db.execute(
            select(Category).where(Category.slug == slug.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Category]:
        """Fetch category by unique name."""
        result = await self.db.execute(
            select(Category).where(Category.name.ilike(name))
        )
        return result.scalar_one_or_none()
