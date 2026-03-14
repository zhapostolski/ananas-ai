from __future__ import annotations

from ananas_ai.agents.base import BaseAgent
from ananas_ai.integrations.ga4 import GA4Integration
from ananas_ai.integrations.search_console import SearchConsoleIntegration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)


class MarketingOpsAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="marketing-ops-agent", module_name="marketing-ops")
        self.ga4 = GA4Integration()
        self.search_console = SearchConsoleIntegration()

    def fetch_live_data(self, date_from: str, date_to: str) -> dict:
        ga4_data = self.ga4.safe_fetch(date_from, date_to)
        sc_data = self.search_console.safe_fetch(date_from, date_to)

        # Tracking health: check if GA4 returned expected event volume
        tracking_ok = bool(ga4_data and ga4_data.get("sessions", 0) > 0)
        tracking_status = "ok" if tracking_ok else "warning — no GA4 data received"

        alerts = []
        if not tracking_ok:
            alerts.append("GA4 returned no sessions — check tracking implementation.")
        if ga4_data and ga4_data.get("conversion_rate_pct", 0) < 0.5:
            alerts.append(
                f"Conversion rate is {ga4_data.get('conversion_rate_pct', 0):.2f}% — below 0.5% threshold."
            )

        # Search Console health
        sc_clicks = sc_data.get("total_clicks", 0)
        sc_position = sc_data.get("avg_position", 0)

        return {
            "headline": self._build_headline(tracking_ok, sc_clicks, sc_position),
            "tracking_health": {
                "status": tracking_status,
                "ga4_sessions": ga4_data.get("sessions", 0),
                "ga4_events_ok": tracking_ok,
            },
            "search_console": {
                "total_clicks": sc_clicks,
                "total_impressions": sc_data.get("total_impressions", 0),
                "avg_position": sc_position,
                "avg_ctr_pct": sc_data.get("avg_ctr_pct", 0),
                "top_queries": sc_data.get("top_queries", [])[:5],
            },
            "kpi_integrity": {
                "ga4_revenue": ga4_data.get("revenue", 0),
                "ga4_conversion_rate_pct": ga4_data.get("conversion_rate_pct", 0),
            },
            "alerts": alerts,
            "notes": [
                "Coupon dependency ratio requires Orders API integration — configure when available.",
                "Campaign analysis coverage tracked manually until Jira integration is live.",
            ],
            "date_from": date_from,
            "date_to": date_to,
        }

    def _build_headline(self, tracking_ok: bool, sc_clicks: int, sc_position: float) -> str:
        parts = []
        parts.append("Tracking: OK" if tracking_ok else "Tracking: WARNING")
        if sc_clicks:
            parts.append(f"Organic {sc_clicks:,} clicks")
        if sc_position:
            parts.append(f"avg pos {sc_position:.1f}")
        return " | ".join(parts)

    def sample_summary(self) -> dict:
        return {
            "headline": "Marketing ops summary (sample data)",
            "tracking_health": {"status": "unknown — no GA4 credentials"},
            "search_console": {},
            "alerts": [],
            "notes": [
                "Coupon dependency ratio requires Orders API integration.",
                "Configure GA4 and Search Console credentials to enable live tracking health.",
            ],
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self.ga4.is_configured() or self.search_console.is_configured():
            logger.info("marketing-ops-agent: running with live integrations")
            raw = self.fetch_live_data(date_from, date_to)
        else:
            logger.warning("marketing-ops-agent: no integrations configured, using sample data")
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Marketing Ops Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace. Your job is to ensure marketing operations health — "
            "tracking integrity, KPI sanity, campaign coverage, and operational issues. "
            "Known issues to watch: heavy coupon dependency masking real acquisition efficiency, "
            "no email lifecycle automations live (no cart recovery, no churn flows), "
            "Trustpilot rating 2.0 and profile unclaimed. "
            "Format: status indicators (OK/WARNING/CRITICAL), bullet points, one priority action."
        )
        user = (
            f"Date: {date_from}\n"
            f"Marketing ops data:\n{raw}\n\n"
            "Write the daily marketing ops briefing."
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
            logger.error("marketing-ops-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Marketing ops summary — model unavailable")

        return raw
