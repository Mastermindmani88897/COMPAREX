"""
COMPAREX Backend – PlanItem Model

Stores individual category product items inside a ShoppingPlan setup.
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.shopping_plan import ShoppingPlan


class PlanItem(Base):
    """Category item within a ShoppingPlan setup."""

    __tablename__ = "plan_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shopping_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    requirement_level: Mapped[str] = mapped_column(String(20), default="REQUIRED")
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    marketplace_name: Mapped[str] = mapped_column(String(100), default="Amazon India")
    deal_score: Mapped[float] = mapped_column(Float, default=9.0)
    compatibility_score: Mapped[float] = mapped_column(Float, default=0.95)
    is_selected: Mapped[bool] = mapped_column(Boolean, default=True)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    plan: Mapped["ShoppingPlan"] = relationship("ShoppingPlan", back_populates="items")

    def __repr__(self) -> str:
        return f"<PlanItem category='{self.category_name}' product='{self.product_name}'>"
