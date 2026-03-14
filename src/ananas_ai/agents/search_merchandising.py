"""Search Merchandising Agent — internal site search quality monitoring.

Phase 1: sample data with realistic Ananas internal search patterns.
Phase 2: wires into internal Search API / GA4 site search events.

Runs daily (08:15). Monitors internal site search: zero-result rate,
failed search sessions, top queries with poor product match, and
search-to-conversion funnel. Internal search is the highest-leverage
conversion driver for a 250k-product marketplace.
"""

from __future__ import annotations

import os
from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

SAMPLE_ZERO_RESULT_QUERIES: list[dict[str, Any]] = [
    {
        "query": "iphone 16",
        "search_count": 842,
        "zero_result": True,
        "fix": "Add iPhone 16 listings or redirect to iPhone 15",
    },
    {
        "query": "ps5 kontroler",
        "search_count": 634,
        "zero_result": True,
        "fix": "Check PS5 controller catalog -- may be out of stock or miscategorised",
    },
    {
        "query": "samsung s24 ultra",
        "search_count": 521,
        "zero_result": True,
        "fix": "Verify Samsung S24 Ultra is listed with correct search tags",
    },
    {
        "query": "macbook m3",
        "search_count": 418,
        "zero_result": True,
        "fix": "Add MacBook M3 or create redirect to M2 with notice",
    },
    {
        "query": "gore tex jakna",
        "search_count": 312,
        "zero_result": False,
        "fix": "Low-relevance results -- improve Gore-Tex tagging in Clothing",
    },
    {
        "query": "smart watch evtini",
        "search_count": 289,
        "zero_result": False,
        "fix": "Budget smartwatch filter missing -- add price tier facet",
    },
    {
        "query": "tenisici za trcanje",
        "search_count": 276,
        "zero_result": False,
        "fix": "Macedonian query not matching translated attribute -- fix synonym mapping",
    },
]

SAMPLE_FAILED_SESSIONS: list[dict[str, Any]] = [
    {
        "query": "laptop za studenti",
        "searches": 1_240,
        "bounced_pct": 68.4,
        "issue": "Too many results, no filter for budget -- overwhelming UX",
    },
    {
        "query": "poklon za zena",
        "searches": 980,
        "bounced_pct": 71.2,
        "issue": "Gift search returns mixed categories -- add gift guide landing page",
    },
    {
        "query": "bela tehnika",
        "searches": 876,
        "bounced_pct": 62.1,
        "issue": "'White goods' search works but category page CVR is 0.3%",
    },
    {
        "query": "gaming stolici",
        "searches": 741,
        "bounced_pct": 54.8,
        "issue": "Gaming chairs exist but rank below office chairs in results",
    },
]

SAMPLE_SEARCH_FUNNEL: dict[str, Any] = {
    "total_search_sessions": 48_420,
    "zero_result_sessions": 6_240,
    "zero_result_rate_pct": 12.9,
    "zero_result_target_pct": 8.0,
    "search_to_product_view_pct": 61.4,
    "search_to_cart_pct": 8.2,
    "search_to_order_pct": 3.1,
    "organic_cvr_pct": 2.4,
    "search_cvr_pct": 3.1,
    "search_cvr_vs_organic_delta_pct": 0.7,
    "wow_zero_result_change_pct": 1.8,
}


class SearchMerchandisingAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="search-merchandising-agent", module_name="search-merchandising")

    def _search_api_configured(self) -> bool:
        return bool(
            os.environ.get("INTERNAL_SEARCH_API_URL") and os.environ.get("INTERNAL_SEARCH_API_KEY")
        )

    def fetch_live_data(self, date_from: str, date_to: str) -> dict:
        """Fetch from internal search API or GA4 site search events.
        TODO: implement once INTERNAL_SEARCH_API_URL is available.
        """
        raise NotImplementedError("Internal Search API integration pending")

    def sample_summary(self) -> dict:
        zero_result_count = sum(1 for q in SAMPLE_ZERO_RESULT_QUERIES if q["zero_result"])
        revenue_at_risk = SAMPLE_SEARCH_FUNNEL["zero_result_sessions"] * 71 * 0.031

        return {
            "headline": (
                f"Zero-result rate {SAMPLE_SEARCH_FUNNEL['zero_result_rate_pct']}% "
                f"(target <{SAMPLE_SEARCH_FUNNEL['zero_result_target_pct']}%) | "
                f"{zero_result_count} fixable zero-result queries | "
                f"~EUR{revenue_at_risk:,.0f}/week at risk"
            ),
            "sources_live": False,
            "search_funnel": SAMPLE_SEARCH_FUNNEL,
            "zero_result_queries": SAMPLE_ZERO_RESULT_QUERIES,
            "failed_sessions": SAMPLE_FAILED_SESSIONS,
            "revenue_at_risk_eur": round(revenue_at_risk, 0),
            "note": "Sample data -- wire INTERNAL_SEARCH_API_URL for live site search analytics.",
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self._search_api_configured():
            logger.info("search-merchandising-agent: fetching from Internal Search API")
            try:
                raw = self.fetch_live_data(date_from, date_to)
            except NotImplementedError:
                logger.warning(
                    "search-merchandising-agent: API not yet implemented, using sample data"
                )
                raw = self.sample_summary()
            except Exception as e:
                logger.warning("search-merchandising-agent: fetch failed: %s", e)
                raw = self.sample_summary()
        else:
            logger.warning(
                "search-merchandising-agent: Search API not configured, using sample data"
            )
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Search Merchandising Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace with 250,000+ products. Internal site search is the highest-leverage "
            "conversion driver -- customers who search convert 3x better than browsing customers. "
            "A zero-result rate above 8% represents direct revenue loss. "
            "Current zero-result rate is above target -- every percentage point above 8% costs revenue. "
            "Format: "
            "1. Search funnel health (zero-result rate vs target, search CVR vs organic CVR). "
            "2. Top 5 zero-result queries with specific fix for each (catalog gap vs tagging issue). "
            "3. Top 3 failed search sessions (high bounce rate -- UX or relevance problem). "
            "4. EUR revenue at risk from zero-result sessions. "
            "5. One fix to implement today (highest impact, lowest effort)."
        )
        user = (
            f"Date: {date_from}\n"
            f"Search data:\n{raw}\n\n"
            "Write the daily search merchandising report."
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
            logger.error("search-merchandising-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Search merchandising -- model unavailable")

        return raw
