"""Supplier Intelligence Agent - co-marketing opportunities and supplier health.

Phase 1: sample data with realistic Ananas supplier distribution.
Phase 2: wires into Supplier API, Categories API, Orders API.

Runs weekly (Tuesday 08:00). Identifies suppliers with revenue potential but
low marketing investment, flags return-rate risks, and surfaces co-marketing
opportunities to the Commercial team.
"""

from __future__ import annotations

import os
from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

SAMPLE_SUPPLIERS: list[dict[str, Any]] = [
    {
        "name": "TechPro Distribution",
        "category": "Electronics",
        "weekly_revenue_eur": 48_200,
        "wow_revenue_change_pct": 12.4,
        "margin_pct": 16.8,
        "return_rate_pct": 7.2,
        "active_campaigns": 0,
        "marketing_spend_eur": 0,
        "catalog_size": 1_240,
        "content_quality_score": 72,
        "opportunity": "HIGH",
        "opportunity_reason": "Strong revenue growth, zero campaign investment -- prime co-marketing candidate",
        "recommended_action": "Propose co-funded Google Shopping campaign for Q2",
    },
    {
        "name": "SportStyle MK",
        "category": "Sports & Outdoors",
        "weekly_revenue_eur": 31_400,
        "wow_revenue_change_pct": 18.7,
        "margin_pct": 29.4,
        "return_rate_pct": 8.9,
        "active_campaigns": 1,
        "marketing_spend_eur": 800,
        "catalog_size": 892,
        "content_quality_score": 81,
        "opportunity": "HIGH",
        "opportunity_reason": "Best-performing sports supplier, underspending on marketing relative to revenue",
        "recommended_action": "Increase co-marketing budget, feature in spring Sports campaign",
    },
    {
        "name": "BeautyFirst Cosmetics",
        "category": "Beauty & Health",
        "weekly_revenue_eur": 22_100,
        "wow_revenue_change_pct": 9.2,
        "margin_pct": 42.1,
        "return_rate_pct": 3.8,
        "active_campaigns": 2,
        "marketing_spend_eur": 1_200,
        "catalog_size": 634,
        "content_quality_score": 88,
        "opportunity": "MEDIUM",
        "opportunity_reason": "High margin, low returns, good content -- scale existing partnership",
        "recommended_action": "Negotiate exclusive SKU deal for Q2 skincare push",
    },
    {
        "name": "HomeDecor Plus",
        "category": "Home & Garden",
        "weekly_revenue_eur": 18_700,
        "wow_revenue_change_pct": -4.1,
        "margin_pct": 24.6,
        "return_rate_pct": 5.1,
        "active_campaigns": 0,
        "marketing_spend_eur": 0,
        "catalog_size": 2_180,
        "content_quality_score": 58,
        "opportunity": "MEDIUM",
        "opportunity_reason": "Large catalog but revenue declining -- content quality is blocking visibility",
        "recommended_action": "Content improvement sprint: fix top 200 listings, then retest with campaign",
    },
    {
        "name": "FashionHub Balkans",
        "category": "Shoes & Clothing",
        "weekly_revenue_eur": 34_600,
        "wow_revenue_change_pct": -8.3,
        "margin_pct": 28.7,
        "return_rate_pct": 24.1,
        "active_campaigns": 1,
        "marketing_spend_eur": 2_100,
        "catalog_size": 4_820,
        "content_quality_score": 64,
        "opportunity": "LOW",
        "opportunity_reason": "RISK: 24.1% return rate is critical. Campaign spend is amplifying returns.",
        "recommended_action": "PAUSE campaigns. Investigate top return reasons. Fix sizing info first.",
    },
    {
        "name": "KidsWorld Toys",
        "category": "Toys & Kids",
        "weekly_revenue_eur": 14_200,
        "wow_revenue_change_pct": -5.8,
        "margin_pct": 27.4,
        "return_rate_pct": 4.2,
        "active_campaigns": 0,
        "marketing_spend_eur": 0,
        "catalog_size": 1_610,
        "content_quality_score": 76,
        "opportunity": "LOW",
        "opportunity_reason": "Seasonal decline (post-holiday). Good fundamentals, revisit for Easter push.",
        "recommended_action": "Hold. Propose Easter campaign in 3 weeks.",
    },
    {
        "name": "AutoParts Express",
        "category": "Automotive",
        "weekly_revenue_eur": 9_800,
        "wow_revenue_change_pct": -11.2,
        "margin_pct": 19.1,
        "return_rate_pct": 13.4,
        "active_campaigns": 0,
        "marketing_spend_eur": 0,
        "catalog_size": 3_940,
        "content_quality_score": 44,
        "opportunity": "LOW",
        "opportunity_reason": "RISK: declining revenue + high returns + poor content quality",
        "recommended_action": "Escalate to Commercial: supplier review meeting required",
    },
]


class SupplierIntelligenceAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="supplier-intelligence-agent", module_name="supplier-intelligence")

    def _supplier_api_configured(self) -> bool:
        return bool(os.environ.get("SUPPLIER_API_URL") and os.environ.get("SUPPLIER_API_KEY"))

    def fetch_live_data(self, date_from: str, date_to: str) -> dict:
        """Fetch from Supplier API + Orders API + Margin API.
        TODO: implement once backend APIs are available.
        """
        raise NotImplementedError("Supplier API integration pending")

    def sample_summary(self) -> dict:
        high_opps = [s for s in SAMPLE_SUPPLIERS if s["opportunity"] == "HIGH"]
        risk_suppliers = [s for s in SAMPLE_SUPPLIERS if s["return_rate_pct"] > 15.0]
        zero_campaign = [
            s
            for s in SAMPLE_SUPPLIERS
            if s["active_campaigns"] == 0 and s["opportunity"] in ("HIGH", "MEDIUM")
        ]
        total_revenue = sum(s["weekly_revenue_eur"] for s in SAMPLE_SUPPLIERS)
        total_campaign_spend = sum(s["marketing_spend_eur"] for s in SAMPLE_SUPPLIERS)

        return {
            "headline": (
                f"{len(high_opps)} HIGH co-marketing opportunities | "
                f"{len(risk_suppliers)} high-return risk suppliers | "
                f"{len(zero_campaign)} suppliers with no campaigns"
            ),
            "sources_live": False,
            "suppliers": SAMPLE_SUPPLIERS,
            "summary": {
                "total_suppliers_analysed": len(SAMPLE_SUPPLIERS),
                "total_weekly_revenue_eur": total_revenue,
                "total_marketing_spend_eur": total_campaign_spend,
                "marketing_to_revenue_pct": round(total_campaign_spend / total_revenue * 100, 2),
                "high_opportunity_suppliers": len(high_opps),
                "risk_suppliers": len(risk_suppliers),
                "zero_campaign_opportunity": len(zero_campaign),
            },
            "note": "Sample data -- wire SUPPLIER_API_URL + SUPPLIER_API_KEY for live data.",
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self._supplier_api_configured():
            logger.info("supplier-intelligence-agent: fetching from Supplier API")
            try:
                raw = self.fetch_live_data(date_from, date_to)
            except NotImplementedError:
                logger.warning(
                    "supplier-intelligence-agent: API not yet implemented, using sample data"
                )
                raw = self.sample_summary()
            except Exception as e:
                logger.warning("supplier-intelligence-agent: fetch failed: %s", e)
                raw = self.sample_summary()
        else:
            logger.warning("supplier-intelligence-agent: API not configured, using sample data")
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Supplier Intelligence Agent. Ananas is a marketplace -- "
            "supplier relationships are a direct revenue lever. Some suppliers have strong products "
            "and zero marketing investment: these are the highest-ROI co-marketing opportunities. "
            "Your job: surface the top co-marketing opportunities, flag high-return suppliers as "
            "risks, and give the Commercial team a specific weekly action list. "
            "Format: "
            "1. Top 3 co-marketing opportunities (supplier, rationale, specific action). "
            "2. Risk suppliers: high return rate -- campaign pause or investigation needed. "
            "3. Declining revenue suppliers -- flag to Commercial before they become a problem. "
            "4. One content gap to fix this week (supplier with poor content score). "
            "Be direct. The Commercial team needs supplier names and specific actions, not analysis."
        )
        user = (
            f"Week of: {date_from}\n"
            f"Supplier data:\n{raw}\n\n"
            "Write the weekly supplier intelligence report."
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
            logger.error("supplier-intelligence-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Supplier intelligence -- model unavailable")

        return raw
