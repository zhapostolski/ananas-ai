"""Traditional Media Correlation Agent — offline campaign lift attribution.

Phase 1: sample data. GA4 + Search Console are live so real branded
         search lift is measurable when campaign calendar is provided.
Phase 2: wire Google Sheets campaign calendar for automated correlation.

Runs weekly (Friday 08:00). Correlates TV/OOH/Radio campaign dates with
branded search lift, direct traffic spikes, and GMV signals.
"""

from __future__ import annotations

from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.integrations.ga4 import GA4Integration
from ananas_ai.integrations.search_console import SearchConsoleIntegration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

SAMPLE_OFFLINE_CAMPAIGNS: list[dict[str, Any]] = [
    {
        "campaign_name": "Ananas Spring 2026 -- TV",
        "channel": "TV",
        "channels": ["Nova TV MK", "Sitel"],
        "region": "Nationwide MK",
        "start_date": "2026-03-01",
        "end_date": "2026-03-21",
        "budget_eur": 28_000,
        "status": "active",
        "branded_search_lift_pct": 34.2,
        "direct_traffic_lift_pct": 18.6,
        "gmv_lift_pct": 9.4,
        "implied_offline_roas": 2.8,
        "confidence": "medium",
        "notes": "Lift measured vs 2-week pre-campaign baseline. Concurrent Meta campaign may inflate numbers.",
    },
    {
        "campaign_name": "Ananas OOH Skopje -- Q1",
        "channel": "OOH",
        "channels": ["Billboards -- Skopje City Centre", "Bus stops"],
        "region": "Skopje",
        "start_date": "2026-02-15",
        "end_date": "2026-03-15",
        "budget_eur": 8_400,
        "status": "ending",
        "branded_search_lift_pct": 12.1,
        "direct_traffic_lift_pct": 7.4,
        "gmv_lift_pct": 3.2,
        "implied_offline_roas": 1.6,
        "confidence": "low",
        "notes": "OOH correlation is weaker due to difficulty isolating from concurrent TV campaign.",
    },
]

SAMPLE_BASELINE_METRICS: dict[str, Any] = {
    "pre_campaign_branded_searches_daily_avg": 1_840,
    "campaign_period_branded_searches_daily_avg": 2_469,
    "branded_search_lift_pct": 34.2,
    "pre_campaign_direct_sessions_daily_avg": 3_120,
    "campaign_period_direct_sessions_daily_avg": 3_701,
    "direct_traffic_lift_pct": 18.6,
    "pre_campaign_daily_gmv_eur": 142_000,
    "campaign_period_daily_gmv_eur": 155_348,
    "gmv_lift_pct": 9.4,
}


class TraditionalMediaCorrelationAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="traditional-media-correlation-agent",
            module_name="traditional-media-correlation",
        )
        self.ga4 = GA4Integration()
        self.search_console = SearchConsoleIntegration()

    def _has_live_sources(self) -> bool:
        return self.ga4.is_configured() or self.search_console.is_configured()

    def fetch_live_data(self, date_from: str, date_to: str) -> dict:
        ga4_data = self.ga4.safe_fetch(date_from, date_to)
        sc_data = self.search_console.safe_fetch(date_from, date_to)
        return {
            "sources_live": True,
            "ga4": ga4_data,
            "search_console": sc_data,
            "offline_campaigns": SAMPLE_OFFLINE_CAMPAIGNS,
            "baseline_metrics": SAMPLE_BASELINE_METRICS,
            "note": "GA4/SC live. Campaign calendar requires Google Sheets integration (pending).",
        }

    def sample_summary(self) -> dict:
        active = [c for c in SAMPLE_OFFLINE_CAMPAIGNS if c["status"] == "active"]
        total_budget = sum(c["budget_eur"] for c in SAMPLE_OFFLINE_CAMPAIGNS)
        avg_roas = round(
            sum(c["implied_offline_roas"] for c in SAMPLE_OFFLINE_CAMPAIGNS)
            / len(SAMPLE_OFFLINE_CAMPAIGNS),
            1,
        )

        return {
            "headline": (
                f"{len(active)} active offline campaign(s) | "
                f"TV branded search lift +{SAMPLE_OFFLINE_CAMPAIGNS[0]['branded_search_lift_pct']}% | "
                f"Implied offline ROAS avg {avg_roas}x"
            ),
            "sources_live": False,
            "offline_campaigns": SAMPLE_OFFLINE_CAMPAIGNS,
            "baseline_metrics": SAMPLE_BASELINE_METRICS,
            "total_offline_budget_eur": total_budget,
            "note": "Sample data -- wire campaign calendar Google Sheet for automated tracking.",
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self._has_live_sources():
            logger.info("traditional-media-correlation-agent: using live GA4 + SC signals")
            raw = self.fetch_live_data(date_from, date_to)
        else:
            logger.warning(
                "traditional-media-correlation-agent: no live sources, using sample data"
            )
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Traditional Media Correlation Agent. Ananas runs TV, OOH, and "
            "radio campaigns in North Macedonia. Without systematic correlation, the business cannot "
            "know if these offline investments are working. "
            "Your approach: measure branded search lift, direct traffic spike, and GMV change "
            "during campaign periods vs equivalent non-campaign baseline periods. "
            "Always state confidence level (high/medium/low) and confounding factors. "
            "Format: "
            "1. Active offline campaigns + their measured lift (branded search, direct traffic, GMV). "
            "2. Implied offline ROAS per campaign (budget / incremental GMV). "
            "3. Confidence assessment -- what confounds the measurement. "
            "4. Recommendation: continue / adjust / pause for each active campaign. "
            "5. One action for the finance/marketing team (e.g. reallocation between channels)."
        )
        user = (
            f"Week of: {date_from}\n"
            f"Traditional media data:\n{raw}\n\n"
            "Write the weekly traditional media correlation report."
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
            logger.error("traditional-media-correlation-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Traditional media -- model unavailable")

        return raw
