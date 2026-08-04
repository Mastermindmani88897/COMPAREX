"""
COMPAREX Backend – GoalParser Sub-Service

Parses natural language prompts to extract goal title, scenario type, budget, and priorities.
"""

import re
from typing import List

from app.schemas.planner import GoalParseRequest, GoalParseResponse


class GoalParser:
    """Natural Language Goal Understanding Parser."""

    SCENARIO_KEYWORDS = {
        "engineering": "ENGINEERING_STUDENT",
        "medical": "MEDICAL_STUDENT",
        "law": "LAW_STUDENT",
        "gaming": "GAMING_SETUP",
        "office": "WFH_OFFICE",
        "home": "WFH_OFFICE",
        "creator": "CONTENT_CREATOR",
        "photography": "PHOTOGRAPHER",
        "video": "VIDEO_EDITOR",
        "travel": "TRAVELLER",
        "fitness": "FITNESS",
        "appliances": "SMART_HOME",
    }

    @classmethod
    def parse_goal(cls, payload: GoalParseRequest) -> GoalParseResponse:
        """Extract goal metadata from prompt string."""
        text = payload.prompt.lower()

        extracted_budget = 90000.0
        budget_match = re.search(r"(?:₹|rs\.?|inr)\s*([\d,]+)", text)
        if not budget_match:
            budget_match = re.search(r"([\d,]+)\s*(?:k|thousand|lakh)", text)
            if budget_match:
                val = float(budget_match.group(1).replace(",", ""))
                extracted_budget = val * 1000.0 if val < 500 else val * 100000.0

        scenario = "CUSTOM"
        for kw, scen in cls.SCENARIO_KEYWORDS.items():
            if kw in text:
                scenario = scen
                break

        title = payload.prompt[:60].strip().capitalize()
        priorities: List[str] = ["Performance", "Value for Money", "Ecosystem Integration"]
        owned_items: List[str] = []

        return GoalParseResponse(
            goal_title=title,
            scenario_type=scenario,
            extracted_budget=extracted_budget,
            priorities=priorities,
            owned_items=owned_items,
        )
