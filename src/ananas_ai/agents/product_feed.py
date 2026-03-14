"""Product Feed Agent — catalog quality scan + Google Shopping feed readiness.

Phase 1: sample data with realistic Ananas catalog patterns.
Phase 2: wires into Product Catalog API and Google Shopping feed API.

Runs weekly (Thursday 08:00). With 250k+ products and zero Google Shopping
campaigns, feed quality is the direct prerequisite to launching Shopping.
"""

from __future__ import annotations

import os
from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

# Realistic attribute gap distribution for a 250k Balkan marketplace catalog.
# Suppliers upload product data at varying quality levels.
SAMPLE_ATTRIBUTE_GAPS: list[dict[str, Any]] = [
    {"attribute": "gtin_ean", "missing_count": 41200, "missing_pct": 16.5, "impact": "critical"},
    {"attribute": "brand", "missing_count": 28700, "missing_pct": 11.5, "impact": "high"},
    {
        "attribute": "description_min_150_chars",
        "missing_count": 19800,
        "missing_pct": 7.9,
        "impact": "high",
    },
    {
        "attribute": "image_count_min_3",
        "missing_count": 15600,
        "missing_pct": 6.2,
        "impact": "medium",
    },
    {"attribute": "color", "missing_count": 34100, "missing_pct": 13.6, "impact": "medium"},
    {"attribute": "size", "missing_count": 29400, "missing_pct": 11.8, "impact": "medium"},
    {"attribute": "material", "missing_count": 52300, "missing_pct": 20.9, "impact": "low"},
]

SAMPLE_DISAPPROVALS: list[dict[str, Any]] = [
    {
        "reason": "Missing required attribute: GTIN",
        "count": 8340,
        "fix": "Add EAN/UPC from supplier",
    },
    {
        "reason": "Image too small (< 100x100px)",
        "count": 3120,
        "fix": "Re-upload higher resolution images",
    },
    {
        "reason": "Title too generic (< 3 category-relevant words)",
        "count": 2870,
        "fix": "Improve title template",
    },
    {
        "reason": "Price mismatch: landing page vs feed",
        "count": 412,
        "fix": "Fix price sync pipeline",
    },
    {
        "reason": "Availability 'out of stock' but bidding enabled",
        "count": 198,
        "fix": "Update feed refresh schedule",
    },
]

SAMPLE_HIGH_TRAFFIC_LOW_CVR: list[dict[str, Any]] = [
    {
        "product_id": "AN-48291",
        "name": "Samsung 65 OLED TV",
        "category": "Electronics/TV",
        "sessions": 4120,
        "cvr_pct": 0.4,
        "issue": "No energy label, missing technical specs",
    },
    {
        "product_id": "AN-12847",
        "name": "Nike Air Max 270",
        "category": "Shoes/Sneakers",
        "sessions": 3870,
        "cvr_pct": 0.6,
        "issue": "Only 1 image, no size guide link",
    },
    {
        "product_id": "AN-73621",
        "name": "Philips Air Fryer XXL",
        "category": "Kitchen/Appliances",
        "sessions": 3540,
        "cvr_pct": 0.5,
        "issue": "Description 48 chars, no capacity/wattage",
    },
    {
        "product_id": "AN-29104",
        "name": "Adidas Ultraboost 22",
        "category": "Shoes/Running",
        "sessions": 3210,
        "cvr_pct": 0.7,
        "issue": "Missing color variants, 2 images only",
    },
    {
        "product_id": "AN-55839",
        "name": "Bosch Dishwasher SMS4",
        "category": "Appliances/Dishwashers",
        "sessions": 2980,
        "cvr_pct": 0.3,
        "issue": "No energy class, missing capacity, old images",
    },
]

SAMPLE_CATEGORY_HEALTH: list[dict[str, Any]] = [
    {
        "category": "Electronics",
        "total": 18400,
        "shopping_eligible_pct": 61.2,
        "trend": "improving",
    },
    {
        "category": "Shoes & Clothing",
        "total": 67200,
        "shopping_eligible_pct": 54.8,
        "trend": "stable",
    },
    {
        "category": "Home & Garden",
        "total": 42100,
        "shopping_eligible_pct": 49.3,
        "trend": "declining",
    },
    {
        "category": "Sports & Outdoors",
        "total": 28600,
        "shopping_eligible_pct": 57.1,
        "trend": "stable",
    },
    {
        "category": "Beauty & Health",
        "total": 31800,
        "shopping_eligible_pct": 44.6,
        "trend": "declining",
    },
    {
        "category": "Toys & Kids",
        "total": 19700,
        "shopping_eligible_pct": 68.4,
        "trend": "improving",
    },
    {"category": "Automotive", "total": 14300, "shopping_eligible_pct": 38.2, "trend": "declining"},
]


class ProductFeedAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="product-feed-agent", module_name="product-feed")

    def _catalog_api_configured(self) -> bool:
        return bool(os.environ.get("CATALOG_API_URL") and os.environ.get("CATALOG_API_KEY"))

    def _shopping_api_configured(self) -> bool:
        return bool(
            os.environ.get("GOOGLE_MERCHANT_ID") and os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
        )

    def fetch_live_data(self, date_from: str, date_to: str) -> dict:
        """Fetch from Product Catalog API + Google Merchant Center.
        TODO: implement once CATALOG_API_URL and CATALOG_API_KEY are available.
        """
        raise NotImplementedError("Product Catalog API integration pending")

    def sample_summary(self) -> dict:
        total_products = 251_400
        shopping_eligible = 148_327
        feed_health_pct = round(shopping_eligible / total_products * 100, 1)
        total_disapprovals = sum(d["count"] for d in SAMPLE_DISAPPROVALS)

        return {
            "headline": (
                f"Feed health {feed_health_pct}% ({shopping_eligible:,}/{total_products:,} eligible) "
                f"| {total_disapprovals:,} disapprovals"
            ),
            "sources_live": False,
            "total_products": total_products,
            "shopping_eligible": shopping_eligible,
            "feed_health_pct": feed_health_pct,
            "feed_health_target_pct": 90.0,
            "total_disapprovals": total_disapprovals,
            "disapprovals": SAMPLE_DISAPPROVALS,
            "attribute_gaps": SAMPLE_ATTRIBUTE_GAPS,
            "high_traffic_low_cvr": SAMPLE_HIGH_TRAFFIC_LOW_CVR,
            "category_health": SAMPLE_CATEGORY_HEALTH,
            "weeks_to_target": _estimate_weeks_to_target(feed_health_pct, 90.0),
            "note": "Sample data -- wire CATALOG_API_URL + CATALOG_API_KEY for live scan.",
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self._catalog_api_configured():
            logger.info("product-feed-agent: fetching from Product Catalog API")
            try:
                raw = self.fetch_live_data(date_from, date_to)
            except NotImplementedError:
                logger.warning(
                    "product-feed-agent: API integration not yet implemented, using sample data"
                )
                raw = self.sample_summary()
            except Exception as e:
                logger.warning("product-feed-agent: catalog API fetch failed: %s", e)
                raw = self.sample_summary()
        else:
            logger.warning("product-feed-agent: catalog API not configured, using sample data")
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Product Feed Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace with 250,000+ products. "
            "CRITICAL CONTEXT: Ananas currently has ZERO Google Shopping campaigns despite having "
            "250k products. Feed quality is the direct prerequisite to launching Shopping. "
            "Google's AI Shopping gives 3-4x higher visibility to catalogs with >90% attribute completeness. "
            "Your job: scan catalog quality, identify the highest-impact fixes to reach 90% feed health, "
            "and give the content team a specific action list ranked by GMV impact. "
            "Format: feed health score, top 3 attribute gaps, top 5 disapproval reasons, "
            "top 5 high-traffic low-CVR products needing content fixes, "
            "category health table, one immediate action for this week."
        )
        user = (
            f"Week of: {date_from}\n"
            f"Product feed data:\n{raw}\n\n"
            "Write the weekly product feed health report."
        )

        try:
            result = call_model(route.model, system, user)
            raw["analysis"] = result["text"]
            raw["model_used"] = result["model_used"]
            raw["fallback"] = result["fallback"]
            raw["tokens_in"] = result["tokens_in"]
            raw["tokens_out"] = result["tokens_out"]
            raw["estimated_cost"] = result["estimated_cost"]
        except Exception as e:
            logger.error("product-feed-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Product feed summary -- model unavailable")

        return raw


def _estimate_weeks_to_target(
    current_pct: float, target_pct: float, weekly_improvement: float = 1.5
) -> int:
    """Rough estimate of weeks to reach target feed health at current improvement rate."""
    if current_pct >= target_pct:
        return 0
    return int((target_pct - current_pct) / weekly_improvement) + 1
