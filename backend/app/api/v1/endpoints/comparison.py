"""
COMPAREX Backend - Comparison & Matching Engine Endpoints
"""

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.price_history_repository import PriceHistoryRepository
from app.repositories.product_listing_repository import ProductListingRepository
from app.schemas.common import SuccessResponse
from app.services.aggregator_service import MarketplaceAggregatorService
from app.services.matching_engine import ProductMatchingEngine

router = APIRouter()


@router.get(
    "/comparison/aggregate",
    summary="Multi-Marketplace Price Aggregator",
    description="Aggregates live and mock connector prices across all relevant connectors.",
)
async def aggregate_marketplace_prices(
    q: str = Query(..., description="Search keyword, title, or EAN"),
    category: Optional[str] = Query(
        None, description="Category filter (e.g. electronics, fashion, beauty)"
    ),
    sort_by: str = Query(
        "price", description="Sort order: price, price_desc, rating, discount, deal_score"
    ),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    in_stock_only: bool = Query(False, description="Filter only in-stock listings"),
    use_cache: bool = Query(True, description="Enable Redis caching"),
) -> Any:
    """Aggregate search across all connector capabilities."""
    result = await MarketplaceAggregatorService.aggregate_search(
        query=q,
        category=category,
        sort_by=sort_by,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
        use_cache=use_cache,
    )
    return SuccessResponse(
        message="Marketplace prices aggregated successfully",
        data=result,
    )


@router.get(
    "/products/{product_id}/history",
    summary="Get price history for product listings",
    description="Returns time-series price history for all marketplace listings of a product.",
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
                "timestamp": r.created_at.isoformat(),
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
    """Compare two product payloads to determine if they are duplicates."""
    p1 = payload.get("product_1", {})
    p2 = payload.get("product_2", {})
    threshold = float(payload.get("threshold", 0.75))

    res = ProductMatchingEngine.evaluate_duplicate_candidate(p1, p2, threshold=threshold)
    return res
