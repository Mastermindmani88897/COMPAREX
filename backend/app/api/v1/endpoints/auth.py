"""
COMPAREX Backend – Auth Endpoints (Stubs)

Phase 2 will implement: register, login, logout, token refresh, email verification.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    status_code=501,
    summary="Register (Phase 2)",
    description="User registration — implemented in Phase 2.",
)
async def register() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"success": False, "message": "Not implemented — coming in Phase 2"},
    )


@router.post(
    "/login",
    status_code=501,
    summary="Login (Phase 2)",
    description="User login — implemented in Phase 2.",
)
async def login() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"success": False, "message": "Not implemented — coming in Phase 2"},
    )


@router.post(
    "/logout",
    status_code=501,
    summary="Logout (Phase 2)",
)
async def logout() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"success": False, "message": "Not implemented — coming in Phase 2"},
    )


@router.post(
    "/refresh",
    status_code=501,
    summary="Refresh Token (Phase 2)",
)
async def refresh_token() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"success": False, "message": "Not implemented — coming in Phase 2"},
    )
