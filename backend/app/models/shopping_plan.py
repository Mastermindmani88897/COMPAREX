"""
COMPAREX Backend – ShoppingPlan Model

Stores user goal plans, target budget, allocated funds, remaining buffer, and scenario type.
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.plan_item import PlanItem
    from app.models.user import User


class ShoppingPlan(Base):
    """User Shopping Goal Plan ORM Model."""

    __tablename__ = "shopping_plans"

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

    goal_title: Mapped[str] = mapped_column(String(255), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(50), default="CUSTOM")
    total_budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    allocated_budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    remaining_budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", backref="shopping_plans")
    items: Mapped[List["PlanItem"]] = relationship(
        "PlanItem", back_populates="plan", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ShoppingPlan title='{self.goal_title}' budget={self.total_budget}>"
