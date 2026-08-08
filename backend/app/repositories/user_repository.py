"""
COMPAREX Backend – User Repository
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User data access operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email address."""
        result = await self.db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Check if an email is already registered."""
        user = await self.get_by_email(email)
        return user is not None

    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Fetch a user by Google OAuth ID."""
        result = await self.db.execute(select(User).where(User.google_id == google_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Fetch a user by case-insensitive username."""
        if not username or not username.strip():
            return None
        from sqlalchemy import func
        clean = username.strip().lower()
        stmt = select(User).where(func.lower(User.username) == clean)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def username_exists(self, username: str) -> bool:
        """Check if a username is already taken (case-insensitive)."""
        user = await self.get_by_username(username)
        return user is not None
