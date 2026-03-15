"""Influencer & Partnership Agent - creator ROI tracking and co-marketing.

Phase 1: sample data with realistic Ananas influencer program state.
Phase 2: wires into GA4 UTM attribution + CRM email platform.

Runs weekly. Tracks influencer campaign ROI, creator scoring, affiliate
revenue, and surfaces emerging creator opportunities in MK/RS/BA market.
"""

from __future__ import annotations

from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.integrations.ga4 import GA4Integration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

SAMPLE_ACTIVE_CAMPAIGNS: list[dict[str, Any]] = [
    {
        "creator": "@lifestyle_mk",
        "platform": "Instagram",
        "followers": 84_200,
        "campaign": "Spring Fashion",
        "spend_eur": 1_400,
        "reach": 62_400,
        "attributed_clicks": 1_840,
        "attributed_orders": 74,
        "attributed_revenue_eur": 4_810,
        "roas": 3.4,
        "cvr_pct": 4.0,
        "status": "active",
        "verdict": "PERFORMING",
    },
    {
        "creator": "@tech_review_mk",
        "platform": "YouTube",
        "followers": 124_000,
        "campaign": "Electronics Q1",
        "spend_eur": 2_800,
        "reach": 98_200,
        "attributed_clicks": 2_140,
        "attributed_orders": 41,
        "attributed_revenue_eur": 4_920,
        "roas": 1.8,
        "cvr_pct": 1.9,
        "status": "active",
        "verdict": "UNDERPERFORMING",
    },
    {
        "creator": "@homestyle_balkan",
        "platform": "TikTok",
        "followers": 47_800,
        "campaign": "Home Decor",
        "spend_eur": 800,
        "reach": 112_400,
        "attributed_clicks": 3_820,
        "attributed_orders": 118,
        "attributed_revenue_eur": 6_140,
        "roas": 7.7,
        "cvr_pct": 3.1,
        "status": "active",
        "verdict": "TOP_PERFORMER",
    },
]

SAMPLE_AFFILIATE_SUMMARY: dict[str, Any] = {
    "active_affiliates": 12,
    "total_weekly_revenue_eur": 8_420,
    "total_commissions_eur": 842,
    "avg_commission_pct": 10.0,
    "top_affiliate": "couponsmk.com",
    "top_affiliate_revenue_eur": 3_210,
    "note": "Affiliate program is coupon-heavy -- 60% of affiliate revenue is coupon-driven",
}

SAMPLE_OPPORTUNITIES: list[dict[str, Any]] = [
    {
        "creator": "@fitness_mk_official",
        "platform": "Instagram",
        "followers": 38_400,
        "niche": "Fitness/Sports",
        "engagement_rate_pct": 6.8,
        "rationale": "High engagement in Sports category which is accelerating demand. No current partnership.",
    },
    {
        "creator": "@kuvanje_makedonija",
        "platform": "TikTok",
        "followers": 91_200,
        "niche": "Food & Kitchen",
        "engagement_rate_pct": 8.2,
        "rationale": "Kitchen category has good margin (24%). Food TikTok is fast-growing in MK market.",
    },
]


class InfluencerPartnershipAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="influencer-partnership-agent", module_name="influencer-partnership")
        self.ga4 = GA4Integration()

    def _has_live_sources(self) -> bool:
        return self.ga4.is_configured()

    def fetch_live_data(self, date_from: str, date_to: str) -> dict:
        ga4_data = self.ga4.safe_fetch(date_from, date_to)
        return {
            "sources_live": True,
            "ga4": ga4_data,
            "active_campaigns": SAMPLE_ACTIVE_CAMPAIGNS,
            "affiliate_summary": SAMPLE_AFFILIATE_SUMMARY,
            "opportunities": SAMPLE_OPPORTUNITIES,
            "note": "GA4 live. Per-creator attribution requires UTM tagging discipline.",
        }

    def sample_summary(self) -> dict:
        total_spend = sum(c["spend_eur"] for c in SAMPLE_ACTIVE_CAMPAIGNS)
        total_revenue = sum(c["attributed_revenue_eur"] for c in SAMPLE_ACTIVE_CAMPAIGNS)
        blended_roas = round(total_revenue / total_spend, 1) if total_spend else 0
        top = max(SAMPLE_ACTIVE_CAMPAIGNS, key=lambda c: c["roas"])
        underperforming = [c for c in SAMPLE_ACTIVE_CAMPAIGNS if c["verdict"] == "UNDERPERFORMING"]

        return {
            "headline": (
                f"Influencer blended ROAS {blended_roas}x | "
                f"Top: {top['creator']} ({top['roas']}x) | "
                f"{len(underperforming)} underperforming campaign(s)"
            ),
            "sources_live": False,
            "active_campaigns": SAMPLE_ACTIVE_CAMPAIGNS,
            "affiliate_summary": SAMPLE_AFFILIATE_SUMMARY,
            "opportunities": SAMPLE_OPPORTUNITIES,
            "summary": {
                "total_influencer_spend_eur": total_spend,
                "total_attributed_revenue_eur": total_revenue,
                "blended_roas": blended_roas,
                "active_campaigns": len(SAMPLE_ACTIVE_CAMPAIGNS),
            },
            "note": "Sample data -- wire GA4 UTM attribution for live influencer tracking.",
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self._has_live_sources():
            logger.info("influencer-partnership-agent: using live GA4 attribution")
            raw = self.fetch_live_data(date_from, date_to)
        else:
            logger.warning("influencer-partnership-agent: GA4 not configured, using sample data")
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Influencer & Partnership Agent. Ananas is North Macedonia's "
            "largest e-commerce marketplace. You track creator campaigns and affiliate partnerships. "
            "The MK/RS/BA influencer market is small -- a 50k follower local creator can outperform "
            "a 500k international one because of audience relevance. "
            "Format: "
            "1. Active campaign performance table (creator, spend, ROAS, verdict). "
            "2. Top performer highlight + why it's working. "
            "3. Underperforming campaigns: pause recommendation or fix. "
            "4. Affiliate revenue summary + coupon dependency note. "
            "5. One new creator opportunity to pursue this week."
        )
        user = (
            f"Week of: {date_from}\n"
            f"Influencer & affiliate data:\n{raw}\n\n"
            "Write the weekly influencer & partnership report."
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
            logger.error("influencer-partnership-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Influencer & partnership -- model unavailable")

        return raw
