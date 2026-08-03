"""
COMPAREX Backend – Marketplace Repository
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.marketplace import Marketplace
from app.repositories.base import BaseRepository


class MarketplaceRepository(BaseRepository[Marketplace]):
    """Repository for Marketplace data access operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Marketplace, db)

    async def get_by_slug(self, slug: str) -> Optional[Marketplace]:
        """Fetch marketplace by unique slug."""
        result = await self.db.execute(
            select(Marketplace).where(Marketplace.slug == slug.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Marketplace]:
        """Fetch marketplace by name."""
        result = await self.db.execute(
            select(Marketplace).where(Marketplace.name.ilike(name))
        )
        return result.scalar_one_or_none()
