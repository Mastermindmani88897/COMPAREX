"""
COMPAREX Backend – Marketplace Service
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.marketplace_repository import MarketplaceRepository
from app.schemas.marketplace import (
    MarketplaceCreate,
    MarketplacePublic,
    MarketplaceUpdate,
)

logger = get_logger(__name__)


class MarketplaceService:
    """Service handling Marketplace operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = MarketplaceRepository(db)

    async def list_marketplaces(self, skip: int = 0, limit: int = 100) -> list[MarketplacePublic]:
        """List all marketplaces."""
        marketplaces = await self.repo.get_all(skip=skip, limit=limit)
        return [MarketplacePublic.model_validate(m) for m in marketplaces]

    async def get_marketplace_by_id(self, marketplace_id: UUID) -> MarketplacePublic:
        """Get marketplace by ID."""
        marketplace = await self.repo.get_by_id(marketplace_id)
        if not marketplace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Marketplace not found",
            )
        return MarketplacePublic.model_validate(marketplace)

    async def create_marketplace(self, req: MarketplaceCreate) -> MarketplacePublic:
        """Create a new marketplace entry."""
        if await self.repo.get_by_slug(req.slug):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Marketplace slug '{req.slug}' already exists",
            )

        marketplace = await self.repo.create(req.model_dump())
        logger.info("Marketplace created: %s (%s)", marketplace.name, marketplace.id)
        return MarketplacePublic.model_validate(marketplace)

    async def update_marketplace(
        self, marketplace_id: UUID, req: MarketplaceUpdate
    ) -> MarketplacePublic:
        """Update an existing marketplace."""
        marketplace = await self.repo.get_by_id(marketplace_id)
        if not marketplace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Marketplace not found",
            )

        update_data = req.model_dump(exclude_unset=True)
        if "slug" in update_data and update_data["slug"] != marketplace.slug:
            if await self.repo.get_by_slug(update_data["slug"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Marketplace slug '{update_data['slug']}' already exists",
                )

        updated = await self.repo.update(marketplace, update_data)
        return MarketplacePublic.model_validate(updated)

    async def delete_marketplace(self, marketplace_id: UUID) -> None:
        """Delete a marketplace."""
        marketplace = await self.repo.get_by_id(marketplace_id)
        if not marketplace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Marketplace not found",
            )
        await self.repo.delete(marketplace)
        logger.info("Marketplace deleted: %s", marketplace_id)
