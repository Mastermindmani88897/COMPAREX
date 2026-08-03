"""
COMPAREX Backend – PriceHistory Repository
"""

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_history import PriceHistory
from app.repositories.base import BaseRepository


class PriceHistoryRepository(BaseRepository[PriceHistory]):
    """Repository for PriceHistory entity."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(PriceHistory, db)

    async def get_by_listing_id(
        self, listing_id: uuid.UUID, limit: int = 50
    ) -> Sequence[PriceHistory]:
        """Fetch historical price points for a specific listing."""
        stmt = (
            select(PriceHistory)
            .where(PriceHistory.listing_id == listing_id)
            .order_by(PriceHistory.timestamp.asc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
