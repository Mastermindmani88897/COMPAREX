"""
COMPAREX Backend – Generic CRUD Repository Base

All domain-specific repositories inherit from this base to get
standard list/get/create/update/delete operations.
"""

from typing import Any, Generic, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic async CRUD repository.

    Usage:
        class UserRepository(BaseRepository[User]):
            def __init__(self, db: AsyncSession):
                super().__init__(User, db)
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession) -> None:
        self.model = model
        self.db = db

    async def get_by_id(self, record_id: UUID) -> Optional[ModelType]:
        """Fetch a single record by UUID primary key."""
        result = await self.db.execute(select(self.model).where(self.model.id == record_id))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Fetch a paginated list of all records."""
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, obj_in: dict[str, Any]) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        update_data: dict[str, Any],
    ) -> ModelType:
        """Update an existing record with provided fields."""
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: ModelType) -> None:
        """Hard-delete a record."""
        await self.db.delete(db_obj)
        await self.db.flush()

    async def count(self) -> int:
        """Count total records in the table."""
        from sqlalchemy import func, select

        result = await self.db.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()
