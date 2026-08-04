"""
COMPAREX Backend – ShoppingProfile Model

Opt-in user shopping preferences, budget bounds, seller choices, and sensitivity profile.
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, Boolean, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class ShoppingProfile(Base):
    """User opt-in shopping preference profile model."""

    __tablename__ = "shopping_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    consent_opt_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    preferred_brands: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String).with_variant(JSON, "sqlite"), nullable=True
    )
    preferred_marketplaces: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String).with_variant(JSON, "sqlite"), nullable=True
    )
    preferred_categories: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String).with_variant(JSON, "sqlite"), nullable=True
    )
    min_budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    max_budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("500000.00"))
    delivery_speed: Mapped[str] = mapped_column(String(50), default="EXPRESS")
    seller_preference: Mapped[str] = mapped_column(String(50), default="VERIFIED_ONLY")
    discount_sensitivity: Mapped[str] = mapped_column(String(20), default="HIGH")

    user: Mapped["User"] = relationship("User", backref="shopping_profile")

    def __repr__(self) -> str:
        return f"<ShoppingProfile user={self.user_id} opt_in={self.consent_opt_in}>"
