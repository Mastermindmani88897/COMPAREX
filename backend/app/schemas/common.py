"""
COMPAREX Backend – Common/Shared Pydantic Schemas

Reusable response envelope schemas used across all endpoints.
"""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Generic success envelope for all API responses."""

    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int = Field(ge=1)
    limit: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response envelope."""

    success: bool = True
    message: str = "Data retrieved successfully"
    data: list[T]
    meta: PaginationMeta


class ErrorDetail(BaseModel):
    """Structured error detail."""

    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response body."""

    success: bool = False
    message: str
    errors: Optional[list[ErrorDetail]] = None
    request_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str
    environment: str
