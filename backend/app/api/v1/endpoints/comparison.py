"""
COMPAREX Backend – Comparison & Matching Engine Endpoints
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.price_history_repository import PriceHistoryRepository
from app.repositories.product_listing_repository import ProductListingRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product_listing import PriceCompareResult
from app.services.comparison_engine import ComparisonEngineService
from app.services.matching_engine import ProductMatchingEngine

router = APIRouter()


@router.get(
    "/products/{product_id}/compare",
    response_model=PriceCompareResult,
    summary="Compare product prices across all marketplaces",
    description="Calculates lowest price, highest price, price spread, and deal scores.",
)
async def compare_product_prices(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Fetch complete comparison matrix for a specific canonical product."""
    product_repo = ProductRepository(db)
    product = await product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found.",
        )

    listing_repo = ProductListingRepository(db)
    listings = await listing_repo.get_by_product_id(product_id)

    raw_listings = []
    for lst in listings:
        m = lst.marketplace
        raw_listings.append(
            {
                "id": str(lst.id),
                "product_id": str(lst.product_id),
                "marketplace_id": str(lst.marketplace_id),
                "price": float(lst.price),
                "original_price": float(lst.original_price) if lst.original_price else None,
                "discount_percent": (
                    float(lst.discount_percent) if lst.discount_percent else None
                ),
                "currency": lst.currency,
                "listing_url": lst.listing_url,
                "marketplace_product_id": lst.marketplace_product_id,
                "seller_name": lst.seller_name,
                "is_available": lst.is_available,
                "is_prime": lst.is_prime,
                "stock_status": lst.stock_status,
                "delivery_estimate": lst.delivery_estimate,
                "rating": float(lst.rating) if lst.rating else None,
                "review_count": lst.review_count,
                "marketplace": (
                    {
                        "id": str(m.id),
                        "name": m.name,
                        "slug": m.slug,
                        "logo_url": m.logo_url,
                        "base_url": m.base_url,
                    }
                    if m
                    else None
                ),
                "created_at": lst.created_at,
                "updated_at": lst.updated_at,
            }
        )

    matrix = ComparisonEngineService.calculate_comparison_matrix(
        product_id=str(product.id),
        product_name=product.name,
        listings=raw_listings,
    )
    return matrix


@router.get(
    "/products/{product_id}/history",
    summary="Get price history points for product listings",
)
async def get_product_price_history(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Fetch timeline price history for all listings of a product."""
    listing_repo = ProductListingRepository(db)
    history_repo = PriceHistoryRepository(db)

    listings = await listing_repo.get_by_product_id(product_id)
    history_data = []

    for lst in listings:
        records = await history_repo.get_by_listing_id(lst.id)
        pts = [
            {
                "id": str(r.id),
                "price": float(r.price),
                "currency": r.currency,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in records
        ]
        history_data.append(
            {
                "listing_id": str(lst.id),
                "marketplace_name": lst.marketplace.name if lst.marketplace else "Store",
                "current_price": float(lst.price),
                "history": pts,
            }
        )

    return {
        "product_id": str(product_id),
        "listings_history": history_data,
    }


@router.post(
    "/products/match",
    summary="Algorithmic product matching & duplicate evaluation",
    description="Evaluates title similarity, brand match, and specs without external AI.",
)
async def evaluate_product_match(
    payload: dict[str, Any],
) -> Any:
    """Compare two product payloads to determine if they match."""
    p1 = payload.get("product_1", {})
    p2 = payload.get("product_2", {})
    threshold = float(payload.get("threshold", 0.75))

    res = ProductMatchingEngine.evaluate_duplicate_candidate(p1, p2, threshold=threshold)
    return res
