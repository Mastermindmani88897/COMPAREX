"""
COMPAREX Backend – Voice Shopping Architecture Schemas

Interface schemas for future voice shopping command contracts.
"""

from typing import Optional

from pydantic import BaseModel, Field


class VoiceShoppingInterfaceRequest(BaseModel):
    """Voice audio intent request payload contract."""

    transcription: str = Field(description="Recognized speech text")
    language: str = Field(default="en-IN")
    confidence: float = Field(default=0.95)


class VoiceShoppingInterfaceResponse(BaseModel):
    """Voice shopping response payload contract."""

    spoken_response: str
    detected_intent: str
    action_url: Optional[str] = None
