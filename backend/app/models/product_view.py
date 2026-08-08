"""
COMPAREX Backend – Product View (Recently Viewed) ORM Model
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductView(Base):
    """Stores user product viewing history for recently viewed tracking."""

    __tablename__ = "product_views"

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
    viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
    )
    price_at_view: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    user = relationship("User", backref="product_views")
    product = relationship("Product", backref="views")

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_product_view"),
    )

    def __repr__(self) -> str:
        return (
            f"<ProductView user_id={self.user_id} product_id={self.product_id} "
            f"viewed_at={self.viewed_at}>"
        )
