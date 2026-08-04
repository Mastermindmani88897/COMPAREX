"""
COMPAREX Backend – Coupon Model

Stores marketplace promotional coupons, discount rules, and applicability metadata.
"""

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, Float, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Coupon(Base):
    """Marketplace coupon & promo offer model."""

    __tablename__ = "coupons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    code: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    marketplace_slug: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    discount_type: Mapped[str] = mapped_column(String(20), default="PERCENTAGE")
    discount_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    min_order_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    max_discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    offer_type: Mapped[str] = mapped_column(String(50), default="COUPON")
    bank_name: Mapped[str] = mapped_column(String(100), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.95)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Coupon code={self.code} marketplace={self.marketplace_slug}>"
