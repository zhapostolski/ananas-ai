"""Competitor Intelligence Agent — lightweight competitor monitoring.

Uses free/existing sources only:
- Meta Ad Library (free public API) -- competitor active ads + estimated spend
- Google Auction Insights (already in our Google Ads data) -- impression share vs competitors
- Public review ratings (Trustpilot/Google, public endpoints)

Phase 2: add SEMrush/Ahrefs once that key is acquired for organic-merchandising-agent.

Runs daily (promo scan) + weekly (strategic summary).
"""

from __future__ import annotations

import os
from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

# Known Ananas competitors in the Balkans region.
KNOWN_COMPETITORS: list[dict[str, Any]] = [
    {"name": "eMAG (BG/RS)", "domain": "emag.bg", "region": "Balkans", "tier": "primary"},
    {"name": "Shoppster", "domain": "shoppster.com", "region": "MK/RS", "tier": "primary"},
    {"name": "Neptun", "domain": "neptun.mk", "region": "MK", "tier": "primary"},
    {"name": "SetMK", "domain": "set.mk", "region": "MK", "tier": "secondary"},
    {
        "name": "Amazon.de",
        "domain": "amazon.de",
        "region": "DE/EU cross-border",
        "tier": "indirect",
    },
]

# Sample Meta Ad Library data -- what Ananas competitors are running.
SAMPLE_COMPETITOR_ADS: list[dict[str, Any]] = [
    {
        "competitor": "eMAG (BG/RS)",
        "active_ad_count": 47,
        "ad_formats": ["image", "video", "carousel"],
        "primary_message": "Free delivery on orders over 30 EUR",
        "promo_detected": True,
        "promo_description": "Spring sale -- up to 40% off electronics",
        "estimated_weekly_spend_eur": 12_400,
        "wow_spend_change_pct": 28.0,
        "urgency": "HIGH -- major spend increase, active promotion",
    },
    {
        "competitor": "Shoppster",
        "active_ad_count": 18,
        "ad_formats": ["image", "carousel"],
        "primary_message": "Exclusive brands, fast delivery",
        "promo_detected": False,
        "promo_description": None,
        "estimated_weekly_spend_eur": 3_200,
        "wow_spend_change_pct": -5.0,
        "urgency": "LOW",
    },
    {
        "competitor": "Neptun",
        "active_ad_count": 12,
        "ad_formats": ["image"],
        "primary_message": "Electronics specialist, 3-year warranty",
        "promo_detected": True,
        "promo_description": "Weekend flash sale on TVs and laptops",
        "estimated_weekly_spend_eur": 2_100,
        "wow_spend_change_pct": 15.0,
        "urgency": "MEDIUM -- flash sale this weekend",
    },
]

# Sample Google Auction Insights -- our impression share vs competitors.
SAMPLE_AUCTION_INSIGHTS: list[dict[str, Any]] = [
    {
        "competitor": "eMAG (BG/RS)",
        "our_impression_share_pct": 18.4,
        "their_impression_share_pct": 34.2,
        "overlap_rate_pct": 41.8,
        "outranking_share_pct": 22.1,
        "position_above_rate_pct": 61.4,
    },
    {
        "competitor": "Neptun",
        "our_impression_share_pct": 18.4,
        "their_impression_share_pct": 28.7,
        "overlap_rate_pct": 31.2,
        "outranking_share_pct": 38.4,
        "position_above_rate_pct": 44.8,
    },
    {
        "competitor": "Shoppster",
        "our_impression_share_pct": 18.4,
        "their_impression_share_pct": 11.3,
        "overlap_rate_pct": 18.6,
        "outranking_share_pct": 62.1,
        "position_above_rate_pct": 28.4,
    },
]

# Public review comparison.
SAMPLE_REVIEW_COMPARISON: list[dict[str, Any]] = [
    {"competitor": "Ananas", "trustpilot_rating": 2.0, "review_count": 148, "trend": "declining"},
    {
        "competitor": "eMAG (BG/RS)",
        "trustpilot_rating": 3.8,
        "review_count": 4_210,
        "trend": "stable",
    },
    {
        "competitor": "Shoppster",
        "trustpilot_rating": 3.2,
        "review_count": 312,
        "trend": "improving",
    },
    {"competitor": "Neptun", "trustpilot_rating": 4.1, "review_count": 891, "trend": "stable"},
]


class CompetitorIntelligenceAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="competitor-intelligence-agent",
            module_name="competitor-intelligence",
        )

    def _meta_ad_library_configured(self) -> bool:
        return bool(os.environ.get("META_ACCESS_TOKEN"))

    def _google_ads_configured(self) -> bool:
        return bool(os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"))

    def fetch_live_data(self, date_from: str, date_to: str) -> dict:
        """Fetch from Meta Ad Library + Google Auction Insights.
        Meta Ad Library: uses existing META_ACCESS_TOKEN.
        Auction Insights: uses existing GoogleAdsIntegration.
        TODO: implement Meta Ad Library search for competitor ads.
        """
        raise NotImplementedError("Meta Ad Library and Auction Insights integration pending")

    def sample_summary(self) -> dict:
        active_promos = [c for c in SAMPLE_COMPETITOR_ADS if c["promo_detected"]]
        high_urgency = [c for c in SAMPLE_COMPETITOR_ADS if c["urgency"].startswith("HIGH")]
        our_rating = next(
            (
                r["trustpilot_rating"]
                for r in SAMPLE_REVIEW_COMPARISON
                if r["competitor"] == "Ananas"
            ),
            2.0,
        )
        avg_competitor_rating = round(
            sum(
                r["trustpilot_rating"]
                for r in SAMPLE_REVIEW_COMPARISON
                if r["competitor"] != "Ananas"
            )
            / len([r for r in SAMPLE_REVIEW_COMPARISON if r["competitor"] != "Ananas"]),
            1,
        )

        return {
            "headline": (
                f"{len(active_promos)} competitor promos active | "
                f"{len(high_urgency)} HIGH urgency | "
                f"Trustpilot gap: Ananas {our_rating} vs competitors avg {avg_competitor_rating}"
            ),
            "sources_live": False,
            "competitors": KNOWN_COMPETITORS,
            "ad_intelligence": SAMPLE_COMPETITOR_ADS,
            "auction_insights": SAMPLE_AUCTION_INSIGHTS,
            "review_comparison": SAMPLE_REVIEW_COMPARISON,
            "summary": {
                "active_competitor_promos": len(active_promos),
                "high_urgency_signals": len(high_urgency),
                "our_trustpilot_rating": our_rating,
                "avg_competitor_trustpilot_rating": avg_competitor_rating,
                "reputation_gap": round(avg_competitor_rating - our_rating, 1),
            },
            "note": (
                "Sample data -- Meta Ad Library integration pending (META_ACCESS_TOKEN needed). "
                "Auction Insights pending Google Ads credential setup."
            ),
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self._meta_ad_library_configured() or self._google_ads_configured():
            logger.info("competitor-intelligence-agent: fetching live competitor data")
            try:
                raw = self.fetch_live_data(date_from, date_to)
            except NotImplementedError:
                logger.warning(
                    "competitor-intelligence-agent: integration not yet implemented, using sample data"
                )
                raw = self.sample_summary()
            except Exception as e:
                logger.warning("competitor-intelligence-agent: fetch failed: %s", e)
                raw = self.sample_summary()
        else:
            logger.warning(
                "competitor-intelligence-agent: no sources configured, using sample data"
            )
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Competitor Intelligence Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace. You monitor competitor activity using Meta Ad Library and "
            "Google Auction Insights. "
            "CRITICAL CONTEXT: Ananas has a Trustpilot rating of 2.0 -- significantly below all "
            "major competitors. eMAG is the primary regional threat with higher spend and better reputation. "
            "Your job: identify competitor promotions that require an Ananas response, "
            "flag impression share losses, and highlight the reputation gap. "
            "Format: "
            "1. Active competitor promotions requiring response (urgent first). "
            "2. Auction Insights summary -- where we are losing/winning impression share. "
            "3. Reputation gap analysis with urgency score. "
            "4. Recommended counter-actions (max 3, specific and actionable). "
            "Do not recommend matching competitor discounts without margin analysis."
        )
        user = (
            f"Date: {date_from}\n"
            f"Competitor intelligence data:\n{raw}\n\n"
            "Write the competitor intelligence brief."
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
            logger.error("competitor-intelligence-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Competitor intelligence -- model unavailable")

        return raw
