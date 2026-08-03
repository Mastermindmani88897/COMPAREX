"""
COMPAREX Backend – Product Endpoints (Stubs)

Phase 2 will implement: search, list, get, compare, price history.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "/",
    status_code=501,
    summary="List Products (Phase 2)",
)
async def list_products() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"success": False, "message": "Not implemented — coming in Phase 2"},
    )


@router.get(
    "/search",
    status_code=501,
    summary="Search Products (Phase 2)",
)
async def search_products() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"success": False, "message": "Not implemented — coming in Phase 2"},
    )


@router.get(
    "/{product_id}",
    status_code=501,
    summary="Get Product (Phase 2)",
)
async def get_product(product_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"success": False, "message": "Not implemented — coming in Phase 2"},
    )


@router.post(
    "/compare",
    status_code=501,
    summary="Compare Products (Phase 2)",
)
async def compare_products() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"success": False, "message": "Not implemented — coming in Phase 2"},
    )
