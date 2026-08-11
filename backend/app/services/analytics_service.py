"""
COMPAREX Backend – Analytics Service

Computes monthly/yearly savings stats, brand preferences, and recommendation accuracy.
All values come exclusively from real database records — no hardcoded fallback data.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shopping_analytics import ShoppingAnalytics
from app.schemas.analytics import ShoppingAnalyticsResponse


class AnalyticsService:
    """User Shopping Analytics Engine Service."""

    @classmethod
    async def get_user_analytics(
        cls,
        db: AsyncSession,
        user_id: UUID,
        month_year: str = "2026-08",
    ) -> ShoppingAnalyticsResponse:
        """Fetch user monthly/yearly shopping analytics overview from real database records."""
        stmt = select(ShoppingAnalytics).where(
            ShoppingAnalytics.user_id == user_id,
            ShoppingAnalytics.month_year == month_year,
        )
        res = await db.execute(stmt)
        record = res.scalars().first()

        if not record:
            # Return a valid empty response — no fake/hardcoded data whatsoever.
            return ShoppingAnalyticsResponse(
                user_id=user_id,
                month_year=month_year,
                total_saved=0.0,
                avg_discount=0.0,
                top_brand=None,
                top_category=None,
                recommendation_accuracy=0.0,
                insights=[
                    "No analytics data yet for this period.",
                    "Compare products and track price alerts to build your shopping insights.",
                ],
            )

        return ShoppingAnalyticsResponse(
            id=record.id,
            user_id=record.user_id,
            month_year=record.month_year,
            total_saved=float(record.total_saved),
            avg_discount=float(record.avg_discount) if record.avg_discount else 0.0,
            top_brand=record.top_brand,
            top_category=record.top_category,
            recommendation_accuracy=float(record.recommendation_accuracy)
            if record.recommendation_accuracy
            else 0.0,
            insights=[
                f"Saved ₹{record.total_saved:,.0f} in {month_year}.",
                f"Favourite Brand: {record.top_brand or 'General'}",
            ],
        )
