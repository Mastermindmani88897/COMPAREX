"""
COMPAREX Backend – RecommendationHistory Model

Logs personalized recommendation events, reasoning, and confidence scores.
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class RecommendationHistory(Base):
    """Historical AI recommendation record model."""

    __tablename__ = "recommendation_histories"

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

    query: Mapped[str] = mapped_column(String(255), nullable=False)
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.90)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(20), default="v8.0")

    user: Mapped["User"] = relationship("User", backref="recommendation_histories")

    def __repr__(self) -> str:
        return f"<RecommendationHistory user={self.user_id} score={self.confidence_score}>"
