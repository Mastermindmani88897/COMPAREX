"""
COMPAREX Backend – Shopping Memory Service

Logs and retrieves user interaction history events and provides clear-memory features.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shopping_memory import ShoppingMemory
from app.schemas.memory import ShoppingMemoryCreate, ShoppingMemoryResponse


class ShoppingMemoryService:
    """Shopping Memory event logging and recall service."""

    @classmethod
    async def log_memory(
        cls,
        db: AsyncSession,
        user_id: UUID,
        payload: ShoppingMemoryCreate,
    ) -> ShoppingMemoryResponse:
        """Log new interaction event into Shopping Memory."""
        memory = ShoppingMemory(
            user_id=user_id,
            memory_type=payload.memory_type,
            query=payload.query,
            product_id=payload.product_id,
            details=payload.details,
        )
        db.add(memory)
        await db.commit()
        await db.refresh(memory)

        return ShoppingMemoryResponse(
            id=memory.id,
            user_id=memory.user_id,
            memory_type=memory.memory_type,
            query=memory.query,
            product_id=memory.product_id,
            details=memory.details,
        )

    @classmethod
    async def get_memories(
        cls,
        db: AsyncSession,
        user_id: UUID,
        memory_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[ShoppingMemoryResponse]:
        """Fetch user shopping memory timeline."""
        stmt = select(ShoppingMemory).where(ShoppingMemory.user_id == user_id)
        if memory_type:
            stmt = stmt.where(ShoppingMemory.memory_type == memory_type)
        stmt = stmt.limit(limit)

        res = await db.execute(stmt)
        memories = res.scalars().all()

        return [
            ShoppingMemoryResponse(
                id=m.id,
                user_id=m.user_id,
                memory_type=m.memory_type,
                query=m.query,
                product_id=m.product_id,
                details=m.details,
            )
            for m in memories
        ]

    @classmethod
    async def clear_memories(
        cls,
        db: AsyncSession,
        user_id: UUID,
    ) -> bool:
        """Clear all shopping memory events for user."""
        stmt = delete(ShoppingMemory).where(ShoppingMemory.user_id == user_id)
        await db.execute(stmt)
        await db.commit()
        return True
