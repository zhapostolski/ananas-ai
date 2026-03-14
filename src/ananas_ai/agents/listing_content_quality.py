"""Listing Content Quality Agent — catalog quality scan across all surfaces.

Phase 1: sample data with realistic quality scores per category.
Phase 2: wires into Product Catalog API.

Runs weekly (Friday 08:00). Scans 250k catalog for thin content, missing
images, poor attributes. Distinct from product-feed-agent (which focuses
on Google Shopping eligibility) -- this covers all surfaces: site search,
category pages, and conversion. Prioritises fixes by GMV impact.
"""

from __future__ import annotations

import os
from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

SAMPLE_QUALITY_ISSUES: list[dict[str, Any]] = [
    {
        "issue_type": "thin_description",
        "description": "Product description under 100 characters",
        "affected_products": 22_840,
        "affected_pct": 9.1,
        "gmv_at_risk_eur_weekly": 48_200,
        "severity": "high",
        "fix": "Auto-expand descriptions using category template + supplier specs",
        "effort": "medium",
    },
    {
        "issue_type": "single_image",
        "description": "Only 1 product image (minimum 3 recommended)",
        "affected_products": 31_600,
        "affected_pct": 12.6,
        "gmv_at_risk_eur_weekly": 61_400,
        "severity": "high",
        "fix": "Request additional images from suppliers in bulk outreach",
        "effort": "high",
    },
    {
        "issue_type": "missing_brand",
        "description": "Brand attribute empty or 'Unknown'",
        "affected_products": 28_700,
        "affected_pct": 11.4,
        "gmv_at_risk_eur_weekly": 34_100,
        "severity": "medium",
        "fix": "Extract brand from product title using NLP; flag remaining for manual review",
        "effort": "low",
    },
    {
        "issue_type": "no_size_chart",
        "description": "Clothing/shoes listing with no size guide link",
        "affected_products": 18_400,
        "affected_pct": 7.3,
        "gmv_at_risk_eur_weekly": 41_800,
        "severity": "high",
        "fix": "Add category-level size guide link template for all Clothing and Shoes",
        "effort": "low",
    },
    {
        "issue_type": "missing_color_variants",
        "description": "Product exists in multiple colours but listed as separate SKUs without linking",
        "affected_products": 14_200,
        "affected_pct": 5.7,
        "gmv_at_risk_eur_weekly": 28_600,
        "severity": "medium",
        "fix": "Merge colour variants into parent listing with variant selector",
        "effort": "high",
    },
    {
        "issue_type": "poor_title",
        "description": "Title under 40 characters or missing category keyword",
        "affected_products": 19_800,
        "affected_pct": 7.9,
        "gmv_at_risk_eur_weekly": 39_200,
        "severity": "medium",
        "fix": "Apply title template: [Brand] + [Product Type] + [Key Spec] + [Category Keyword]",
        "effort": "low",
    },
]

SAMPLE_CATEGORY_QUALITY: list[dict[str, Any]] = [
    {
        "category": "Electronics",
        "quality_score": 72,
        "listings_below_threshold": 3_840,
        "worst_issue": "Missing technical specs",
        "trend": "improving",
    },
    {
        "category": "Shoes & Clothing",
        "quality_score": 61,
        "listings_below_threshold": 18_200,
        "worst_issue": "Missing size charts, single image",
        "trend": "stable",
    },
    {
        "category": "Home & Garden",
        "quality_score": 58,
        "listings_below_threshold": 12_100,
        "worst_issue": "Thin descriptions, missing brand",
        "trend": "declining",
    },
    {
        "category": "Beauty & Health",
        "quality_score": 81,
        "listings_below_threshold": 2_840,
        "worst_issue": "Missing ingredient lists",
        "trend": "improving",
    },
    {
        "category": "Sports & Outdoors",
        "quality_score": 74,
        "listings_below_threshold": 4_200,
        "worst_issue": "Missing material/size details",
        "trend": "stable",
    },
    {
        "category": "Automotive",
        "quality_score": 44,
        "listings_below_threshold": 6_840,
        "worst_issue": "Thin content, missing compatibility info",
        "trend": "declining",
    },
]

SAMPLE_NEW_LISTINGS: list[dict[str, Any]] = [
    {
        "supplier": "TechPro Distribution",
        "new_listings_24h": 142,
        "below_threshold": 89,
        "below_pct": 62.7,
        "action": "Hold from homepage feature until content fixed",
    },
    {
        "supplier": "FashionHub Balkans",
        "new_listings_24h": 318,
        "below_threshold": 201,
        "below_pct": 63.2,
        "action": "Auto-flag for content review queue before going live",
    },
]


class ListingContentQualityAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="listing-content-quality-agent", module_name="listing-content-quality"
        )

    def _catalog_api_configured(self) -> bool:
        return bool(os.environ.get("CATALOG_API_URL") and os.environ.get("CATALOG_API_KEY"))

    def fetch_live_data(self, date_from: str, date_to: str) -> dict:
        """Fetch catalog quality metrics from Product Catalog API.
        TODO: implement once CATALOG_API_URL is available.
        """
        raise NotImplementedError("Product Catalog API integration pending")

    def sample_summary(self) -> dict:
        total_products = 251_400
        total_gmv_at_risk = sum(i["gmv_at_risk_eur_weekly"] for i in SAMPLE_QUALITY_ISSUES)
        quality_score = round(
            sum(c["quality_score"] for c in SAMPLE_CATEGORY_QUALITY) / len(SAMPLE_CATEGORY_QUALITY),
            1,
        )
        high_severity = [i for i in SAMPLE_QUALITY_ISSUES if i["severity"] == "high"]
        low_effort_high_impact = sorted(
            [i for i in SAMPLE_QUALITY_ISSUES if i["effort"] == "low"],
            key=lambda x: x["gmv_at_risk_eur_weekly"],
            reverse=True,
        )

        return {
            "headline": (
                f"Catalog quality score {quality_score}/100 | "
                f"EUR{total_gmv_at_risk:,.0f}/week GMV at risk | "
                f"{len(high_severity)} high-severity issues"
            ),
            "sources_live": False,
            "total_products": total_products,
            "catalog_quality_score": quality_score,
            "catalog_quality_target": 80.0,
            "total_gmv_at_risk_weekly_eur": total_gmv_at_risk,
            "quality_issues": SAMPLE_QUALITY_ISSUES,
            "category_quality": SAMPLE_CATEGORY_QUALITY,
            "new_listing_alerts": SAMPLE_NEW_LISTINGS,
            "quick_wins": low_effort_high_impact[:3],
            "note": "Sample data -- wire CATALOG_API_URL + CATALOG_API_KEY for live scan.",
        }

    def run(self, date_from: str, date_to: str) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        if self._catalog_api_configured():
            logger.info("listing-content-quality-agent: fetching from Catalog API")
            try:
                raw = self.fetch_live_data(date_from, date_to)
            except NotImplementedError:
                logger.warning(
                    "listing-content-quality-agent: API not yet implemented, using sample data"
                )
                raw = self.sample_summary()
            except Exception as e:
                logger.warning("listing-content-quality-agent: fetch failed: %s", e)
                raw = self.sample_summary()
        else:
            logger.warning(
                "listing-content-quality-agent: Catalog API not configured, using sample data"
            )
            raw = self.sample_summary()

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Listing Content Quality Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace with 250,000+ products. "
            "Poor listing content directly reduces search visibility, conversion rate, and Shopping eligibility. "
            "EUR GMV at risk from content issues is measurable and actionable. "
            "This agent covers ALL surfaces (site search, category pages, conversion) -- "
            "not just Google Shopping feed readiness (that is the product-feed-agent's scope). "
            "Format: "
            "1. Catalog quality score vs target (80/100). "
            "2. Top 3 high-severity issues: affected product count, GMV at risk, specific fix. "
            "3. Quick wins: low-effort fixes with high GMV impact (do these first). "
            "4. Category worst performers (2 categories needing most attention). "
            "5. New listing alerts: suppliers uploading poor-quality content in last 24h."
        )
        user = (
            f"Week of: {date_from}\n"
            f"Content quality data:\n{raw}\n\n"
            "Write the weekly listing content quality report."
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
            logger.error("listing-content-quality-agent: model call failed: %s", e)
            raw["analysis"] = raw.get("headline", "Listing quality -- model unavailable")

        return raw
