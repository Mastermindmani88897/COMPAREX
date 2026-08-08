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
    errors = []
    user_messages = []

    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        raw_msg = error["msg"]
        code = error["type"]

        clean_msg = raw_msg
        if "email" in field_path.lower():
            clean_msg = "Invalid email address."
        elif "password" in field_path.lower() and "too_short" in code:
            clean_msg = "Password must contain at least 8 characters."
        elif "confirm" in field_path.lower():
            clean_msg = "Passwords do not match."

        user_messages.append(clean_msg)
        errors.append(
            ErrorDetail(
                field=field_path,
                message=clean_msg,
                code=code,
            )
        )

    primary_message = user_messages[0] if user_messages else "Invalid input data."

    logger.warning(
        "Validation error | path=%s | primary=%s | errors=%d | request_id=%s",
        request.url.path,
        primary_message,
        len(errors),
        request_id,
    )
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            message=primary_message,
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
