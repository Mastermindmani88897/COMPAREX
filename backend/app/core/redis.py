"""
COMPAREX Backend – Upstash Redis Client & Cache Manager

Connects to Upstash Redis using REST API (via httpx).
Falls back gracefully to in-memory store when Redis is unconfigured or unreachable.
Provides key-value caching, session token blacklisting, and health checks.
"""

import time
from typing import Any, Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class UpstashRedisClient:
    """Async client for Upstash Redis REST API with in-memory fallback."""

    def __init__(self) -> None:
        self.url = settings.UPSTASH_REDIS_REST_URL
        self.token = settings.UPSTASH_REDIS_REST_TOKEN
        self._memory_store: dict[str, tuple[str, Optional[float]]] = {}

    @property
    def is_configured(self) -> bool:
        """Check if Upstash REST credentials are set and active."""
        if settings.ENVIRONMENT.lower() in ("testing", "test"):
            return False
        return bool(self.url and self.token)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def execute_command(self, *cmd: Any) -> Any:
        """Execute a raw Redis command array against Upstash REST API."""
        if not self.is_configured:
            return None

        cmd_list = [str(arg) if not isinstance(arg, (int, float, str)) else arg for arg in cmd]

        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.post(
                    self.url,
                    json=cmd_list,
                    headers=self._headers(),
                )
                response.raise_for_status()
                data = response.json()
                return data.get("result")
        except Exception as exc:
            logger.error("Upstash Redis REST command error [%s]: %s", cmd_list, exc)
            return None

    async def ping(self) -> bool:
        """Ping Redis instance or return True for in-memory fallback."""
        if not self.is_configured:
            return True
        res = await self.execute_command("PING")
        if res is None:
            return True
        return res == "PONG"

    async def get(self, key: str) -> Optional[str]:
        """Get string value by key."""
        if self.is_configured:
            res = await self.execute_command("GET", key)
            if res is not None:
                return str(res)

        item = self._memory_store.get(key)
        if not item:
            return None
        val, exp = item
        if exp and time.time() > exp:
            del self._memory_store[key]
            return None
        return val

    async def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        """Set key-value pair with optional TTL in seconds."""
        exp_time = (time.time() + expire_seconds) if expire_seconds else None
        self._memory_store[key] = (str(value), exp_time)

        if self.is_configured:
            if expire_seconds:
                res = await self.execute_command("SET", key, value, "EX", expire_seconds)
            else:
                res = await self.execute_command("SET", key, value)
            if res == "OK":
                return True

        return True

    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        if key in self._memory_store:
            del self._memory_store[key]

        if self.is_configured:
            res = await self.execute_command("DEL", key)
            try:
                if bool(res and int(res) > 0):
                    return True
            except (ValueError, TypeError):
                pass

        return True

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if self.is_configured:
            res = await self.execute_command("EXISTS", key)
            try:
                if res is not None:
                    return bool(int(res) > 0)
            except (ValueError, TypeError):
                pass

        return (await self.get(key)) is not None

    async def ttl(self, key: str) -> Optional[int]:
        """Return time-to-live in seconds for a key. Returns None if key not found or no TTL."""
        if self.is_configured:
            res = await self.execute_command("TTL", key)
            try:
                if res is not None:
                    ttl_val = int(res)
                    # Redis returns -1 if key has no TTL, -2 if key doesn't exist
                    if ttl_val >= 0:
                        return ttl_val
                    return None
            except (ValueError, TypeError):
                pass

        # In-memory fallback: check remaining TTL
        item = self._memory_store.get(key)
        if item:
            val, exp = item
            if exp:
                remaining = int(exp - time.time())
                return max(0, remaining) if remaining > 0 else None
        return None


# Global Upstash Redis instance
redis_client = UpstashRedisClient()


async def get_redis_client() -> UpstashRedisClient:
    """Dependency / accessor for Redis client."""
    return redis_client
