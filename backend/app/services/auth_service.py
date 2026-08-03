"""
COMPAREX Backend – Auth Service (Stub)

Full implementation in Phase 2 — login, registration, token refresh logic.
"""

from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """
    Authentication service — orchestrates login, registration, and token management.

    Phase 2 Implementation Plan:
    - register(user_data) -> UserPublic
    - login(email, password) -> TokenPair
    - refresh_token(refresh_token) -> TokenPair
    - logout(token) -> None
    - verify_email(token) -> None
    - request_password_reset(email) -> None
    - reset_password(token, new_password) -> None
    """

    pass  # Phase 2
