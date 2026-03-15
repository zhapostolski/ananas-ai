"""Customer Segmentation Agent - RFM segmentation, LTV prediction, churn risk.

Phase 1: sample data with realistic Ananas customer distribution.
Phase 2: wires into Orders API + Sales Snap CRM for real RFM computation.

Runs weekly (Monday 07:00). Outputs customer segment distribution, week-over-week
drift, and churn risk alerts for high-value customers.

This is a critical enabler for reducing coupon dependency: it identifies which
customers actually need an incentive vs. which would purchase without one.
"""

from __future__ import annotations

import os
from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

# Realistic RFM segment distribution for an established Balkan marketplace.
# Based on industry benchmarks: healthy marketplaces have ~15-20% VIP,
# ~25% Active, ~20% At-Risk, ~30% Churned, ~10% New.
SAMPLE_SEGMENTS: dict[str, dict[str, Any]] = {
    "vip": {
        "label": "VIP",
        "definition": "Purchased 4+ times in 90 days, high AOV",
        "customer_count": 18_420,
        "pct_of_base": 12.8,
        "avg_ltv_eur": 892.0,
        "avg_order_value_eur": 118.0,
        "avg_orders_per_year": 7.6,
        "churn_risk": "low",
        "coupon_needed": False,
        "recommended_action": "Loyalty rewards, early access to new products",
        "wow_change_pct": -0.4,
    },
    "active": {
        "label": "Active",
        "definition": "Purchased 1-3 times in 90 days",
        "customer_count": 34_810,
        "pct_of_base": 24.2,
        "avg_ltv_eur": 312.0,
        "avg_order_value_eur": 74.0,
        "avg_orders_per_year": 4.2,
        "churn_risk": "low",
        "coupon_needed": False,
        "recommended_action": "Cross-sell adjacent categories, loyalty nudge",
        "wow_change_pct": 1.2,
    },
    "at_risk": {
        "label": "At Risk",
        "definition": "Purchased in last 90-180 days, declining frequency",
        "customer_count": 28_640,
        "pct_of_base": 19.9,
        "avg_ltv_eur": 198.0,
        "avg_order_value_eur": 62.0,
        "avg_orders_per_year": 3.2,
        "churn_risk": "medium",
        "coupon_needed": True,
        "recommended_action": "Win-back campaign with 10-15% targeted discount",
        "wow_change_pct": 2.1,
    },
    "churned": {
        "label": "Churned",
        "definition": "No purchase in 180+ days",
        "customer_count": 47_920,
        "pct_of_base": 33.3,
        "avg_ltv_eur": 94.0,
        "avg_order_value_eur": 51.0,
        "avg_orders_per_year": 0.0,
        "churn_risk": "high",
        "coupon_needed": True,
        "recommended_action": "Re-engagement flow, 20% reactivation discount for high LTV churned",
        "wow_change_pct": 0.8,
    },
    "new": {
        "label": "New",
        "definition": "First purchase in last 30 days",
        "customer_count": 13_940,
        "pct_of_base": 9.7,
        "avg_ltv_eur": 48.0,
        "avg_order_value_eur": 68.0,
        "avg_orders_per_year": None,
        "churn_risk": "medium",
        "coupon_needed": False,
        "recommended_action": "Welcome series, second-purchase nudge within 14 days",
        "wow_change_pct": 3.4,
    },
}

SAMPLE_CHURN_ALERTS: list[dict[str, Any]] = [
    {
        "segment": "vip_approaching_churn",
        "description": "VIP customers with no purchase in 45-60 days (unusual for VIP)",
        "customer_count": 842,
        "avg_ltv_eur": 1240.0,
        "revenue_at_risk_eur": 1_044_080,
        "recommended_action": "Personal outreach + exclusive offer within 48 hours",
        "urgency": "critical",
    },
    {
        "segment": "active_to_at_risk_migration",
        "description": "Active customers who haven't purchased in 30 days (sliding to At Risk)",
        "customer_count": 2_180,
        "avg_ltv_eur": 287.0,
        "revenue_at_risk_eur": 625_660,
        "recommended_action": "Targeted re-engagement email, no discount needed for 60%",
        "urgency": "high",
    },
]


class CustomerSegmentationAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="customer-segmentation-agent", module_name="customer-segmentation")

    def _orders_api_configured(self) -> bool:
        return bool(os.environ.get("ORDERS_API_URL") and os.environ.get("ORDERS_API_KEY"))

    def fetch_live_data(self, date_from: str, date_to: str) -> dict:
        """Compute RFM segments from Orders API.
        TODO: implement once ORDERS_API_URL and ORDERS_API_KEY are available.
        """
        raise NotImplementedError("Orders API integration pending")

    def sample_summary(self) -> dict:
        total_customers = sum(s["customer_count"] for s in SAMPLE_SEGMENTS.values())
        coupon_needed_count = sum(
            s["customer_count"] for s in SAMPLE_SEGMENTS.values() if s["coupon_needed"]
        )
        coupon_needed_pct = round(coupon_needed_count / total_customers * 100, 1)
        total_ltv = sum(s["customer_count"] * s["avg_ltv_eur"] for s in SAMPLE_SEGMENTS.values())
        avg_ltv = round(total_ltv / total_customers, 2)

        return {
            "headline": (
                f"Active base {total_customers:,} customers | "
                f"VIP {SAMPLE_SEGMENTS['vip']['pct_of_base']}% | "
                f"Churned {SAMPLE_SEGMENTS['churned']['pct_of_base']}% | "
                f"Only {coupon_needed_pct:.0f}% actually need a coupon"
            ),
            "sources_live": False,
            "total_customers": total_customers,
            "avg_ltv_eur": avg_ltv,
            "segments": SAMPLE_SEGMENTS,
            "churn_alerts": SAMPLE_CHURN_ALERTS,
            "coupon_insight": {
                "customers_needing_coupon_pct": coupon_needed_pct,
                "customers_not_needing_coupon_pct": round(100 - coupon_needed_pct, 1),
                "insight": (
                    f"Only {coupon_needed_pct:.0f}% of the customer base (At Risk + Churned) "
                    "actually require a discount incentive to convert. Sitewide coupons waste "
                    f"{round(100 - coupon_needed_pct, 1)}% of discount budget on customers "
                    "who would purchase anyway."
                ),
            },
            "note": "Sample data -- wire ORDERS_API_URL + ORDERS_API_KEY for live RFM computation.",
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self._orders_api_configured():
            logger.info("customer-segmentation-agent: fetching from Orders API")
            try:
                raw = self.fetch_live_data(date_from, date_to)
            except NotImplementedError:
                logger.warning(
                    "customer-segmentation-agent: API integration not yet implemented, using sample data"
                )
                raw = self.sample_summary()
            except Exception as e:
                logger.warning("customer-segmentation-agent: fetch failed: %s", e)
                raw = self.sample_summary()
        else:
            logger.warning(
                "customer-segmentation-agent: Orders API not configured, using sample data"
            )
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Customer Segmentation Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace. You run RFM segmentation and churn risk analysis weekly. "
            "CRITICAL CONTEXT: Ananas has heavy coupon dependency -- blanket discounts are given to "
            "all customers, masking real acquisition efficiency and eroding margin. "
            "Your job: identify which customer segments actually need an incentive vs. which would "
            "purchase without one, surface urgent churn alerts, and give the CRM team a specific "
            "targeting plan for the week. "
            "Format: segment summary table (count, LTV, trend), coupon dependency insight "
            "(% who need discount vs % who don't), top 2 churn alerts with EUR revenue at risk, "
            "weekly CRM action plan (3 targeted actions, not blanket campaigns)."
        )
        user = (
            f"Week of: {date_from}\n"
            f"Segmentation data:\n{raw}\n\n"
            "Write the weekly customer segmentation report and CRM action plan."
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
            logger.error("customer-segmentation-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Segmentation summary -- model unavailable")

        return raw
