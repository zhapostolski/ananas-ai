"""Organic & Merchandising Agent — SEO performance and catalog indexation.

Phase 1: Search Console is live (already wired). Uses real SC data where available
         and fills gaps with sample data for category-level analysis.
Phase 2: add Ahrefs/Semrush API for domain authority and keyword gap analysis.

Runs daily (08:00). Monitors organic search health for 250k product catalog.
SEO agency is already engaged -- this agent gives internal team oversight.
"""

from __future__ import annotations

import os
from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.integrations.search_console import SearchConsoleIntegration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

SAMPLE_KEYWORD_MOVEMENTS: list[dict[str, Any]] = [
    {
        "query": "klima uredaj cena",
        "current_position": 4.2,
        "prev_position": 6.8,
        "change": -2.6,
        "clicks_wow": 340,
        "direction": "UP",
    },
    {
        "query": "nike patiki",
        "current_position": 2.1,
        "prev_position": 2.4,
        "change": -0.3,
        "clicks_wow": 820,
        "direction": "UP",
    },
    {
        "query": "laptop evtino",
        "current_position": 8.4,
        "prev_position": 5.1,
        "change": 3.3,
        "clicks_wow": -180,
        "direction": "DOWN",
    },
    {
        "query": "gradinski namestaj",
        "current_position": 3.7,
        "prev_position": 7.2,
        "change": -3.5,
        "clicks_wow": 290,
        "direction": "UP",
    },
    {
        "query": "mobilni telefoni makedonija",
        "current_position": 11.2,
        "prev_position": 9.8,
        "change": 1.4,
        "clicks_wow": -210,
        "direction": "DOWN",
    },
]

SAMPLE_CATEGORY_SEO: list[dict[str, Any]] = [
    {
        "category": "Electronics",
        "indexed_pages": 11_240,
        "catalog_size": 18_400,
        "indexation_pct": 61.1,
        "organic_cvr_pct": 1.8,
        "trend": "stable",
    },
    {
        "category": "Shoes & Clothing",
        "indexed_pages": 36_800,
        "catalog_size": 67_200,
        "indexation_pct": 54.8,
        "organic_cvr_pct": 2.1,
        "trend": "improving",
    },
    {
        "category": "Home & Garden",
        "indexed_pages": 19_400,
        "catalog_size": 42_100,
        "indexation_pct": 46.1,
        "organic_cvr_pct": 1.4,
        "trend": "declining",
    },
    {
        "category": "Beauty & Health",
        "indexed_pages": 18_900,
        "catalog_size": 31_800,
        "indexation_pct": 59.4,
        "organic_cvr_pct": 2.6,
        "trend": "improving",
    },
    {
        "category": "Sports & Outdoors",
        "indexed_pages": 17_200,
        "catalog_size": 28_600,
        "indexation_pct": 60.1,
        "organic_cvr_pct": 2.2,
        "trend": "stable",
    },
]

SAMPLE_SEO_ISSUES: list[dict[str, Any]] = [
    {
        "issue": "Duplicate meta titles",
        "affected_pages": 4_120,
        "severity": "high",
        "fix": "Implement dynamic title templates per category",
    },
    {
        "issue": "Missing H1 on product pages",
        "affected_pages": 2_840,
        "severity": "high",
        "fix": "Add product name as H1 in template",
    },
    {
        "issue": "Thin content pages (<300 words)",
        "affected_pages": 18_600,
        "severity": "medium",
        "fix": "Expand product descriptions with structured data",
    },
    {
        "issue": "Slow Core Web Vitals (LCP > 2.5s)",
        "affected_pages": 0,
        "severity": "low",
        "fix": "Image optimization, lazy loading",
    },
]


class OrganicMerchandisingAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="organic-merchandising-agent", module_name="organic-merchandising")
        self.search_console = SearchConsoleIntegration()

    def _semrush_configured(self) -> bool:
        return bool(os.environ.get("SEMRUSH_API_KEY") or os.environ.get("AHREFS_API_KEY"))

    def fetch_live_data(self, date_from: str, date_to: str) -> dict:
        sc_data = self.search_console.safe_fetch(date_from, date_to)
        return {
            "sources_live": True,
            "search_console": sc_data,
            "keyword_movements": SAMPLE_KEYWORD_MOVEMENTS,
            "category_seo": SAMPLE_SEO_ISSUES,
            "seo_issues": SAMPLE_SEO_ISSUES,
            "note": "Search Console live. Category-level SEO requires Ahrefs/Semrush key.",
        }

    def sample_summary(self) -> dict:
        total_indexed = sum(c["indexed_pages"] for c in SAMPLE_CATEGORY_SEO)
        total_catalog = sum(c["catalog_size"] for c in SAMPLE_CATEGORY_SEO)
        indexation_pct = round(total_indexed / total_catalog * 100, 1)
        gains = [k for k in SAMPLE_KEYWORD_MOVEMENTS if k["direction"] == "UP"]
        drops = [k for k in SAMPLE_KEYWORD_MOVEMENTS if k["direction"] == "DOWN"]

        return {
            "headline": (
                f"Indexation {indexation_pct}% ({total_indexed:,}/{total_catalog:,} pages) | "
                f"{len(gains)} keyword gains | {len(drops)} drops"
            ),
            "sources_live": False,
            "total_indexed_pages": total_indexed,
            "total_catalog_size": total_catalog,
            "indexation_pct": indexation_pct,
            "indexation_target_pct": 80.0,
            "keyword_movements": SAMPLE_KEYWORD_MOVEMENTS,
            "category_seo": SAMPLE_CATEGORY_SEO,
            "seo_issues": SAMPLE_SEO_ISSUES,
            "note": "Sample category data. Search Console is live -- wire SC credentials for real keyword data.",
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self.search_console.is_configured():
            logger.info("organic-merchandising-agent: using live Search Console data")
            raw = self.fetch_live_data(date_from, date_to)
        else:
            logger.warning(
                "organic-merchandising-agent: Search Console not configured, using sample data"
            )
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Organic & Merchandising Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace with 250,000+ products. An SEO agency is engaged externally -- "
            "your role is internal oversight, not replacing the agency. "
            "Critical metric: only ~57% of 250k products are currently indexed by Google. "
            "Every product not indexed is invisible to organic search. "
            "Format: "
            "1. Organic traffic snapshot (sessions, CVR vs paid, trend). "
            "2. Indexation health (% indexed, worst-performing categories). "
            "3. Top 3 keyword movements (gains to protect, drops to investigate). "
            "4. Top SEO technical issue this week (one fix, specific and actionable). "
            "5. One agency deliverable to check (if Semrush/Ahrefs data available)."
        )
        user = (
            f"Date: {date_from}\n"
            f"SEO data:\n{raw}\n\n"
            "Write the daily organic & merchandising report."
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
            logger.error("organic-merchandising-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Organic merchandising -- model unavailable")

        return raw
