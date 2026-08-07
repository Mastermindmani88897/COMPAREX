"""
COMPAREX Backend – Notification Service
"""

import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository

logger = get_logger(__name__)


class NotificationService:
    """Service handling notification CRUD, unread badges, and triggers."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = NotificationRepository(db)

    async def get_user_notifications(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Fetch notifications list and unread badge count."""
        items = await self.repo.get_by_user_id(user_id, limit=50)
        unread_count = await self.repo.get_unread_count(user_id)

        notifications_data = [
            {
                "id": str(n.id),
                "user_id": str(n.user_id),
                "product_id": str(n.product_id) if n.product_id else None,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "target_price": float(n.target_price) if n.target_price else None,
                "current_price": float(n.current_price) if n.current_price else None,
                "marketplace": n.marketplace or "Store",
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in items
        ]

        return {
            "unread_count": unread_count,
            "total_count": len(items),
            "notifications": notifications_data,
        }

    async def create_notification(
        self,
        user_id: uuid.UUID,
        title: str,
        message: str,
        type: str = "price_drop",
        product_id: Optional[uuid.UUID] = None,
        target_price: Optional[Decimal] = None,
        current_price: Optional[Decimal] = None,
        marketplace: Optional[str] = None,
    ) -> Notification:
        """Create a new notification for user."""
        notif = await self.repo.create(
            {
                "user_id": user_id,
                "product_id": product_id,
                "title": title,
                "message": message,
                "type": type,
                "target_price": target_price,
                "current_price": current_price,
                "marketplace": marketplace,
                "is_read": False,
            }
        )
        logger.info("Notification created for user %s: %s", user_id, title)
        return notif

    async def mark_read(self, notification_id: str, user_id: uuid.UUID) -> bool:
        """Mark a single notification as read."""
        try:
            nid = uuid.UUID(notification_id)
            res = await self.repo.mark_as_read(nid, user_id)
            return res is not None
        except Exception as exc:
            logger.warning("Failed to mark notification read: %s", exc)
            return False

    async def mark_all_read(self, user_id: uuid.UUID) -> int:
        """Mark all unread notifications as read."""
        return await self.repo.mark_all_as_read(user_id)

    async def delete_notification(self, notification_id: str, user_id: uuid.UUID) -> bool:
        """Delete an individual notification."""
        try:
            nid = uuid.UUID(notification_id)
            return await self.repo.delete_notification(nid, user_id)
        except Exception as exc:
            logger.warning("Failed to delete notification: %s", exc)
            return False

    async def clear_all(self, user_id: uuid.UUID) -> int:
        """Clear all notifications for user."""
        return await self.repo.clear_all(user_id)
