"""
COMPAREX Backend – Price Comparison Engine Service

Computes price matrices, savings potential, deal scores,
and marketplace comparison metrics.
"""

from decimal import Decimal
from typing import Any


class ComparisonEngineService:
    """Service providing comparison matrix calculations across product listings."""

    @staticmethod
    def calculate_comparison_matrix(
        product_id: str,
        product_name: str,
        listings: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Process listings and return a structured price comparison matrix.

        :param product_id: Canonical product UUID string
        :param product_name: Product title string
        :param listings: List of product listing dictionary payloads
        :return: Standardized comparison matrix dictionary
        """
        if not listings:
            return {
                "product_id": product_id,
                "product_name": product_name,
                "listings": [],
                "total_listings": 0,
                "lowest_price": None,
                "highest_price": None,
                "average_price": None,
                "price_spread": 0.0,
                "best_listing_id": None,
                "max_savings": 0.0,
            }

        available_listings = [lst for lst in listings if lst.get("is_available", True)]
        target_listings = available_listings if available_listings else listings

        prices = [float(lst["price"]) for lst in target_listings if lst.get("price") is not None]

        lowest_price = min(prices) if prices else 0.0
        highest_price = max(prices) if prices else 0.0
        avg_price = sum(prices) / len(prices) if prices else 0.0
        price_spread = highest_price - lowest_price

        # Rank listings by price & rating to pick best listing
        def compute_deal_score(item: dict[str, Any]) -> float:
            p = float(item.get("price", 999999))
            rating = float(item.get("rating") or 3.5)
            discount = float(item.get("discount_percent") or 0)
            is_prime = 1.0 if item.get("is_prime") else 0.0
            # Higher score is better
            score = (100000.0 / (p + 1.0)) * 0.7 + (rating * 2.0) + (discount * 0.5)
            score += is_prime * 3.0
            return score

        sorted_listings = sorted(target_listings, key=compute_deal_score, reverse=True)
        best_listing_id = sorted_listings[0].get("id") if sorted_listings else None

        # Annotate listings with badges
        annotated_listings = []
        for lst in listings:
            l_copy = dict(lst)
            p = float(lst.get("price", 0))
            badges = []
            if p == lowest_price and lowest_price > 0:
                badges.append("BEST_PRICE")
            if lst.get("is_prime"):
                badges.append("EXPRESS_DELIVERY")
            if float(lst.get("rating") or 0) >= 4.5:
                badges.append("TOP_RATED")
            if not lst.get("is_available"):
                badges.append("OUT_OF_STOCK")

            l_copy["badges"] = badges
            if lst.get("discount_percent") is not None:
                l_copy["discount_percent"] = float(lst["discount_percent"])
            elif lst.get("original_price") and float(lst["original_price"]) > p:
                orig = float(lst["original_price"])
                l_copy["discount_percent"] = round(((orig - p) / orig) * 100, 2)
            else:
                l_copy["discount_percent"] = 0.0

            annotated_listings.append(l_copy)

        # Sort annotated listings by price ascending
        annotated_listings.sort(key=lambda x: float(x.get("price", 0)))

        return {
            "product_id": product_id,
            "product_name": product_name,
            "listings": annotated_listings,
            "total_listings": len(listings),
            "lowest_price": float(Decimal(str(lowest_price))),
            "highest_price": float(Decimal(str(highest_price))),
            "average_price": round(avg_price, 2),
            "price_spread": round(price_spread, 2),
            "best_listing_id": str(best_listing_id) if best_listing_id else None,
            "max_savings": round(price_spread, 2),
        }
