"""
COMPAREX Backend – PriceHistory API Endpoints

Provides price history timeline analytics, volatility scores, and price predictions.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.common import SuccessResponse
from app.schemas.price_history import PriceHistoryAnalyticsResponse
from app.services.price_history_service import PriceHistoryService

router = APIRouter(prefix="/price-history", tags=["Price History Intelligence"])


@router.get(
    "/product/{product_id}",
    response_model=SuccessResponse[PriceHistoryAnalyticsResponse],
    summary="Get Product Price History & Trend Analytics",
    description="Returns price history timeline, trend analysis, volatility index, and prediction.",
)
async def get_product_price_history(
    product_id: UUID,
    product_name: Optional[str] = Query(None, description="Product display title"),
    base_price: float = Query(49999.0, description="Base current price"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve historical price points and analytics."""
    res = await PriceHistoryService.get_price_history(
        db=db,
        product_id=product_id,
        product_name=product_name,
        base_price=base_price,
    )
    return SuccessResponse(message="Price history analytics generated", data=res)
