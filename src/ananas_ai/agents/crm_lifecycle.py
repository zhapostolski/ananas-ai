"""CRM & Lifecycle Agent — Sales Snap + email automation health.

Phase 1: runs on sample data with Claude analysis.
Phase 2: wires directly into Sales Snap REST API when credentials are available.

Sales Snap is Ananas's CRM platform (regional Balkan provider).
API docs to be requested from sales-snap.com support.
"""

from __future__ import annotations

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

# Known context about Ananas CRM state (from project brief)
KNOWN_GAPS = [
    "No cart recovery automation live — estimated 15-25% revenue recovery opportunity.",
    "No churn prevention flow — at-risk customers not being re-engaged.",
    "No post-purchase lifecycle sequence (upsell, review request, loyalty).",
    "Birthday/anniversary journeys blocked on profile field capture.",
    "Welcome series not tested for conversion rate.",
    "Heavy coupon dependency masks real email-driven revenue — segment needs isolation.",
]

JOURNEYS = {
    "cart-recovery": {"status": "not_live", "priority": "critical", "est_impact": "high"},
    "welcome-series": {"status": "not_live", "priority": "high", "est_impact": "medium"},
    "churn-prevention": {"status": "not_live", "priority": "high", "est_impact": "high"},
    "post-purchase": {"status": "not_live", "priority": "medium", "est_impact": "medium"},
    "win-back": {"status": "not_live", "priority": "medium", "est_impact": "medium"},
    "birthday": {"status": "not_live", "priority": "low", "est_impact": "low"},
}


class CRMLifecycleAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="crm-lifecycle-agent", module_name="crm-lifecycle")

    def _sales_snap_configured(self) -> bool:
        import os

        return bool(os.environ.get("SALES_SNAP_API_KEY"))

    def _fetch_sales_snap(self, date_from: str, date_to: str) -> dict:
        """Fetch live data from Sales Snap API.
        TODO: implement once API credentials are available.
        """
        import os

        import requests

        api_key = os.environ["SALES_SNAP_API_KEY"]
        base_url = os.environ.get("SALES_SNAP_BASE_URL", "https://app.sales-snap.com/api/v1")

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        campaigns = requests.get(
            f"{base_url}/campaigns",
            headers=headers,
            params={"date_from": date_from, "date_to": date_to},
            timeout=30,
        ).json()

        return {
            "campaigns": campaigns.get("data", []),
            "date_from": date_from,
            "date_to": date_to,
        }

    def sample_summary(self) -> dict:
        return {
            "headline": "CRM & Lifecycle — no live data (Sales Snap not configured)",
            "journeys": JOURNEYS,
            "known_gaps": KNOWN_GAPS,
            "crm_platform": "Sales Snap",
            "automations_live": 0,
            "automations_total": len(JOURNEYS),
            "priority_action": "Activate cart recovery automation immediately — highest revenue impact.",
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self._sales_snap_configured():
            logger.info("crm-lifecycle-agent: fetching from Sales Snap")
            try:
                raw = self._fetch_sales_snap(date_from, date_to)
            except Exception as e:
                logger.warning("crm-lifecycle-agent: Sales Snap fetch failed: %s", e)
                raw = self.sample_summary()
        else:
            logger.warning("crm-lifecycle-agent: Sales Snap not configured, using known gaps")
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI CRM & Lifecycle Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace using Sales Snap as their CRM platform. "
            "Your job is to monitor lifecycle automation health, email campaign performance, "
            "cart recovery rates, churn signals, and repeat purchase trends. "
            "Critical context: NO lifecycle automations are currently live. "
            "Cart recovery, churn prevention, welcome series, and post-purchase flows are all missing. "
            "Heavy coupon dependency masks real email-driven revenue. "
            "Format: status per journey (LIVE/MISSING/BROKEN), revenue impact estimates, "
            "one immediate action item."
        )
        user = f"Date: {date_from}\nCRM data:\n{raw}\n\nWrite the daily CRM & lifecycle briefing."

        try:
            result = call_model(route.model, system, user)
            raw["analysis"] = result["text"]
            raw["model_used"] = result["model_used"]
            raw["fallback"] = result["fallback"]
            raw["tokens_in"] = result["tokens_in"]
            raw["tokens_out"] = result["tokens_out"]
            raw["estimated_cost"] = result["estimated_cost"]
        except Exception as e:
            logger.error("crm-lifecycle-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "CRM summary — model unavailable")

        return raw
