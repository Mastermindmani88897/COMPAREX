"""
COMPAREX Backend – User Service

Handles user profile management, updates, and account deletion.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserPublic, UserUpdate

logger = get_logger(__name__)


class UserService:
    """Service handling User business operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_profile(self, user: User) -> UserPublic:
        """Get profile for current user."""
        return UserPublic.model_validate(user)

    async def update_profile(self, user: User, update_data: UserUpdate) -> UserPublic:
        """Update current user profile information."""
        fields_to_update = update_data.model_dump(exclude_unset=True)
        if not fields_to_update:
            return UserPublic.model_validate(user)

        if "username" in fields_to_update and fields_to_update["username"]:
            new_un = fields_to_update["username"].strip()
            existing = await self.user_repo.get_by_username(new_un)
            if existing and existing.id != user.id:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="That username is already taken. Please choose another.",
                )
            fields_to_update["username"] = new_un

        updated_user = await self.user_repo.update(user, fields_to_update)
        logger.info("Updated profile for user: %s", user.id)
        return UserPublic.model_validate(updated_user)

    async def delete_account(self, user: User) -> None:
        """Delete current user account."""
        await self.user_repo.delete(user)
        logger.info("Deleted user account: %s (%s)", user.id, user.email)
