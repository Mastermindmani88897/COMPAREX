"""
COMPAREX Backend – Security Utilities

Placeholder module for JWT creation/verification and password hashing.
Full implementation in Phase 2 when auth endpoints are built.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Password Hashing ──────────────────────────────────────────────────────────
# Phase 2: Full bcrypt implementation will go here


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password. (Stub – Phase 2)"""
    # from passlib.context import CryptContext
    # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # return pwd_context.hash(plain_password)
    raise NotImplementedError("Password hashing not implemented until Phase 2")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a hash. (Stub – Phase 2)"""
    raise NotImplementedError("Password verification not implemented until Phase 2")


# ── JWT Tokens ────────────────────────────────────────────────────────────────


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    """Create a signed JWT access token. (Stub – Phase 2)"""
    # from jose import jwt
    # expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    # payload = {"sub": subject, "exp": expire, "iat": datetime.now(timezone.utc), "type": "access"}
    # if extra_claims:
    #     payload.update(extra_claims)
    # return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    raise NotImplementedError("JWT creation not implemented until Phase 2")


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT access token. (Stub – Phase 2)"""
    raise NotImplementedError("JWT decoding not implemented until Phase 2")
