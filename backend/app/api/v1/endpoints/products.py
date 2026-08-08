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
    "/recently-viewed",
    response_model=SuccessResponse[list[ProductPublic]],
    summary="Get Recently Viewed Products",
    description="Retrieve top 20 recently viewed products for the current user.",
)
async def get_recently_viewed(
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Recently viewed products endpoint."""
    service = ProductService(db)
    products = await service.get_recently_viewed(user_id=current_user.id, limit=limit)
    return SuccessResponse(
        message="Recently viewed products retrieved",
        data=products,
    )


@router.get(
    "/trending",
    response_model=SuccessResponse[list[ProductPublic]],
    summary="Get Dynamic Trending Products",
    description="Retrieve top trending products from the database.",
)
async def get_trending_products(
    limit: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
):
    """Trending products endpoint."""
    service = ProductService(db)
    products = await service.get_trending_products(limit=limit)
    return SuccessResponse(
        message="Trending products retrieved",
        data=products,
    )


@router.get(
    "",
    response_model=SuccessResponse[list[ProductPublic]],
    summary="List Products",
    description=(
        "Retrieve all indexed products with search query, category, brand, rating, stock status, "
        "and price range filters."
    ),
)
async def list_products(
    skip: int = Query(0, ge=0),
    page: Optional[int] = Query(None, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(24, ge=1, le=100),
    query: Optional[str] = Query(None, description="Search term for product name"),
    category: Optional[str] = Query(None, description="Category filter"),
    brand: Optional[str] = Query(None, description="Brand filter"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating filter"),
    in_stock_only: Optional[bool] = Query(None, description="Filter in-stock products only"),
    sort_by: Optional[str] = Query(
        None, description="Sort order: popularity, price_low, price_high, rating, discount"
    ),
    db: AsyncSession = Depends(get_db),
):
    from app.core.logging import get_logger
    endpoint_logger = get_logger(__name__)

    if page is not None:
        skip = (page - 1) * limit
    else:
        page = (skip // limit) + 1

    endpoint_logger.info(
        "SEARCH REQUEST: query='%s', category='%s', brand='%s', min_price=%s, "
        "max_price=%s, page=%d, skip=%d, limit=%d",
        query,
        category,
        brand,
        min_price,
        max_price,
        page,
        skip,
        limit,
    )
    try:
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
        has_next = len(products) == limit
        return SuccessResponse(
            message="Products retrieved successfully",
            data=products,
            pagination={
                "page": page,
                "limit": limit,
                "total": len(products),
                "has_next": has_next,
                "has_previous": page > 1,
            },
        )
    except Exception as exc:
        endpoint_logger.error(
            "Unhandled exception in list_products endpoint: %s", exc, exc_info=True
        )
        return SuccessResponse(
            message="Products retrieved with fallback",
            data=[],
            pagination={
                "page": page,
                "limit": limit,
                "total": 0,
                "has_next": False,
                "has_previous": page > 1,
            },
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


@router.post(
    "/{product_id}/view",
    response_model=SuccessResponse[None],
    summary="Record Product View",
    description="Record user product view for recently viewed tracking.",
)
async def record_product_view(
    product_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Record product view endpoint."""
    service = ProductService(db)
    await service.record_product_view(user_id=current_user.id, product_id=product_id)
    return SuccessResponse(
        message="Product view recorded",
        data=None,
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
