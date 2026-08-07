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
    "/autocomplete",
    summary="Search Autocomplete Suggestions",
    description="Returns instant search suggestions, brand matches, and categories for search bar.",
)
async def autocomplete_products(
    q: str = Query(..., min_length=1, description="Search term prefix"),
    limit: int = Query(8, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Autocomplete endpoint."""
    service = ProductService(db)
    suggestions = await service.autocomplete_suggestions(query=q, limit=limit)
    return SuccessResponse(
        message="Autocomplete suggestions retrieved",
        data=suggestions,
    )


@router.get(
    "",
    response_model=SuccessResponse[list[ProductPublic]],
    summary="List Products",
    description="Retrieve all indexed products with search query, category, brand, rating, stock status, and price range filters.",
)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    query: Optional[str] = Query(None, description="Search term for product name"),
    category: Optional[str] = Query(None, description="Category filter"),
    brand: Optional[str] = Query(None, description="Brand filter"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating filter"),
    in_stock_only: Optional[bool] = Query(None, description="Filter in-stock products only"),
    sort_by: Optional[str] = Query(None, description="Sort order: popularity, price_low, price_high, rating, discount"),
    db: AsyncSession = Depends(get_db),
):
    """List products endpoint."""
    service = ProductService(db)
    products = await service.list_products(
        skip=skip,
        limit=limit,
        query=query,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        in_stock_only=in_stock_only,
        sort_by=sort_by,
    )
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
