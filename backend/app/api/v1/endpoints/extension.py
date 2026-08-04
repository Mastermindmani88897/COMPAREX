"""
COMPAREX Backend - Extension Gateway Endpoints

Handles product ingestion, quick comparison matrix queries, health checks,
and version compatibility validation for the Browser Extension Ecosystem.
"""

from typing import Any
from fastapi import APIRouter, Query

from app.adapters.registry import ConnectorRegistry
from app.core.config import settings
from app.schemas.common import SuccessResponse
from app.schemas.extension import (
    ExtensionCompareRequest,
    ExtensionProductPayload,
    ExtensionStatusResponse,
    ExtensionVersionCheck,
)
from app.services.aggregator_service import MarketplaceAggregatorService

router = APIRouter(prefix="/extension", tags=["Extension Gateway"])


@router.get(
    "/status",
    response_model=SuccessResponse[ExtensionStatusResponse],
    summary="Extension Gateway Status",
    description="Check connectivity, active connectors count, and min extension version.",
)
async def get_extension_status() -> Any:
    """Get extension connectivity and health status."""
    connectors = ConnectorRegistry.list_connectors(enabled_only=True)
    supported_slugs = [c.slug for c in connectors]

    status_data = ExtensionStatusResponse(
        status="online",
        environment=settings.ENVIRONMENT,
        api_version="1.0.0",
        min_supported_extension_version="1.0.0",
        active_connectors_count=len(connectors),
        supported_marketplaces=supported_slugs,
    )
    return SuccessResponse(
        message="Extension gateway status retrieved",
        data=status_data,
    )


@router.get(
    "/version",
    response_model=SuccessResponse[ExtensionVersionCheck],
    summary="Check Extension Version Compatibility",
    description="Validate extension client version against minimum required backend version.",
)
async def check_extension_version(
    v: str = Query("1.0.0", description="Current extension client version"),
) -> Any:
    """Validate client version compatibility."""
    version_data = ExtensionVersionCheck(
        client_version=v,
        latest_version="1.0.0",
        is_compatible=True,
        update_required=False,
        download_url=None,
    )
    return SuccessResponse(
        message="Extension version check completed",
        data=version_data,
    )


@router.post(
    "/product",
    summary="Ingest Extension Product & Compare",
    description="Accepts detected product info from content script and returns live marketplace comparison matrix.",
)
async def ingest_extension_product(payload: ExtensionProductPayload) -> Any:
    """Ingest extracted product details and aggregate comparison matrix across connectors."""
    agg_res = await MarketplaceAggregatorService.aggregate_search(
        query=payload.title,
        category=None,
        sort_by="price",
        use_cache=True,
    )

    # Compute comparison summary relative to detected price
    curr_price = payload.price
    listings = agg_res.get("listings", [])

    better_deals = [
        item for item in listings
        if float(item.get("price", 0.0)) < curr_price and item.get("is_available", True)
    ]
    lowest_overall = agg_res.get("lowest_price")

    has_savings = (lowest_overall is not None) and (curr_price > lowest_overall)
    savings_potential = round(curr_price - lowest_overall, 2) if has_savings else 0.0

    result = {
        "detected_product": {
            "title": payload.title,
            "current_price": payload.price,
            "currency": payload.currency,
            "url": payload.url,
            "image_url": payload.image_url,
            "seller_name": payload.seller_name,
            "rating": payload.rating,
            "marketplace_slug": payload.marketplace_slug,
        },
        "better_deals_count": len(better_deals),
        "savings_potential": savings_potential,
        "is_best_price_here": len(better_deals) == 0,
        "comparison_matrix": agg_res,
    }

    return SuccessResponse(
        message="Extension product processed successfully",
        data=result,
    )


@router.post(
    "/compare",
    summary="Quick Extension Comparison Search",
    description="Search and aggregate prices specifically tailored for extension overlay.",
)
async def extension_quick_compare(payload: ExtensionCompareRequest) -> Any:
    """Quick compare lookup for overlay widget."""
    agg_res = await MarketplaceAggregatorService.aggregate_search(
        query=payload.product_title,
        category=payload.category,
        sort_by="price",
        use_cache=True,
    )
    return SuccessResponse(
        message="Quick comparison completed",
        data=agg_res,
    )
