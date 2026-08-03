"""
COMPAREX Backend – User Endpoints (Stubs)

Phase 2 will implement: get profile, update profile, delete account, etc.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    status_code=501,
    summary="Get Current User (Phase 2)",
)
async def get_current_user() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"success": False, "message": "Not implemented — coming in Phase 2"},
    )


@router.patch(
    "/me",
    status_code=501,
    summary="Update Profile (Phase 2)",
)
async def update_profile() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"success": False, "message": "Not implemented — coming in Phase 2"},
    )


@router.delete(
    "/me",
    status_code=501,
    summary="Delete Account (Phase 2)",
)
async def delete_account() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"success": False, "message": "Not implemented — coming in Phase 2"},
    )
