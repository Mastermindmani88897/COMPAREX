"""
COMPAREX Backend - Provider Status & Health Tracker Model

Provides structured status classification and health tracking for all external marketplace
API providers (SerpAPI, Rainforest, Bright Data, ZenRows).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class ProviderStatus(str, Enum):
    SUCCESS_WITH_RESULTS = "SUCCESS_WITH_RESULTS"
    SUCCESS_NO_RESULTS = "SUCCESS_NO_RESULTS"
    QUOTA_EXHAUSTED = "QUOTA_EXHAUSTED"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    PAYMENT_REQUIRED = "PAYMENT_REQUIRED"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    TIMEOUT = "TIMEOUT"
    PARSER_ERROR = "PARSER_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    NOT_CONFIGURED = "NOT_CONFIGURED"


@dataclass
class ProviderResponse:
    """Structured response from an external marketplace provider."""

    provider_name: str
    status: ProviderStatus
    http_status: Optional[int] = None
    error_message: Optional[str] = None
    results: List[Dict[str, Any]] = field(default_factory=list)
    raw_result_count: int = 0
    parsed_result_count: int = 0
    rejected_count: int = 0
    rejection_reasons: List[str] = field(default_factory=list)
    response_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "status": self.status.value,
            "http_status": self.http_status,
            "error_message": self.error_message,
            "results": self.results,
            "raw_result_count": self.raw_result_count,
            "parsed_result_count": self.parsed_result_count,
            "rejected_count": self.rejected_count,
            "rejection_reasons": self.rejection_reasons,
            "response_time_ms": self.response_time_ms,
        }


class ProviderHealthTracker:
    """Singleton diagnostic tracker for external marketplace API providers."""

    _health_data: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def record_call(
        cls,
        provider: str,
        configured: bool,
        status: ProviderStatus,
        http_status: Optional[int] = None,
        error_message: Optional[str] = None,
        result_count: int = 0,
        response_time_ms: float = 0.0,
    ) -> None:
        quota_state = "HEALTHY"
        if status in (ProviderStatus.QUOTA_EXHAUSTED, ProviderStatus.PAYMENT_REQUIRED):
            quota_state = "EXHAUSTED"
        elif status in (ProviderStatus.CONFIGURATION_ERROR, ProviderStatus.AUTHENTICATION_ERROR):
            quota_state = "CONFIGURATION_ERROR"
        elif status == ProviderStatus.RATE_LIMITED:
            quota_state = "RATE_LIMITED"
        elif not configured or status == ProviderStatus.NOT_CONFIGURED:
            quota_state = "NOT_CONFIGURED"

        cls._health_data[provider.lower()] = {
            "provider": provider,
            "configured": configured,
            "status": status.value,
            "last_checked": datetime.now(timezone.utc).isoformat(),
            "last_http_status": http_status,
            "last_error": error_message,
            "last_result_count": result_count,
            "quota_state": quota_state,
            "response_time_ms": round(response_time_ms, 2),
        }

    @classmethod
    def get_health_status(cls) -> List[Dict[str, Any]]:
        """Return diagnostic health status for all registered providers (secrets never exposed)."""
        from app.core.config import settings

        bd_has_zone = bool(getattr(settings, "BRIGHTDATA_ZONE", None))
        bd_configured = bool(settings.BRIGHTDATA_API_KEY and bd_has_zone)
        providers = [
            ("SerpAPI", bool(settings.SERPAPI_API_KEY)),
            ("Rainforest", bool(settings.RAINFOREST_API_KEY)),
            ("Bright Data", bd_configured),
            ("ZenRows", bool(settings.ZENROWS_API_KEY)),
        ]

        result = []
        for p_name, is_cfg in providers:
            p_key = p_name.lower().replace(" ", "")
            stored_key = "bright data" if p_key == "brightdata" else p_key
            if stored_key in cls._health_data:
                entry = dict(cls._health_data[stored_key])
                entry["configured"] = is_cfg
                result.append(entry)
            else:
                err_msg = "No requests logged yet" if is_cfg else "API credentials not configured"
                result.append(
                    {
                        "provider": p_name,
                        "configured": is_cfg,
                        "status": ProviderStatus.NOT_CONFIGURED.value if not is_cfg else "UNKNOWN",
                        "last_checked": None,
                        "last_http_status": None,
                        "last_error": err_msg,
                        "last_result_count": 0,
                        "quota_state": "NOT_CONFIGURED" if not is_cfg else "HEALTHY",
                        "response_time_ms": 0.0,
                    }
                )
        return result

    @classmethod
    def get_provider_status_map(cls) -> Dict[str, Dict[str, Any]]:
        """Return provider status map keyed by provider slug (secrets never exposed)."""
        list_status = cls.get_health_status()
        status_map = {}
        for item in list_status:
            p_name = item["provider"].lower().replace(" ", "")
            raw_st = item.get("status", "UNKNOWN")
            # Map raw status enum string to concise user-friendly summary status
            if raw_st in ("SUCCESS_WITH_RESULTS", "SUCCESS_NO_RESULTS", "HEALTHY", "UNKNOWN"):
                summary_status = "AVAILABLE" if item.get("configured") else "NOT_CONFIGURED"
            else:
                summary_status = raw_st

            status_map[p_name] = {
                "provider": item["provider"],
                "status": summary_status,
                "raw_status": raw_st,
                "configured": item.get("configured", False),
                "quota_state": item.get("quota_state", "UNKNOWN"),
                "last_checked": item.get("last_checked"),
                "last_error": item.get("last_error"),
            }
        return status_map
