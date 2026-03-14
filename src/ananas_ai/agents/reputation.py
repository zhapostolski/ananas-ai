"""Reputation Agent — Trustpilot, Google Business, review monitoring.

Phase 1: runs with known critical context + Claude analysis.
Phase 2: wires into Trustpilot API and Google Business API.

Critical known state:
- Trustpilot: 2.0 rating, profile NOT claimed — CRITICAL risk
- Google Business: status unknown, needs verification
"""

from __future__ import annotations

import os

import requests

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

TRUSTPILOT_KNOWN_STATE = {
    "rating": 2.0,
    "profile_claimed": False,
    "review_count": None,
    "status": "CRITICAL — profile unclaimed, 2.0 rating",
    "recommended_actions": [
        "Claim Trustpilot profile immediately (free).",
        "Set up automated review invitation emails post-purchase.",
        "Create response templates for negative reviews.",
        "Assign ownership for daily review monitoring.",
    ],
}


class ReputationAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="reputation-agent", module_name="reputation")

    def _trustpilot_configured(self) -> bool:
        return bool(os.environ.get("TRUSTPILOT_API_KEY"))

    def _fetch_trustpilot(self, date_from: str, date_to: str) -> dict:
        """Fetch live Trustpilot data via API.
        TODO: implement once API key is available (free business account).
        """
        api_key = os.environ["TRUSTPILOT_API_KEY"]
        business_unit_id = os.environ.get("TRUSTPILOT_BUSINESS_UNIT_ID", "")
        base = "https://api.trustpilot.com/v1"

        headers = {"apikey": api_key}

        summary = requests.get(
            f"{base}/business-units/{business_unit_id}/reviews/summary",
            headers=headers,
            timeout=30,
        ).json()

        recent = requests.get(
            f"{base}/business-units/{business_unit_id}/reviews",
            headers=headers,
            params={"startDateTime": date_from, "perPage": "20"},
            timeout=30,
        ).json()

        return {
            "rating": summary.get("starsAverage", 0),
            "total_reviews": summary.get("numberOfReviews", {}).get("total", 0),
            "recent_reviews": recent.get("reviews", []),
            "date_from": date_from,
        }

    def sample_summary(self) -> dict:
        return {
            "headline": "Reputation — CRITICAL: Trustpilot 2.0, profile unclaimed",
            "trustpilot": TRUSTPILOT_KNOWN_STATE,
            "google_business": {
                "status": "unknown — not yet integrated",
            },
            "sources_live": [],
            "overall_risk": "CRITICAL",
            "priority_action": "Claim Trustpilot profile today — this is costing conversions.",
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self._trustpilot_configured():
            logger.info("reputation-agent: fetching live Trustpilot data")
            try:
                raw = self._fetch_trustpilot(date_from, date_to)
            except Exception as e:
                logger.warning("reputation-agent: Trustpilot fetch failed: %s", e)
                raw = self.sample_summary()
        else:
            logger.warning("reputation-agent: Trustpilot not configured, using known state")
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Reputation Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace. "
            "CRITICAL KNOWN ISSUE: Trustpilot rating is 2.0 and the profile is NOT claimed. "
            "This is actively hurting conversion rates. "
            "Your job: monitor review sentiment, identify themes in negative reviews, "
            "track rating trends, flag urgent issues, and recommend response actions. "
            "Format: overall risk level (OK/WARNING/CRITICAL), key themes, "
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
            raw["analysis"] = raw.get("headline", "Reputation summary — model unavailable")

        return raw
