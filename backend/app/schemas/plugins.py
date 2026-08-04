"""
COMPAREX Backend – AI Plugin Architecture Schemas

Interface schemas for future tool plugins (Shopping Tool, Vision Tool, Coupon Tool).
"""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class AIPluginManifest(BaseModel):
    """Manifest describing an AI plugin capabilities."""

    plugin_name: str
    version: str = "1.0.0"
    description: str
    capabilities: List[str] = Field(default_factory=list)


class AIPluginExecuteRequest(BaseModel):
    """Payload to execute an AI tool plugin."""

    plugin_name: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AIPluginExecuteResponse(BaseModel):
    """Execution output from AI tool plugin."""

    plugin_name: str
    action: str
    status: str = "success"
    result: Dict[str, Any] = Field(default_factory=dict)
