"""
COMPAREX Backend – AI Feedback Service

Stores user recommendation feedback (helpful / not helpful) and tunes recommendation metrics.
"""

from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_feedback import AIFeedback
from app.schemas.feedback import AIFeedbackCreate, AIFeedbackResponse


class AIFeedbackService:
    """User rating feedback management service."""

    @classmethod
    async def record_feedback(
        cls,
        db: AsyncSession,
        user_id: UUID,
        payload: AIFeedbackCreate,
    ) -> AIFeedbackResponse:
        """Record user helpful/not helpful rating feedback."""
        feedback = AIFeedback(
            user_id=user_id,
            recommendation_id=payload.recommendation_id,
            is_helpful=payload.is_helpful,
            feedback_text=payload.feedback_text,
        )
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)

        return AIFeedbackResponse(
            id=feedback.id,
            user_id=feedback.user_id,
            recommendation_id=feedback.recommendation_id,
            is_helpful=feedback.is_helpful,
            feedback_text=feedback.feedback_text,
        )

    @classmethod
    async def list_feedback(
        cls,
        db: AsyncSession,
        user_id: UUID,
    ) -> List[AIFeedbackResponse]:
        """List feedback history submitted by user."""
        stmt = select(AIFeedback).where(AIFeedback.user_id == user_id)
        res = await db.execute(stmt)
        items = res.scalars().all()

        return [
            AIFeedbackResponse(
                id=item.id,
                user_id=item.user_id,
                recommendation_id=item.recommendation_id,
                is_helpful=item.is_helpful,
                feedback_text=item.feedback_text,
            )
            for item in items
        ]
