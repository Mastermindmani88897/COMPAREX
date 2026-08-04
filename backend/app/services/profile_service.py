"""
COMPAREX Backend – Shopping Profile Service

Opt-in learning consent, profile CRUD, export, import, and reset features.
"""

import uuid
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shopping_profile import ShoppingProfile
from app.schemas.profile import ShoppingProfileCreate, ShoppingProfileResponse


class ShoppingProfileService:
    """Shopping Profile management service."""

    @classmethod
    async def get_or_create_profile(
        cls,
        db: Optional[AsyncSession],
        user_id: UUID,
    ) -> ShoppingProfileResponse:
        """Fetch or create default shopping profile."""
        if db is None:
            return ShoppingProfileResponse(
                id=uuid.uuid4(),
                user_id=user_id,
                consent_opt_in=True,
                preferred_brands=["Apple", "Samsung", "Sony"],
                preferred_marketplaces=["Amazon India", "Flipkart", "Croma"],
                preferred_categories=["electronics"],
                min_budget=0.0,
                max_budget=500000.0,
                delivery_speed="EXPRESS",
                seller_preference="VERIFIED_ONLY",
                discount_sensitivity="HIGH",
            )

        stmt = select(ShoppingProfile).where(ShoppingProfile.user_id == user_id)
        res = await db.execute(stmt)
        profile = res.scalars().first()

        if not profile:
            profile = ShoppingProfile(
                user_id=user_id,
                consent_opt_in=False,
                preferred_brands=["Apple", "Samsung", "Sony"],
                preferred_marketplaces=["Amazon India", "Flipkart", "Croma"],
                preferred_categories=["electronics"],
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)

        return cls._map_response(profile)

    @classmethod
    async def update_profile(
        cls,
        db: AsyncSession,
        user_id: UUID,
        payload: ShoppingProfileCreate,
    ) -> ShoppingProfileResponse:
        """Update shopping profile settings."""
        stmt = select(ShoppingProfile).where(ShoppingProfile.user_id == user_id)
        res = await db.execute(stmt)
        profile = res.scalars().first()

        if not profile:
            profile = ShoppingProfile(user_id=user_id)
            db.add(profile)

        profile.consent_opt_in = payload.consent_opt_in
        profile.preferred_brands = payload.preferred_brands
        profile.preferred_marketplaces = payload.preferred_marketplaces
        profile.preferred_categories = payload.preferred_categories
        profile.min_budget = Decimal(str(payload.min_budget))
        profile.max_budget = Decimal(str(payload.max_budget))
        profile.delivery_speed = payload.delivery_speed
        profile.seller_preference = payload.seller_preference
        profile.discount_sensitivity = payload.discount_sensitivity

        await db.commit()
        await db.refresh(profile)
        return cls._map_response(profile)

    @classmethod
    async def reset_profile(
        cls,
        db: AsyncSession,
        user_id: UUID,
    ) -> ShoppingProfileResponse:
        """Reset profile to default non-personalized state."""
        stmt = select(ShoppingProfile).where(ShoppingProfile.user_id == user_id)
        res = await db.execute(stmt)
        profile = res.scalars().first()

        if profile:
            profile.consent_opt_in = False
            profile.preferred_brands = []
            profile.preferred_marketplaces = []
            profile.preferred_categories = []
            profile.min_budget = Decimal("0.00")
            profile.max_budget = Decimal("500000.00")
            await db.commit()
            await db.refresh(profile)
        else:
            return await cls.get_or_create_profile(db, user_id)

        return cls._map_response(profile)

    @classmethod
    async def export_profile(
        cls,
        db: AsyncSession,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """Export shopping profile JSON payload."""
        p = await cls.get_or_create_profile(db, user_id)
        return p.model_dump()

    @classmethod
    def _map_response(cls, profile: ShoppingProfile) -> ShoppingProfileResponse:
        return ShoppingProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            consent_opt_in=profile.consent_opt_in,
            preferred_brands=profile.preferred_brands or [],
            preferred_marketplaces=profile.preferred_marketplaces or [],
            preferred_categories=profile.preferred_categories or [],
            min_budget=float(profile.min_budget),
            max_budget=float(profile.max_budget),
            delivery_speed=profile.delivery_speed,
            seller_preference=profile.seller_preference,
            discount_sensitivity=profile.discount_sensitivity,
        )
