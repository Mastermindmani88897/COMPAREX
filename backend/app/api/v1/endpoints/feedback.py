"""
COMPAREX Backend – AI Feedback API Endpoints

Stores user rating feedback (helpful / not helpful) to improve AI recommendations.
"""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.feedback import AIFeedbackCreate, AIFeedbackResponse
from app.services.feedback_service import AIFeedbackService

router = APIRouter(prefix="/feedback", tags=["AI Recommendation Feedback Loop"])


@router.post(
    "",
    response_model=SuccessResponse[AIFeedbackResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit AI Recommendation Rating Feedback",
    description="Submit helpful / not helpful rating feedback on AI recommendation.",
)
async def submit_feedback(
    payload: AIFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit AI recommendation rating feedback."""
    res = await AIFeedbackService.record_feedback(db, current_user.id, payload)
    return SuccessResponse(message="AI recommendation feedback recorded", data=res)


@router.get(
    "",
    response_model=SuccessResponse[List[AIFeedbackResponse]],
    summary="List User Feedback History",
    description="Retrieve list of past recommendation rating feedback submitted by user.",
)
async def list_feedback(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve user rating feedback history."""
    res = await AIFeedbackService.list_feedback(db, current_user.id)
    return SuccessResponse(message="Feedback history retrieved", data=res)
