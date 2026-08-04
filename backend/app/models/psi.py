"""
COMPAREX Backend - Personal Shopping Intelligence (PSI) Domain Models
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ShoppingProfile(Base):
    """User Personal Shopping Profile & Persona."""

    __tablename__ = "shopping_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    persona: Mapped[str] = mapped_column(String(50), default="VALUE_SEEKER", nullable=False)
    is_psi_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    learning_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", backref="shopping_profile")


class UserPreference(Base):
    """Learned & Customizable User Preferences."""

    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    preferred_marketplaces: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    preferred_brands: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    favorite_categories: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    budget_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    budget_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    delivery_speed: Mapped[str] = mapped_column(String(30), default="EXPRESS", nullable=False)
    discount_sensitivity: Mapped[str] = mapped_column(String(30), default="HIGH", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ShoppingMemory(Base):
    """Shopping Interaction History Log."""

    __tablename__ = "shopping_memories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title_or_query: Mapped[str] = mapped_column(String(500), nullable=False)
    category_slug: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    brand_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    marketplace_slug: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class RecommendationHistory(Base):
    """History of Personalized Recommendations Shown to User."""

    __tablename__ = "recommendation_histories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    product_title: Mapped[str] = mapped_column(String(500), nullable=False)
    marketplace_slug: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    personalization_reason: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ShoppingAnalytics(Base):
    """Aggregated User Shopping Analytics & Cumulative Savings."""

    __tablename__ = "shopping_analytics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    total_money_saved: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    average_discount_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    favorite_categories: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    most_viewed_brands: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    favorite_shopping_month: Mapped[str] = mapped_column(
        String(30), default="August", nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class PreferenceEvent(Base):
    """Audit Log of User Preference & Privacy Changes."""

    __tablename__ = "preference_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
