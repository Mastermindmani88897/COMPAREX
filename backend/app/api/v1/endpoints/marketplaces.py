"""
COMPAREX Backend – Marketplace Endpoints (Stubs)

Phase 2 will implement: list marketplaces, get marketplace details.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/marketplaces", tags=["Marketplaces"])


@router.get(
    "/",
    status_code=501,
    summary="List Marketplaces (Phase 2)",
)
async def list_marketplaces() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"success": False, "message": "Not implemented — coming in Phase 2"},
    )


@router.get(
    "/{marketplace_id}",
    status_code=501,
    summary="Get Marketplace (Phase 2)",
)
async def get_marketplace(marketplace_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"success": False, "message": "Not implemented — coming in Phase 2"},
    )
