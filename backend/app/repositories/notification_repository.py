"""
COMPAREX Backend – Notification Repository
"""

import uuid
from typing import List, Optional
from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification data access operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Notification, db)

    async def get_by_user_id(
        self, user_id: uuid.UUID, limit: int = 50, unread_only: bool = False
    ) -> List[Notification]:
        """Fetch notifications for user sorted by newest first."""
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
        stmt = stmt.order_by(desc(Notification.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        """Get count of unread notifications for a user."""
        stmt = select(Notification).where(
            Notification.user_id == user_id, Notification.is_read.is_(False)
        )
        res = await self.db.execute(stmt)
        return len(list(res.scalars().all()))

    async def mark_as_read(
        self, notification_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Notification]:
        """Mark a single notification as read."""
        stmt = select(Notification).where(
            Notification.id == notification_id, Notification.user_id == user_id
        )
        res = await self.db.execute(stmt)
        item = res.scalar_one_or_none()
        if item:
            item.is_read = True
            await self.db.commit()
            await self.db.refresh(item)
        return item

    async def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        """Mark all unread notifications as read for a user."""
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount

    async def delete_notification(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete an individual notification."""
        stmt = delete(Notification).where(
            Notification.id == notification_id, Notification.user_id == user_id
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount > 0

    async def clear_all(self, user_id: uuid.UUID) -> int:
        """Delete all notifications for a user."""
        stmt = delete(Notification).where(Notification.user_id == user_id)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount
