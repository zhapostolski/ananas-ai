"""Reputation Agent -- Google Business Profile reviews and rating monitoring.

Phase 1: runs with known critical context + Claude analysis.
Phase 2: wires into Google Business Profile API for live review data.

Critical known state:
- Google Business Profile rating: unknown, needs verification
- Review response rate: unknown, likely very low
"""

from __future__ import annotations

from ananas_ai.agents.base import BaseAgent
from ananas_ai.integrations.google_business import GoogleBusinessIntegration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)


class ReputationAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="reputation-agent", module_name="reputation")
        self.gbp = GoogleBusinessIntegration()

    def sample_summary(self) -> dict:
        return {
            "headline": "Reputation -- Google Business Profile not yet integrated",
            "google_business": {
                "average_rating": None,
                "total_reviews": None,
                "unanswered_reviews": None,
                "status": "Not configured -- set GBP_ACCOUNT_ID and GBP_LOCATION_ID",
            },
            "sources_live": [],
            "overall_risk": "UNKNOWN",
            "priority_action": (
                "Set up Google Business Profile API access to enable live review monitoring."
            ),
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self.gbp.is_configured():
            logger.info("reputation-agent: fetching live Google Business Profile data")
            try:
                raw = self.gbp.safe_fetch(date_from, date_to)
            except Exception as e:
                logger.warning("reputation-agent: GBP fetch failed: %s", e)
                raw = self.sample_summary()
        else:
            logger.warning(
                "reputation-agent: Google Business Profile not configured, using known state"
            )
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Reputation Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace. "
            "Your job: monitor Google Business Profile reviews and rating, identify themes "
            "in negative reviews, track rating trends, flag urgent issues, and recommend "
            "response actions for the team. "
            "Format: overall risk level (OK/WARNING/CRITICAL), key themes from reviews, "
            "reviews needing immediate response, one priority action."
        )
        user = f"Date: {date_from}\nReputation data:\n{raw}\n\nWrite the daily reputation briefing."

        try:
            result = call_model(route.model, system, user)
            raw["analysis"] = result["text"]
            raw["model_used"] = result["model_used"]
            raw["fallback"] = result["fallback"]
            raw["tokens_in"] = result["tokens_in"]
            raw["tokens_out"] = result["tokens_out"]
            raw["estimated_cost"] = result["estimated_cost"]
        except Exception as e:
            logger.error("reputation-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Reputation summary -- model unavailable")

        return raw
