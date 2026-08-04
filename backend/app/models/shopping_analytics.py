"""
COMPAREX Backend – ShoppingAnalytics Model

Aggregates monthly/yearly user savings, discount metrics, and marketplace usage stats.
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class ShoppingAnalytics(Base):
    """User shopping analytics and savings metrics model."""

    __tablename__ = "shopping_analytics"

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
        index=True,
    )

    month_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    total_saved: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    avg_discount: Mapped[float] = mapped_column(Float, default=0.0)
    top_brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    top_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    recommendation_accuracy: Mapped[float] = mapped_column(Float, default=0.92)

    user: Mapped["User"] = relationship("User", backref="shopping_analytics")

    def __repr__(self) -> str:
        return f"<ShoppingAnalytics user={self.user_id} month={self.month_year}>"
