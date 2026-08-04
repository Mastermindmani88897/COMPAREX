"""
COMPAREX Backend – Shopping DNA Service

Generates and manages user Shopping Personas (Budget Shopper, Deal Hunter, Tech Enthusiast).
"""

import uuid
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shopping_dna import ShoppingDNA
from app.schemas.dna import ShoppingDNAResponse, ShoppingDNAUpdate


class ShoppingDNAService:
    """Shopping DNA persona engine service."""

    VALID_PERSONAS = [
        "Budget Shopper",
        "Premium Buyer",
        "Deal Hunter",
        "Tech Enthusiast",
        "Fashion Explorer",
        "Minimalist",
        "Mixed Shopper",
    ]

    @classmethod
    async def get_or_create_dna(
        cls,
        db: Optional[AsyncSession],
        user_id: UUID,
    ) -> ShoppingDNAResponse:
        """Fetch or create default Shopping DNA persona."""
        if db is None:
            return ShoppingDNAResponse(
                id=uuid.uuid4(),
                user_id=user_id,
                persona_name="Deal Hunter",
                traits=["High Discount Sensitivity", "Frequent Compare", "Coupon Seeker"],
                is_active=True,
            )

        stmt = select(ShoppingDNA).where(ShoppingDNA.user_id == user_id)
        res = await db.execute(stmt)
        dna = res.scalars().first()

        if not dna:
            dna = ShoppingDNA(
                user_id=user_id,
                persona_name="Deal Hunter",
                traits=[
                    "High Discount Sensitivity",
                    "Frequent Compare Operations",
                    "Coupon Seeker",
                ],
                is_active=True,
            )
            db.add(dna)
            await db.commit()
            await db.refresh(dna)

        return cls._map_response(dna)

    @classmethod
    async def update_dna(
        cls,
        db: AsyncSession,
        user_id: UUID,
        payload: ShoppingDNAUpdate,
    ) -> ShoppingDNAResponse:
        """Update or customize Shopping DNA persona."""
        stmt = select(ShoppingDNA).where(ShoppingDNA.user_id == user_id)
        res = await db.execute(stmt)
        dna = res.scalars().first()

        if not dna:
            dna = ShoppingDNA(user_id=user_id)
            db.add(dna)

        if payload.persona_name:
            dna.persona_name = payload.persona_name
        if payload.traits is not None:
            dna.traits = payload.traits
        if payload.is_active is not None:
            dna.is_active = payload.is_active

        await db.commit()
        await db.refresh(dna)
        return cls._map_response(dna)

    @classmethod
    def _map_response(cls, dna: ShoppingDNA) -> ShoppingDNAResponse:
        return ShoppingDNAResponse(
            id=dna.id,
            user_id=dna.user_id,
            persona_name=dna.persona_name,
            traits=dna.traits or [],
            is_active=dna.is_active,
        )
