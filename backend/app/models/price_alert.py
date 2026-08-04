"""
COMPAREX Backend – PriceAlert Model

Manages price drop notification triggers and target price threshold configurations.
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class PriceAlert(Base):
    """User price drop alert configuration model."""

    __tablename__ = "price_alerts"

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

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    initial_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    notification_channel: Mapped[str] = mapped_column(String(50), default="email")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    triggered: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", backref="price_alerts")
    product: Mapped["Product"] = relationship("Product", backref="price_alerts")

    def __repr__(self) -> str:
        return f"<PriceAlert user={self.user_id} target={self.target_price}>"
