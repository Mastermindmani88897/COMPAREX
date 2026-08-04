"""
COMPAREX Backend – Smart Privacy Service

Provides full user data control, export, import, and AI memory/profile deletion.
"""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.memory_service import ShoppingMemoryService
from app.services.profile_service import ShoppingProfileService


class SmartPrivacyService:
    """Smart Privacy Center management service."""

    @classmethod
    async def export_all_user_data(
        cls,
        db: AsyncSession,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """Export all user shopping profile, memory, and analytics data."""
        profile_data = await ShoppingProfileService.export_profile(db, user_id)
        memories = await ShoppingMemoryService.get_memories(db, user_id)

        return {
            "user_id": str(user_id),
            "profile": profile_data,
            "memories": [m.model_dump() for m in memories],
            "privacy_status": (
                "OPT_IN_LEARNING_ACTIVE" if profile_data.get("consent_opt_in") else "OPT_OUT"
            ),
        }

    @classmethod
    async def purge_all_ai_data(
        cls,
        db: AsyncSession,
        user_id: UUID,
    ) -> Dict[str, str]:
        """Purge all user AI memories, profiles, and learned context."""
        await ShoppingMemoryService.clear_memories(db, user_id)
        await ShoppingProfileService.reset_profile(db, user_id)

        return {
            "status": "PURGED",
            "message": "All user AI memories, profile preferences, and DNA traits purged.",
        }
