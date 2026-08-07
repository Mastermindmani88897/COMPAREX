"""
COMPAREX Backend - Wishlist Repository
"""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.models.wishlist import Wishlist
from app.repositories.base import BaseRepository


class WishlistRepository(BaseRepository[Wishlist]):
    """Repository handling Wishlist database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Wishlist, db)

    async def get_by_user_id(self, user_id: uuid.UUID) -> List[Wishlist]:
        """Fetch all wishlist items for a given user with eager product loading."""
        stmt = (
            select(Wishlist)
            .where(Wishlist.user_id == user_id)
            .options(
                selectinload(Wishlist.product).selectinload(Product.images),
            )
            .order_by(Wishlist.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_by_user_and_product(
        self, user_id: uuid.UUID, product_id: uuid.UUID
    ) -> Optional[Wishlist]:
        """Fetch wishlist item for a specific user and product combination."""
        stmt = (
            select(Wishlist)
            .where(Wishlist.user_id == user_id, Wishlist.product_id == product_id)
            .options(
                selectinload(Wishlist.product).selectinload(Product.images),
            )
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_by_id_and_user(
        self, wishlist_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Wishlist]:
        """Fetch wishlist item by ID ensuring user ownership."""
        stmt = (
            select(Wishlist)
            .where(Wishlist.id == wishlist_id, Wishlist.user_id == user_id)
            .options(
                selectinload(Wishlist.product).selectinload(Product.images),
            )
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()
