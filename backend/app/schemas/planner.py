"""
COMPAREX Backend – AI Marketplace Planner Schemas

Goal parsing, budget allocation, compatibility validation, simulation, and report schemas.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GoalParseRequest(BaseModel):
    """Payload to parse natural language shopping goal prompt."""

    prompt: str = Field(description="Goal prompt, e.g. 'Engineering student setup under ₹90,000'")


class GoalParseResponse(BaseModel):
    """Parsed goal structure."""

    goal_title: str
    scenario_type: str
    extracted_budget: float
    priorities: List[str] = Field(default_factory=list)
    owned_items: List[str] = Field(default_factory=list)


class CategoryPlanItem(BaseModel):
    """Category item recommendation within shopping plan."""

    category_name: str
    requirement_level: str = Field(description="REQUIRED, RECOMMENDED, OPTIONAL")
    product_name: str
    price: float
    marketplace_name: str = "Amazon India"
    deal_score: float = 9.2
    compatibility_score: float = 0.95
    is_selected: bool = True
    rationale: Optional[str] = None


class PlanGenerationRequest(BaseModel):
    """Payload to generate full multi-category shopping plan."""

    prompt: str
    budget: Optional[float] = None
    scenario_type: Optional[str] = None
    priorities: Optional[List[str]] = None


class PlanGenerationResponse(BaseModel):
    """Generated shopping plan response."""

    id: Optional[UUID] = None
    goal_title: str
    scenario_type: str
    total_budget: float
    allocated_budget: float
    remaining_budget: float
    compatibility_score: float = 0.98
    items: List[CategoryPlanItem] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class PlanSimulationRequest(BaseModel):
    """Payload to re-simulate plan upon user tweaks."""

    items: List[CategoryPlanItem]
    target_budget: float
    filter_marketplace: Optional[str] = None
    optimize_mode: str = Field(default="BALANCED", description="BEST_VALUE, PREMIUM, FASTEST")


class PlanConversationRequest(BaseModel):
    """Follow-up natural language editing message payload."""

    message: str
    current_plan: PlanGenerationResponse


class PlanExportResponse(BaseModel):
    """Shopping plan export response model."""

    goal_title: str
    format: str = Field(description="JSON, CSV, PDF_HTML")
    export_payload: Dict[str, Any]
