"""Demand Forecasting Agent — demand spike detection and seasonal patterns.

Phase 1: sample data with realistic Ananas demand signals.
Phase 2: wires into GA4 (already live), Search Console, and Categories API.

Runs weekly (Wednesday 08:00). Identifies rising demand before it peaks so
marketing can prepare campaigns and Commercial can ensure stock is in place.
"""

from __future__ import annotations

from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.integrations.ga4 import GA4Integration
from ananas_ai.integrations.search_console import SearchConsoleIntegration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

SAMPLE_DEMAND_SIGNALS: list[dict[str, Any]] = [
    {
        "category": "Sports & Outdoors",
        "signal": "ACCELERATING",
        "ga4_sessions_wow_change_pct": 14.2,
        "search_console_query_lift_pct": 18.6,
        "top_queries": ["bicikl", "trekking oprema", "fitnes doma", "roleri"],
        "wishlist_growth_pct": 22.1,
        "strength": "strong",
        "forecast_next_2w": "Demand expected to peak in 10-14 days (spring onset)",
        "action": "Launch Sports campaign next Monday, prepare 15% bid increase on cycling",
    },
    {
        "category": "Garden & Outdoor Living",
        "signal": "RISING",
        "ga4_sessions_wow_change_pct": 9.8,
        "search_console_query_lift_pct": 12.3,
        "top_queries": ["gradinski namestaj", "gradinska pikavac", "cvekinja", "sejalka"],
        "wishlist_growth_pct": 16.4,
        "strength": "moderate",
        "forecast_next_2w": "Seasonal spring peak approaching (MKD payday cycle: 15th)",
        "action": "Prepare garden furniture campaign for 10-12 March payday window",
    },
    {
        "category": "Beauty & Skincare",
        "signal": "ACCELERATING",
        "ga4_sessions_wow_change_pct": 8.3,
        "search_console_query_lift_pct": 11.2,
        "top_queries": ["serum za lice", "spf krema", "eye cream"],
        "wishlist_growth_pct": 19.7,
        "strength": "moderate",
        "forecast_next_2w": "Spring skincare refresh — consistent 6-week rising trend",
        "action": "Feature skincare brands with high wishlist-to-cart potential in newsletter",
    },
    {
        "category": "Electronics / Air Conditioning",
        "signal": "EARLY_SIGNAL",
        "ga4_sessions_wow_change_pct": 4.1,
        "search_console_query_lift_pct": 6.8,
        "top_queries": ["klima uredaj", "inverter klima", "mobile klima"],
        "wishlist_growth_pct": 31.2,
        "strength": "early",
        "forecast_next_2w": "Wishlist buildup is unusually high -- demand will spike in 3-4 weeks",
        "action": "Alert Commercial to check AC stock levels; begin supplier conversations now",
    },
    {
        "category": "Toys & Kids",
        "signal": "DECLINING",
        "ga4_sessions_wow_change_pct": -6.1,
        "search_console_query_lift_pct": -4.2,
        "top_queries": [],
        "wishlist_growth_pct": -3.8,
        "strength": "weak",
        "forecast_next_2w": "Post-holiday demand trough. Expect recovery around Easter.",
        "action": "Hold spend. Brief reactivation opportunity in 3 weeks (Easter gifts).",
    },
]

SAMPLE_SEASONAL_CALENDAR: list[dict[str, Any]] = [
    {
        "event": "Spring cleaning season",
        "starts": "2026-03-20",
        "relevant_categories": ["Home & Garden", "Cleaning", "Storage"],
        "confidence": "high",
    },
    {
        "event": "MK payday cycle",
        "starts": "2026-03-15",
        "relevant_categories": ["All"],
        "confidence": "high",
    },
    {
        "event": "Easter (MK)",
        "starts": "2026-04-12",
        "relevant_categories": ["Toys & Kids", "Home Decor", "Food & Grocery"],
        "confidence": "high",
    },
    {
        "event": "School season prep",
        "starts": "2026-08-15",
        "relevant_categories": ["Stationery", "Toys & Kids", "Electronics"],
        "confidence": "medium",
    },
]


class DemandForecastingAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="demand-forecasting-agent", module_name="demand-forecasting")
        self.ga4 = GA4Integration()
        self.search_console = SearchConsoleIntegration()

    def _has_live_sources(self) -> bool:
        return self.ga4.is_configured() or self.search_console.is_configured()

    def fetch_live_data(self, date_from: str, date_to: str) -> dict:
        """Combine GA4 session trends with Search Console query trends per category.
        Phase 2: add Categories API for internal search signals.
        """
        ga4_data = self.ga4.safe_fetch(date_from, date_to)
        sc_data = self.search_console.safe_fetch(date_from, date_to)
        return {
            "sources_live": True,
            "ga4": ga4_data,
            "search_console": sc_data,
            "demand_signals": [],
            "note": "Live category-level demand analysis requires Categories API (pending).",
        }

    def sample_summary(self) -> dict:
        rising = [
            s
            for s in SAMPLE_DEMAND_SIGNALS
            if s["signal"] in ("RISING", "ACCELERATING", "EARLY_SIGNAL")
        ]
        declining = [s for s in SAMPLE_DEMAND_SIGNALS if s["signal"] == "DECLINING"]
        top_action = next(
            (s["action"] for s in SAMPLE_DEMAND_SIGNALS if s["signal"] == "ACCELERATING"), ""
        )

        return {
            "headline": (
                f"{len(rising)} categories rising | "
                f"{len(declining)} declining | "
                f"Top signal: {SAMPLE_DEMAND_SIGNALS[0]['category']} +{SAMPLE_DEMAND_SIGNALS[0]['ga4_sessions_wow_change_pct']}% sessions"
            ),
            "sources_live": False,
            "demand_signals": SAMPLE_DEMAND_SIGNALS,
            "seasonal_calendar": SAMPLE_SEASONAL_CALENDAR,
            "summary": {
                "rising_categories": len(rising),
                "declining_categories": len(declining),
                "top_opportunity": SAMPLE_DEMAND_SIGNALS[0]["category"],
                "recommended_immediate_action": top_action,
            },
            "note": "Sample data -- GA4 is live; wire CATEGORIES_API_URL for category-level demand breakdown.",
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self._has_live_sources():
            logger.info("demand-forecasting-agent: using live GA4 + Search Console")
            raw = self.fetch_live_data(date_from, date_to)
            if not raw.get("demand_signals"):
                raw = self.sample_summary()
                raw["sources_live"] = False
        else:
            logger.warning("demand-forecasting-agent: no live sources, using sample data")
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Demand Forecasting Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace with 250k+ products. "
            "Your job is to identify rising demand BEFORE it peaks -- giving marketing 1-2 weeks "
            "lead time to launch campaigns and giving Commercial time to ensure stock is in place. "
            "Ananas is in the Balkans market. Seasonal signals: spring starts mid-March, "
            "payday cycles are the 15th of each month, Easter is a significant gifting event. "
            "Format: "
            "1. Top 3 rising demand signals (category, signal strength, what to do this week). "
            "2. 2-week seasonal forecast (events coming up, which categories to prepare). "
            "3. One stock alert if any wishlist-demand gap is large. "
            "4. One category to deprioritize spend this week (declining). "
            "Be specific: name categories, suggest campaign timing in days, flag stock risks clearly."
        )
        user = f"Week of: {date_from}\nDemand signals:\n{raw}\n\nWrite the weekly demand forecast."

        try:
            result = call_model(route.model, system, user)
            raw["analysis"] = result["text"]
            raw["model_used"] = result["model_used"]
            raw["fallback"] = result["fallback"]
            raw["tokens_in"] = result["tokens_in"]
            raw["tokens_out"] = result["tokens_out"]
            raw["estimated_cost"] = result["estimated_cost"]
        except Exception as e:
            logger.error("demand-forecasting-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Demand forecast -- model unavailable")

        return raw
