from __future__ import annotations

from ananas_ai.agents.base import BaseAgent
from ananas_ai.integrations.ga4 import GA4Integration
from ananas_ai.integrations.google_ads import GoogleAdsIntegration
from ananas_ai.integrations.meta_ads import MetaAdsIntegration
from ananas_ai.integrations.pinterest import PinterestAdsIntegration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)


class PerformanceAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="performance-agent", module_name="performance")
        self.ga4 = GA4Integration()
        self.google_ads = GoogleAdsIntegration()
        self.meta = MetaAdsIntegration()
        self.pinterest = PinterestAdsIntegration()

    def fetch_live_data(self, date_from: str, date_to: str) -> dict:
        ga4_data = self.ga4.safe_fetch(date_from, date_to)
        gads_data = self.google_ads.safe_fetch(date_from, date_to)
        meta_data = self.meta.safe_fetch(date_from, date_to)
        pinterest_data = self.pinterest.safe_fetch(date_from, date_to)

        configured = [
            src
            for src, d in [
                ("ga4", ga4_data),
                ("google-ads", gads_data),
                ("meta-ads", meta_data),
                ("pinterest-ads", pinterest_data),
            ]
            if d
        ]

        total_paid_spend = sum(
            filter(
                None,
                [
                    gads_data.get("total_spend"),
                    meta_data.get("spend"),
                    pinterest_data.get("spend"),
                ],
            )
        )
        total_paid_value = sum(
            filter(
                None,
                [
                    gads_data.get("total_conversion_value"),
                    meta_data.get("purchase_value"),
                    pinterest_data.get("conversion_value"),
                ],
            )
        )
        blended_roas = round(total_paid_value / total_paid_spend, 2) if total_paid_spend else 0.0

        shopping_is = gads_data.get("shopping_impression_share_pct", 0.0)
        shopping_active = gads_data.get("shopping_campaigns_active", 0)

        notes = []
        if gads_data and shopping_is == 0.0:
            notes.append(
                "CRITICAL: Google Shopping impression share is 0% — no active Shopping campaigns."
            )
        elif shopping_is and shopping_is < 20:
            notes.append(
                f"Google Shopping impression share is low at {shopping_is}% — review bids/budget."
            )
        if not notes:
            notes.append("All channels operational.")

        return {
            "headline": self._build_headline(
                ga4_data.get("revenue", 0), blended_roas, shopping_is, ga4_data.get("sessions", 0)
            ),
            "sources_active": configured,
            "ga4": ga4_data,
            "google_ads": gads_data,
            "meta_ads": meta_data,
            "pinterest_ads": pinterest_data,
            "summary": {
                "total_paid_spend": round(total_paid_spend, 2),
                "total_paid_conversion_value": round(total_paid_value, 2),
                "blended_roas": blended_roas,
                "shopping_impression_share_pct": shopping_is,
                "shopping_campaigns_active": shopping_active,
                "ga4_revenue": ga4_data.get("revenue", 0),
                "ga4_sessions": ga4_data.get("sessions", 0),
                "ga4_conversion_rate_pct": ga4_data.get("conversion_rate_pct", 0),
            },
            "notes": notes,
            "date_from": date_from,
            "date_to": date_to,
        }

    def _build_headline(
        self, revenue: float, roas: float, shopping_is: float, sessions: int
    ) -> str:
        parts = []
        if revenue:
            parts.append(f"Revenue EUR{revenue:,.0f}")
        if roas:
            parts.append(f"blended ROAS {roas:.1f}x")
        if shopping_is == 0.0:
            parts.append("Shopping IS: 0% CRITICAL")
        elif shopping_is:
            parts.append(f"Shopping IS {shopping_is:.0f}%")
        if sessions:
            parts.append(f"{sessions:,} sessions")
        return " | ".join(parts) if parts else "Performance summary (no live data)"

    def sample_summary(self) -> dict:
        return {
            "headline": "Performance summary (sample data — configure credentials)",
            "sources_active": [],
            "summary": {
                "total_paid_spend": 0,
                "blended_roas": 0,
                "shopping_impression_share_pct": 0,
                "shopping_campaigns_active": 0,
                "ga4_revenue": 0,
                "ga4_sessions": 0,
                "ga4_conversion_rate_pct": 0,
            },
            "notes": [
                "CRITICAL: Google Shopping has 0 active campaigns despite 250k+ products.",
                "No live integration data — configure GA4, Google Ads, Meta, Pinterest credentials.",
            ],
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        any_configured = any(
            [
                self.ga4.is_configured(),
                self.google_ads.is_configured(),
                self.meta.is_configured(),
                self.pinterest.is_configured(),
            ]
        )
        raw = self.fetch_live_data(date_from, date_to) if any_configured else self.sample_summary()
        if any_configured:
            logger.info("performance-agent: running with live integrations")
        else:
            logger.warning("performance-agent: no integrations configured, using sample data")

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Performance Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace with 250k+ products. Analyse the paid media performance data "
            "and write a concise daily briefing for the marketing team. "
            "Critical context: Google Shopping has ZERO active campaigns despite 250k+ products — "
            "always flag this. Sales are heavily coupon-dependent. "
            "Format: 3-5 bullet points, plain language, numbers in EUR, flag anomalies clearly. "
            "End with one priority action for today."
        )
        user = (
            f"Date: {date_from}\nPerformance data:\n{raw}\n\nWrite the daily performance briefing."
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
            logger.error("performance-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Performance summary — model unavailable")

        return raw
