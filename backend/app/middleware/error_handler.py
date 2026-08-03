"""
COMPAREX Backend – Global Error Handler Middleware

Converts unhandled exceptions and validation errors into
consistent JSON error responses using the ErrorResponse schema.
"""

import traceback
import uuid

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.schemas.common import ErrorDetail, ErrorResponse

logger = get_logger(__name__)


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Handle HTTP exceptions (404, 403, 401, etc.)."""
    request_id = str(uuid.uuid4())
    logger.warning(
        "HTTP %s: %s | path=%s | request_id=%s",
        exc.status_code,
        exc.detail,
        request.url.path,
        request_id,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=str(exc.detail),
            request_id=request_id,
        ).model_dump(),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle Pydantic validation errors (422 Unprocessable Entity)."""
    request_id = str(uuid.uuid4())
    errors = [
        ErrorDetail(
            field=" -> ".join(str(loc) for loc in error["loc"]),
            message=error["msg"],
            code=error["type"],
        )
        for error in exc.errors()
    ]
    logger.warning(
        "Validation error | path=%s | errors=%d | request_id=%s",
        request.url.path,
        len(errors),
        request_id,
    )
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            message="Request validation failed",
            errors=errors,
            request_id=request_id,
        ).model_dump(),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catch-all for unhandled server errors (500)."""
    request_id = str(uuid.uuid4())
    logger.error(
        "Unhandled exception | path=%s | request_id=%s\n%s",
        request.url.path,
        request_id,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="An unexpected error occurred. Please try again.",
            request_id=request_id,
        ).model_dump(),
    )
