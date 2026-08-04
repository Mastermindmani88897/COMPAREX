"""
COMPAREX Backend - Comparison & Matching Engine Endpoints

Price history timeline and product duplicate detection.
The /compare endpoint lives in products.py to avoid route duplication.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.price_history_repository import PriceHistoryRepository
from app.repositories.product_listing_repository import ProductListingRepository
from app.services.matching_engine import ProductMatchingEngine

router = APIRouter()


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
