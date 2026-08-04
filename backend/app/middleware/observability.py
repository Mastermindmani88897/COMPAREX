"""
COMPAREX Backend – Observability Middleware

Request IDs, Latency Tracking, and Prometheus Metrics Collection.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SystemMetricsCollector:
    """Prometheus & Observability Metrics Store."""

    TOTAL_REQUESTS = 0
    SUCCESS_REQUESTS = 0
    FAILED_REQUESTS = 0
    TOTAL_LATENCY_MS = 0.0

    @classmethod
    def record_request(cls, latency_ms: float, status_code: int) -> None:
        """Record request metrics."""
        cls.TOTAL_REQUESTS += 1
        cls.TOTAL_LATENCY_MS += latency_ms
        if status_code < 400:
            cls.SUCCESS_REQUESTS += 1
        else:
            cls.FAILED_REQUESTS += 1


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Observability Tracing & Latency Middleware."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track request latency and inject X-Request-ID."""
        start_time = time.time()
        request_id = str(uuid.uuid4())

        response = await call_next(request)

        latency_ms = (time.time() - start_time) * 1000.0
        SystemMetricsCollector.record_request(latency_ms, response.status_code)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-MS"] = f"{latency_ms:.2f}"

        return response
