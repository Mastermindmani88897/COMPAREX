"""
COMPAREX Backend – Product Management API Endpoints
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.product import ProductCreate, ProductPublic, ProductUpdate
from app.schemas.product_listing import PriceCompareResult
from app.services.product_listing_service import ProductListingService
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "",
    response_model=SuccessResponse[list[ProductPublic]],
    summary="List Products",
    description="Retrieve all indexed products with optional search query filter.",
)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    query: Optional[str] = Query(None, description="Search term for product name"),
    db: AsyncSession = Depends(get_db),
):
    """List products endpoint."""
    service = ProductService(db)
    products = await service.list_products(skip=skip, limit=limit, query=query)
    return SuccessResponse(
        message="Products retrieved successfully",
        data=products,
    )


@router.post(
    "",
    response_model=SuccessResponse[ProductPublic],
    status_code=status.HTTP_201_CREATED,
    summary="Create Product",
    description="Create a new product in the index.",
)
async def create_product(
    req: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create product endpoint."""
    service = ProductService(db)
    product = await service.create_product(req)
    return SuccessResponse(
        message="Product created successfully",
        data=product,
    )


@router.get(
    "/{product_id}",
    response_model=SuccessResponse[ProductPublic],
    summary="Get Product Details",
    description="Retrieve details of a single product by UUID.",
)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get product by ID endpoint."""
    service = ProductService(db)
    product = await service.get_product_by_id(product_id)
    return SuccessResponse(
        message="Product details retrieved",
        data=product,
    )


@router.get(
    "/{product_id}/compare",
    response_model=SuccessResponse[PriceCompareResult],
    summary="Compare Product Prices",
    description=(
        "Retrieve all marketplace price listings for a product, "
        "along with computed stats: lowest price, highest price, "
        "average, and best deal listing."
    ),
)
async def compare_product_prices(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Price comparison endpoint — returns all listings sorted by price."""
    service = ProductListingService(db)
    result = await service.get_compare_result(product_id)
    return SuccessResponse(
        message="Price comparison data retrieved",
        data=result,
    )


@router.put(
    "/{product_id}",
    response_model=SuccessResponse[ProductPublic],
    summary="Update Product",
    description="Update an existing product by UUID.",
)
async def update_product(
    product_id: UUID,
    req: ProductUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update product endpoint."""
    service = ProductService(db)
    updated = await service.update_product(product_id, req)
    return SuccessResponse(
        message="Product updated successfully",
        data=updated,
    )


@router.delete(
    "/{product_id}",
    response_model=SuccessResponse[None],
    summary="Delete Product",
    description="Delete a product by UUID.",
)
async def delete_product(
    product_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete product endpoint."""
    service = ProductService(db)
    await service.delete_product(product_id)
    return SuccessResponse(
        message="Product deleted successfully",
        data=None,
    )
