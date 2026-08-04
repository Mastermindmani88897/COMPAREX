"""
COMPAREX Backend – Advanced AI Mode Service

Provides tuning profiles for 9 specialized AI modes.
"""

from typing import Dict, List

from app.schemas.ai_modes import AIModeDefinition, AIModeSelectRequest, AIModeSelectResponse


class AIModeService:
    """Advanced AI Mode Tuning Engine."""

    MODES: Dict[str, AIModeDefinition] = {
        "BUDGET": AIModeDefinition(
            mode_id="BUDGET",
            mode_name="Budget Mode",
            description="Strictly prioritizes lowest price, max discount %, and cashback.",
            weights={"price": 0.50, "deal_score": 0.30, "specs": 0.20},
        ),
        "PERFORMANCE": AIModeDefinition(
            mode_id="PERFORMANCE",
            mode_name="Performance Mode",
            description="Prioritizes hardware specifications, benchmarks, and thermal ratings.",
            weights={"price": 0.10, "deal_score": 0.20, "specs": 0.70},
        ),
        "PREMIUM": AIModeDefinition(
            mode_id="PREMIUM",
            mode_name="Premium Mode",
            description="Prioritizes top tier build quality, verified sellers, and warranty.",
            weights={"price": 0.10, "seller_trust": 0.40, "specs": 0.50},
        ),
        "STUDENT": AIModeDefinition(
            mode_id="STUDENT",
            mode_name="Student Mode",
            description="Focuses on durability, battery life, student discounts, and value.",
            weights={"price": 0.40, "battery": 0.30, "specs": 0.30},
        ),
        "PROFESSIONAL": AIModeDefinition(
            mode_id="PROFESSIONAL",
            mode_name="Professional Mode",
            description="Prioritizes color accuracy, RAM capacity, and reliability.",
            weights={"specs": 0.60, "seller_trust": 0.30, "price": 0.10},
        ),
        "GAMING": AIModeDefinition(
            mode_id="GAMING",
            mode_name="Gaming Mode",
            description="Focuses on GPU TGP, display refresh rates, and low latency.",
            weights={"gpu": 0.50, "display_hz": 0.30, "price": 0.20},
        ),
        "ECO": AIModeDefinition(
            mode_id="ECO",
            mode_name="Eco Mode",
            description="Prioritizes energy efficiency star ratings and sustainable materials.",
            weights={"energy_rating": 0.50, "price": 0.30, "specs": 0.20},
        ),
        "FAST_DELIVERY": AIModeDefinition(
            mode_id="FAST_DELIVERY",
            mode_name="Fast Delivery Mode",
            description="Prioritizes express 1-day/same-day local delivery availability.",
            weights={"delivery_speed": 0.70, "price": 0.20, "specs": 0.10},
        ),
        "GIFT_RECOMMENDATION": AIModeDefinition(
            mode_id="GIFT_RECOMMENDATION",
            mode_name="Gift Recommendation Mode",
            description="Focuses on unboxing experience, high ratings, and gift wrapping.",
            weights={"ratings": 0.40, "packaging": 0.30, "price": 0.30},
        ),
    }

    @classmethod
    def list_modes(cls) -> List[AIModeDefinition]:
        """List all 9 available AI modes."""
        return list(cls.MODES.values())

    @classmethod
    def select_mode(cls, payload: AIModeSelectRequest) -> AIModeSelectResponse:
        """Select active AI mode profile."""
        mode_id = payload.mode_id.upper()
        mode_def = cls.MODES.get(mode_id, cls.MODES["BUDGET"])

        return AIModeSelectResponse(
            active_mode=mode_def.mode_id,
            mode_definition=mode_def,
            message=f"Active AI mode switched to {mode_def.mode_name}.",
        )
