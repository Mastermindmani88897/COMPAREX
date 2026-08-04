"""
COMPAREX Backend – Persona & Shopping DNA API Endpoint

Manages user Shopping DNA personas (Budget Shopper, Deal Hunter, Tech Enthusiast).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.dna import ShoppingDNAResponse, ShoppingDNAUpdate
from app.services.dna_service import ShoppingDNAService

router = APIRouter(prefix="/persona", tags=["Shopping DNA & Persona Engine"])


@router.get(
    "",
    response_model=SuccessResponse[ShoppingDNAResponse],
    summary="Get Shopping DNA Persona",
    description="Retrieve active Shopping DNA persona and behavioral traits.",
)
async def get_persona(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve user Shopping DNA persona."""
    res = await ShoppingDNAService.get_or_create_dna(db, current_user.id)
    return SuccessResponse(message="Shopping DNA persona retrieved", data=res)


@router.put(
    "",
    response_model=SuccessResponse[ShoppingDNAResponse],
    summary="Update Shopping DNA Persona",
    description="Customize or toggle active Shopping DNA persona traits.",
)
async def update_persona(
    payload: ShoppingDNAUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user Shopping DNA persona."""
    res = await ShoppingDNAService.update_dna(db, current_user.id, payload)
    return SuccessResponse(message="Shopping DNA persona updated", data=res)
