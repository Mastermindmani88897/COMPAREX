"""
COMPAREX Backend – Observability Metrics API Endpoint

Exposes Prometheus system metrics, request counters, and response latency statistics.
"""

from typing import Dict

from fastapi import APIRouter

from app.middleware.observability import SystemMetricsCollector
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/metrics", tags=["System Observability & Metrics"])


@router.get(
    "",
    response_model=SuccessResponse[Dict[str, float]],
    summary="Get System Observability Metrics",
    description="Exposes Prometheus request counters, success/failure rate, and response latency.",
)
async def get_metrics():
    """Retrieve observability metrics."""
    avg_latency = (
        SystemMetricsCollector.TOTAL_LATENCY_MS / SystemMetricsCollector.TOTAL_REQUESTS
        if SystemMetricsCollector.TOTAL_REQUESTS > 0
        else 0.0
    )

    metrics = {
        "total_requests": float(SystemMetricsCollector.TOTAL_REQUESTS),
        "success_requests": float(SystemMetricsCollector.SUCCESS_REQUESTS),
        "failed_requests": float(SystemMetricsCollector.FAILED_REQUESTS),
        "avg_latency_ms": round(avg_latency, 2),
        "system_health_score": 1.0 if SystemMetricsCollector.FAILED_REQUESTS == 0 else 0.95,
    }
    return SuccessResponse(message="System metrics retrieved successfully", data=metrics)
