"""
COMPAREX Backend – Shopping Memory API Endpoints

Manages user interaction history events (search, compare, wishlist) and memory timeline.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.memory import ShoppingMemoryCreate, ShoppingMemoryResponse
from app.services.memory_service import ShoppingMemoryService

router = APIRouter(tags=["Shopping Memory"])


@router.post(
    "/memory",
    response_model=SuccessResponse[ShoppingMemoryResponse],
    summary="Log Interaction Event to Shopping Memory",
    description="Log user search, product view, comparison, or alert event.",
)
async def log_memory(
    payload: ShoppingMemoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log memory interaction event."""
    res = await ShoppingMemoryService.log_memory(db, current_user.id, payload)
    return SuccessResponse(message="Interaction event logged to memory", data=res)


@router.get(
    "/memory",
    response_model=SuccessResponse[List[ShoppingMemoryResponse]],
    summary="Retrieve Shopping Memory Timeline",
    description="Retrieve user interaction memory history.",
)
async def get_memories(
    memory_type: Optional[str] = Query(None, description="Filter by event type"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve shopping memory timeline."""
    res = await ShoppingMemoryService.get_memories(db, current_user.id, memory_type)
    return SuccessResponse(message="Shopping memory retrieved successfully", data=res)


@router.delete(
    "/memory",
    response_model=SuccessResponse[bool],
    summary="Clear Shopping Memory Timeline",
    description="Purge user interaction history timeline from memory.",
)
async def clear_memory(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear memory timeline."""
    res = await ShoppingMemoryService.clear_memories(db, current_user.id)
    return SuccessResponse(message="Shopping memory cleared successfully", data=res)
