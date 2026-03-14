"""Employer Branding Agent — LinkedIn employer presence and talent pipeline.

Phase 1: sample data. LinkedIn Ads is already in integrations.
Phase 2: LinkedIn Company Pages API + Berry HR when available.

Runs weekly (Friday 09:00). Lowest-priority Phase 2 agent -- monitors
talent pipeline visibility and employer brand health on LinkedIn.
"""

from __future__ import annotations

from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

SAMPLE_LINKEDIN_METRICS: dict[str, Any] = {
    "followers": 4_820,
    "followers_wow_change": 48,
    "followers_wow_change_pct": 1.0,
    "avg_post_engagement_rate_pct": 2.8,
    "posts_this_week": 3,
    "top_post_impressions": 3_840,
    "top_post_engagement_rate_pct": 4.2,
    "top_post_topic": "New warehouse opening in Skopje",
}

SAMPLE_JOB_POSTINGS: list[dict[str, Any]] = [
    {
        "title": "Performance Marketing Manager",
        "days_open": 42,
        "views": 840,
        "applications": 12,
        "funnel_pct": 1.4,
        "status": "RISK -- open 42 days",
    },
    {
        "title": "CRM Specialist",
        "days_open": 28,
        "views": 620,
        "applications": 8,
        "funnel_pct": 1.3,
        "status": "monitoring",
    },
    {
        "title": "Content Creator (Social)",
        "days_open": 14,
        "views": 1_240,
        "applications": 34,
        "funnel_pct": 2.7,
        "status": "healthy",
    },
    {
        "title": "Data Analyst",
        "days_open": 56,
        "views": 480,
        "applications": 4,
        "funnel_pct": 0.8,
        "status": "RISK -- low applications, consider boosting",
    },
]


class EmployerBrandingAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="employer-branding-agent", module_name="employer-branding")

    def sample_summary(self) -> dict:
        risk_roles = [j for j in SAMPLE_JOB_POSTINGS if "RISK" in j["status"]]
        return {
            "headline": (
                f"LinkedIn {SAMPLE_LINKEDIN_METRICS['followers']:,} followers "
                f"(+{SAMPLE_LINKEDIN_METRICS['followers_wow_change_pct']}% WoW) | "
                f"{len(risk_roles)} at-risk open role(s)"
            ),
            "sources_live": False,
            "linkedin": SAMPLE_LINKEDIN_METRICS,
            "job_postings": SAMPLE_JOB_POSTINGS,
            "note": "Sample data -- LinkedIn Company Pages API integration pending.",
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        logger.warning("employer-branding-agent: LinkedIn API not configured, using sample data")
        raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Employer Branding Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace competing for digital talent. "
            "Format: "
            "1. LinkedIn presence snapshot (followers, engagement trend). "
            "2. Job posting funnel (open roles, views, application rate). "
            "3. At-risk roles (open >30 days or low application rate). "
            "4. One employer content recommendation for next week."
        )
        user = (
            f"Week of: {date_from}\n"
            f"Employer branding data:\n{raw}\n\n"
            "Write the weekly employer branding report."
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
            logger.error("employer-branding-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Employer branding -- model unavailable")

        return raw
