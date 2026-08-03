"""
COMPAREX Backend – Brand Repository
"""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand import Brand
from app.repositories.base import BaseRepository


class BrandRepository(BaseRepository[Brand]):
    """Repository for Brand entity CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Brand, db)

    async def get_by_slug(self, slug: str) -> Brand | None:
        """Fetch brand by unique slug."""
        stmt = select(Brand).where(Brand.slug == slug)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_brands(self) -> Sequence[Brand]:
        """Fetch all registered brands."""
        stmt = select(Brand).order_by(Brand.name.asc())
        result = await self.db.execute(stmt)
        return result.scalars().all()
