"""
COMPAREX Backend – ShoppingMemory Model

Stores user interaction history events (searches, views, comparisons) for opt-in recall.
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class ShoppingMemory(Base):
    """User shopping history and context memory model."""

    __tablename__ = "shopping_memories"

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

    memory_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    query: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", backref="shopping_memories")

    def __repr__(self) -> str:
        return f"<ShoppingMemory user={self.user_id} type={self.memory_type}>"
