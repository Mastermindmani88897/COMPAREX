"""
COMPAREX Backend – Notification API Endpoints
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="Get User Notifications",
    description="Retrieve all in-app notifications and unread badge count for authenticated user.",
)
async def get_user_notifications(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user notifications endpoint."""
    service = NotificationService(db)
    res = await service.get_user_notifications(user_id=current_user.id)
    return SuccessResponse(message="Notifications retrieved successfully", data=res)


@router.patch(
    "/read",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="Mark Notifications as Read",
    description="Mark a single notification or all notifications as read.",
)
async def mark_notifications_read(
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark read endpoint."""
    service = NotificationService(db)
    notification_id = payload.get("notification_id")
    mark_all = payload.get("mark_all", False)

    if mark_all:
        count = await service.mark_all_read(current_user.id)
        return SuccessResponse(message=f"{count} notifications marked as read", data={"marked_count": count})
    elif notification_id:
        success = await service.mark_read(notification_id=notification_id, user_id=current_user.id)
        return SuccessResponse(message="Notification marked as read", data={"success": success})
    else:
        # Default mark all as read
        count = await service.mark_all_read(current_user.id)
        return SuccessResponse(message="Notifications marked as read", data={"marked_count": count})


@router.delete(
    "/{id}",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="Delete Notification",
    description="Delete an individual notification by ID.",
)
async def delete_notification(
    id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete notification endpoint."""
    service = NotificationService(db)
    success = await service.delete_notification(notification_id=id, user_id=current_user.id)
    return SuccessResponse(message="Notification deleted", data={"success": success})


@router.post(
    "/clear-all",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="Clear All Notifications",
    description="Clear all notifications for current user.",
)
async def clear_all_notifications(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear all notifications endpoint."""
    service = NotificationService(db)
    count = await service.clear_all(user_id=current_user.id)
    return SuccessResponse(message="All notifications cleared", data={"cleared_count": count})
