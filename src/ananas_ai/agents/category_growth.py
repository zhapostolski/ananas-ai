"""Category Growth Agent - marketplace category intelligence.

Phase 1: sample data with realistic Ananas category performance.
Phase 2: wires into Categories API, Margin API, Returns API + GA4.

Runs weekly (Monday 08:30). Ranks categories by revenue, margin, return risk,
and demand trend. Identifies which categories to scale, monitor, or fix.
This is the foundational marketplace intelligence layer.
"""

from __future__ import annotations

import os
from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

# Realistic Ananas category performance data.
# Categories span a typical Balkan general marketplace catalog.
SAMPLE_CATEGORIES: list[dict[str, Any]] = [
    {
        "name": "Electronics",
        "subcategories": 47,
        "active_products": 18_400,
        "weekly_revenue_eur": 284_200,
        "wow_revenue_change_pct": 3.2,
        "margin_pct": 14.2,
        "return_rate_pct": 8.1,
        "demand_trend": "growing",
        "ga4_sessions_wow_change_pct": 5.1,
        "top_subcategory": "Smartphones",
        "risk_flags": [],
        "signal": "SCALE",
    },
    {
        "name": "Shoes & Clothing",
        "subcategories": 124,
        "active_products": 67_200,
        "weekly_revenue_eur": 198_400,
        "wow_revenue_change_pct": -1.8,
        "margin_pct": 32.1,
        "return_rate_pct": 18.4,
        "demand_trend": "stable",
        "ga4_sessions_wow_change_pct": -0.9,
        "top_subcategory": "Sneakers",
        "risk_flags": ["return_rate_above_15pct"],
        "signal": "MONITOR",
    },
    {
        "name": "Home & Garden",
        "subcategories": 89,
        "active_products": 42_100,
        "weekly_revenue_eur": 152_100,
        "wow_revenue_change_pct": 1.4,
        "margin_pct": 22.8,
        "return_rate_pct": 6.2,
        "demand_trend": "growing",
        "ga4_sessions_wow_change_pct": 4.2,
        "top_subcategory": "Garden Furniture",
        "risk_flags": [],
        "signal": "SCALE",
    },
    {
        "name": "Beauty & Health",
        "subcategories": 63,
        "active_products": 31_800,
        "weekly_revenue_eur": 98_700,
        "wow_revenue_change_pct": 6.8,
        "margin_pct": 38.6,
        "return_rate_pct": 4.1,
        "demand_trend": "accelerating",
        "ga4_sessions_wow_change_pct": 8.3,
        "top_subcategory": "Skincare",
        "risk_flags": [],
        "signal": "SCALE",
    },
    {
        "name": "Sports & Outdoors",
        "subcategories": 52,
        "active_products": 28_600,
        "weekly_revenue_eur": 87_400,
        "wow_revenue_change_pct": 12.1,
        "margin_pct": 28.4,
        "return_rate_pct": 9.7,
        "demand_trend": "accelerating",
        "ga4_sessions_wow_change_pct": 14.2,
        "top_subcategory": "Cycling",
        "risk_flags": [],
        "signal": "SCALE",
    },
    {
        "name": "Toys & Kids",
        "subcategories": 38,
        "active_products": 19_700,
        "weekly_revenue_eur": 64_200,
        "wow_revenue_change_pct": -4.2,
        "margin_pct": 26.3,
        "return_rate_pct": 5.8,
        "demand_trend": "declining",
        "ga4_sessions_wow_change_pct": -6.1,
        "top_subcategory": "Building Sets",
        "risk_flags": ["demand_declining_3_consecutive_weeks"],
        "signal": "INVESTIGATE",
    },
    {
        "name": "Automotive",
        "subcategories": 34,
        "active_products": 14_300,
        "weekly_revenue_eur": 43_800,
        "wow_revenue_change_pct": -8.4,
        "margin_pct": 18.7,
        "return_rate_pct": 11.2,
        "demand_trend": "declining",
        "ga4_sessions_wow_change_pct": -9.8,
        "top_subcategory": "Car Electronics",
        "risk_flags": ["revenue_declining", "return_rate_above_10pct"],
        "signal": "FIX",
    },
    {
        "name": "Books & Media",
        "subcategories": 18,
        "active_products": 9_200,
        "weekly_revenue_eur": 18_400,
        "wow_revenue_change_pct": -2.1,
        "margin_pct": 12.4,
        "return_rate_pct": 2.1,
        "demand_trend": "stable",
        "ga4_sessions_wow_change_pct": -1.4,
        "top_subcategory": "Bestsellers",
        "risk_flags": ["low_margin"],
        "signal": "MAINTAIN",
    },
    {
        "name": "Food & Grocery",
        "subcategories": 29,
        "active_products": 8_100,
        "weekly_revenue_eur": 29_600,
        "wow_revenue_change_pct": 9.2,
        "margin_pct": 19.8,
        "return_rate_pct": 1.4,
        "demand_trend": "growing",
        "ga4_sessions_wow_change_pct": 11.3,
        "top_subcategory": "Organic Food",
        "risk_flags": [],
        "signal": "SCALE",
    },
    {
        "name": "Office & Stationery",
        "subcategories": 22,
        "active_products": 11_700,
        "weekly_revenue_eur": 22_100,
        "wow_revenue_change_pct": -0.4,
        "margin_pct": 24.1,
        "return_rate_pct": 3.8,
        "demand_trend": "stable",
        "ga4_sessions_wow_change_pct": 0.2,
        "top_subcategory": "Printer Supplies",
        "risk_flags": [],
        "signal": "MAINTAIN",
    },
]

SIGNAL_DESCRIPTIONS = {
    "SCALE": "Strong margins + growing demand -- increase ad spend and catalog investment",
    "MONITOR": "Good revenue but risk flag present -- watch closely, hold spend",
    "INVESTIGATE": "Declining trend -- diagnose root cause before next week",
    "FIX": "Multiple risk flags -- requires immediate action plan",
    "MAINTAIN": "Stable, no urgent action needed",
}


class CategoryGrowthAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="category-growth-agent", module_name="category-growth")

    def _categories_api_configured(self) -> bool:
        return bool(
            os.environ.get("CATEGORIES_API_URL")
            and os.environ.get("CATEGORIES_API_KEY")
            and os.environ.get("MARGIN_API_URL")
        )

    def fetch_live_data(self, date_from: str, date_to: str) -> dict:
        """Fetch category performance from Categories API + Margin API + Returns API.
        TODO: implement once APIs are available from backend team.
        """
        raise NotImplementedError("Categories API integration pending")

    def sample_summary(self) -> dict:
        total_revenue = sum(c["weekly_revenue_eur"] for c in SAMPLE_CATEGORIES)
        scale_categories = [c for c in SAMPLE_CATEGORIES if c["signal"] == "SCALE"]
        fix_categories = [c for c in SAMPLE_CATEGORIES if c["signal"] == "FIX"]
        investigate_categories = [c for c in SAMPLE_CATEGORIES if c["signal"] == "INVESTIGATE"]
        high_return_categories = [c for c in SAMPLE_CATEGORIES if c["return_rate_pct"] > 12.0]
        top_by_margin = sorted(SAMPLE_CATEGORIES, key=lambda c: c["margin_pct"], reverse=True)[:3]

        return {
            "headline": (
                f"Weekly GMV EUR{total_revenue:,.0f} | "
                f"{len(scale_categories)} categories to SCALE | "
                f"{len(fix_categories) + len(investigate_categories)} need attention"
            ),
            "sources_live": False,
            "total_weekly_revenue_eur": total_revenue,
            "total_active_products": sum(c["active_products"] for c in SAMPLE_CATEGORIES),
            "categories": SAMPLE_CATEGORIES,
            "signal_summary": {
                "SCALE": [c["name"] for c in scale_categories],
                "MONITOR": [c["name"] for c in SAMPLE_CATEGORIES if c["signal"] == "MONITOR"],
                "INVESTIGATE": [c["name"] for c in investigate_categories],
                "FIX": [c["name"] for c in fix_categories],
                "MAINTAIN": [c["name"] for c in SAMPLE_CATEGORIES if c["signal"] == "MAINTAIN"],
            },
            "signal_descriptions": SIGNAL_DESCRIPTIONS,
            "top_margin_categories": [
                {"name": c["name"], "margin_pct": c["margin_pct"]} for c in top_by_margin
            ],
            "high_return_risk": [
                {"name": c["name"], "return_rate_pct": c["return_rate_pct"]}
                for c in high_return_categories
            ],
            "note": "Sample data -- wire CATEGORIES_API_URL + MARGIN_API_URL for live data.",
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self._categories_api_configured():
            logger.info("category-growth-agent: fetching from Categories/Margin API")
            try:
                raw = self.fetch_live_data(date_from, date_to)
            except NotImplementedError:
                logger.warning(
                    "category-growth-agent: API integration not yet implemented, using sample data"
                )
                raw = self.sample_summary()
            except Exception as e:
                logger.warning("category-growth-agent: fetch failed: %s", e)
                raw = self.sample_summary()
        else:
            logger.warning("category-growth-agent: APIs not configured, using sample data")
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Category Growth Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace with 250,000+ products across 10+ categories. "
            "Your job is to rank categories by business health and give the marketing team a clear "
            "weekly action plan: which categories to scale spend on, which need investigation, "
            "which are at risk. "
            "Use these signals: revenue trend, margin %, return rate, demand trend (GA4 sessions). "
            "High margin + growing demand = SCALE. High return rate = risk. Declining 3+ weeks = FIX. "
            "Format: "
            "1. Category ranking table (revenue, margin, return rate, signal). "
            "2. Top 3 SCALE opportunities with specific action (budget, channel). "
            "3. Top 2 risk categories with root cause hypothesis. "
            "4. One category to deprioritize this week and why. "
            "Be specific with EUR amounts and percentages."
        )
        user = (
            f"Week of: {date_from}\n"
            f"Category performance data:\n{raw}\n\n"
            "Write the weekly category growth report."
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
            logger.error("category-growth-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Category growth summary -- model unavailable")

        return raw
