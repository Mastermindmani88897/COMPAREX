"""
COMPAREX Backend – ShoppingPlanner Sub-Service

Generates multi-category product setups for required, recommended, and optional items.
"""

from typing import List

from app.schemas.planner import CategoryPlanItem


class ShoppingPlanner:
    """Multi-Category Setup Blueprint Generator."""

    PRESET_BLUEPRINTS = {
        "ENGINEERING_STUDENT": [
            (
                "Laptop",
                "REQUIRED",
                "Lenovo LOQ Intel Core i5 (16GB/512GB SSD/RTX 3050)",
                62000.0,
                "Amazon India",
            ),
            ("Mouse", "REQUIRED", "Logitech MX Master 3S Wireless Mouse", 6999.0, "Flipkart"),
            ("Backpack", "REQUIRED", "Wildcraft Laptop Backpack 30L", 1999.0, "Amazon India"),
            ("External SSD", "RECOMMENDED", "SanDisk 1TB Extreme Portable SSD", 7499.0, "Croma"),
            (
                "Noise Cancelling Headphones",
                "RECOMMENDED",
                "Sony WH-CH720N Wireless ANC Headphones",
                7990.0,
                "Reliance Digital",
            ),
            (
                "USB-C Docking Station",
                "OPTIONAL",
                "Anker 7-in-1 USB-C Docking Station",
                3499.0,
                "Amazon India",
            ),
        ],
        "GAMING_SETUP": [
            (
                "Gaming Laptop / PC",
                "REQUIRED",
                "ASUS TUF Gaming F15 Intel Core i7 (RTX 4060)",
                84990.0,
                "Flipkart",
            ),
            (
                "Mechanical Keyboard",
                "REQUIRED",
                "Keychron K2 Wireless Mechanical Keyboard",
                7499.0,
                "Amazon India",
            ),
            (
                "Gaming Mouse",
                "REQUIRED",
                "Razer DeathAdder V3 Ergonomic Mouse",
                4999.0,
                "Vijay Sales",
            ),
            (
                "Gaming Monitor",
                "RECOMMENDED",
                "LG Ultragear 24-inch 165Hz IPS Gaming Monitor",
                11999.0,
                "Amazon India",
            ),
            ("Headset", "RECOMMENDED", "HyperX Cloud III Gaming Headset", 6990.0, "Croma"),
        ],
        "WFH_OFFICE": [
            ("Laptop", "REQUIRED", "Apple MacBook Air M3 (8GB/256GB)", 94900.0, "Amazon India"),
            (
                "Ergonomic Chair",
                "REQUIRED",
                "Green Soul Monster Ultimate Ergonomic Chair",
                16999.0,
                "Flipkart",
            ),
            ("Monitor", "RECOMMENDED", "Dell 27-inch 4K UHD USB-C Monitor", 27999.0, "Croma"),
            ("Webcam", "RECOMMENDED", "Logitech C922 Pro Stream HD Webcam", 7999.0, "Amazon India"),
        ],
    }

    @classmethod
    def generate_category_items(
        cls,
        scenario_type: str,
        target_budget: float,
    ) -> List[CategoryPlanItem]:
        """Generate setup categories for specified scenario blueprint."""
        blueprint = cls.PRESET_BLUEPRINTS.get(
            scenario_type, cls.PRESET_BLUEPRINTS["ENGINEERING_STUDENT"]
        )
        items: List[CategoryPlanItem] = []

        for category, req, name, base_price, mp in blueprint:
            items.append(
                CategoryPlanItem(
                    category_name=category,
                    requirement_level=req,
                    product_name=name,
                    price=base_price,
                    marketplace_name=mp,
                    deal_score=9.2,
                    compatibility_score=0.96,
                    is_selected=True,
                    rationale=f"Selected for top performance in {scenario_type} setup.",
                )
            )

        return items
