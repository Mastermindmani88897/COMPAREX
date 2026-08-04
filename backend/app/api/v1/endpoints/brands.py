"""
COMPAREX Backend - Brand Management API Endpoints

Provides CRUD operations for product brands.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.repositories.brand_repository import BrandRepository
from app.schemas.brand import BrandCreate, BrandPublic, BrandUpdate
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/brands", tags=["Brands"])


@router.get(
    "",
    response_model=SuccessResponse[list[BrandPublic]],
    summary="List Brands",
    description="Retrieve all registered product brands.",
)
async def list_brands(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List all brands endpoint."""
    repo = BrandRepository(db)
    brands = await repo.get_all(skip=skip, limit=limit)
    return SuccessResponse(
        message="Brands retrieved successfully",
        data=[BrandPublic.model_validate(b) for b in brands],
    )


@router.post(
    "",
    response_model=SuccessResponse[BrandPublic],
    status_code=status.HTTP_201_CREATED,
    summary="Create Brand",
    description="Create a new product brand.",
)
async def create_brand(
    req: BrandCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create brand endpoint."""
    repo = BrandRepository(db)
    existing = await repo.get_by_slug(req.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Brand with slug '{req.slug}' already exists",
        )
    brand = await repo.create(req.model_dump())
    return SuccessResponse(
        message="Brand created successfully",
        data=BrandPublic.model_validate(brand),
    )


@router.get(
    "/{brand_id}",
    response_model=SuccessResponse[BrandPublic],
    summary="Get Brand Details",
    description="Retrieve a single brand by UUID.",
)
async def get_brand(
    brand_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get brand by ID endpoint."""
    repo = BrandRepository(db)
    brand = await repo.get_by_id(brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )
    return SuccessResponse(
        message="Brand details retrieved",
        data=BrandPublic.model_validate(brand),
    )


@router.put(
    "/{brand_id}",
    response_model=SuccessResponse[BrandPublic],
    summary="Update Brand",
    description="Update an existing brand by UUID.",
)
async def update_brand(
    brand_id: UUID,
    req: BrandUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update brand endpoint."""
    repo = BrandRepository(db)
    brand = await repo.get_by_id(brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )
    update_data = req.model_dump(exclude_unset=True)
    if "slug" in update_data and update_data["slug"] != brand.slug:
        conflict = await repo.get_by_slug(update_data["slug"])
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Brand with slug '{update_data['slug']}' already exists",
            )
    updated = await repo.update(brand, update_data)
    return SuccessResponse(
        message="Brand updated successfully",
        data=BrandPublic.model_validate(updated),
    )


@router.delete(
    "/{brand_id}",
    response_model=SuccessResponse[None],
    summary="Delete Brand",
    description="Delete a brand by UUID.",
)
async def delete_brand(
    brand_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete brand endpoint."""
    repo = BrandRepository(db)
    brand = await repo.get_by_id(brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )
    await repo.delete(brand)
    return SuccessResponse(
        message="Brand deleted successfully",
        data=None,
    )
