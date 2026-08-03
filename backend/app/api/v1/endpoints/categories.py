"""
COMPAREX Backend – Category Management API Endpoints
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryPublic, CategoryUpdate
from app.schemas.common import SuccessResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "",
    response_model=SuccessResponse[list[CategoryPublic]],
    summary="List Categories",
    description="Retrieve all product categories with optional pagination.",
)
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List categories endpoint."""
    service = CategoryService(db)
    categories = await service.list_categories(skip=skip, limit=limit)
    return SuccessResponse(
        message="Categories retrieved successfully",
        data=categories,
    )


@router.post(
    "",
    response_model=SuccessResponse[CategoryPublic],
    status_code=status.HTTP_201_CREATED,
    summary="Create Category",
    description="Create a new product category.",
)
async def create_category(
    req: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create category endpoint."""
    service = CategoryService(db)
    category = await service.create_category(req)
    return SuccessResponse(
        message="Category created successfully",
        data=category,
    )


@router.get(
    "/{category_id}",
    response_model=SuccessResponse[CategoryPublic],
    summary="Get Category Details",
    description="Retrieve details of a single category by UUID.",
)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get category by ID endpoint."""
    service = CategoryService(db)
    category = await service.get_category_by_id(category_id)
    return SuccessResponse(
        message="Category details retrieved",
        data=category,
    )


@router.put(
    "/{category_id}",
    response_model=SuccessResponse[CategoryPublic],
    summary="Update Category",
    description="Update an existing category by UUID.",
)
async def update_category(
    category_id: UUID,
    req: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update category endpoint."""
    service = CategoryService(db)
    updated = await service.update_category(category_id, req)
    return SuccessResponse(
        message="Category updated successfully",
        data=updated,
    )


@router.delete(
    "/{category_id}",
    response_model=SuccessResponse[None],
    summary="Delete Category",
    description="Delete a category by UUID.",
)
async def delete_category(
    category_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete category endpoint."""
    service = CategoryService(db)
    await service.delete_category(category_id)
    return SuccessResponse(
        message="Category deleted successfully",
        data=None,
    )
