"""
COMPAREX Backend – PriceHistory API Endpoints

Provides multi-store price history timeline analytics, volatility, and Gemini AI predictions.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.common import SuccessResponse
from app.services.price_history_service import PriceHistoryService

router = APIRouter(prefix="/price-history", tags=["Price History Intelligence"])


@router.get(
    "/product/{product_id}",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="Get Product Price History & Multi-Store Trend Analytics",
    description=(
        "Returns multi-store price history points, store toggles, volatility index, and prediction."
    ),
)
async def get_product_price_history(
    product_id: UUID,
    product_name: Optional[str] = Query(None, description="Product display title"),
    base_price: float = Query(49999.0, description="Base current price"),
    time_range: str = Query("30d", description="Time filter: 24h, 7d, 30d, 3m, 6m, 1y, all"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve historical price points and multi-store analytics."""
    res = await PriceHistoryService.get_price_history(
        db=db,
        product_id=product_id,
        product_name=product_name,
        base_price=base_price,
        time_range=time_range,
    )
    return SuccessResponse(message="Price history analytics generated", data=res)
