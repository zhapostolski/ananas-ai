from __future__ import annotations

import os

import requests

from ananas_ai.integrations.base import BaseIntegration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

PINTEREST_BASE = "https://api.pinterest.com/v5"


class PinterestAdsIntegration(BaseIntegration):
    """
    Pinterest Ads via Pinterest API v5.

    Required env vars:
      PINTEREST_ACCESS_TOKEN  - OAuth2 access token
      PINTEREST_AD_ACCOUNT_ID - ad account ID
    """

    name = "pinterest-ads"

    def is_configured(self) -> bool:
        return bool(
            os.environ.get("PINTEREST_ACCESS_TOKEN") and os.environ.get("PINTEREST_AD_ACCOUNT_ID")
        )

    def _get(self, path: str, params: dict | None = None) -> dict:
        headers = {
            "Authorization": f"Bearer {os.environ['PINTEREST_ACCESS_TOKEN']}",
            "Content-Type": "application/json",
        }
        resp = requests.get(
            f"{PINTEREST_BASE}/{path}",
            headers=headers,
            params=params or {},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]

    def fetch(self, date_from: str, date_to: str) -> dict:
        account_id = os.environ["PINTEREST_AD_ACCOUNT_ID"]

        # ── Account-level analytics ──────────────────────────────────────────
        analytics = self._get(
            f"ad_accounts/{account_id}/analytics",
            {
                "start_date": date_from,
                "end_date": date_to,
                "columns": "SPEND_IN_DOLLAR,TOTAL_CONVERSIONS,TOTAL_CONVERSION_VALUE_IN_MICRO_DOLLAR,IMPRESSION_1,CLICK_1",
                "granularity": "TOTAL",
            },
        )

        totals = analytics.get("data", [{}])[0] if analytics.get("data") else {}
        spend = float(totals.get("SPEND_IN_DOLLAR", 0))
        conv_value = float(totals.get("TOTAL_CONVERSION_VALUE_IN_MICRO_DOLLAR", 0)) / 1_000_000
        conversions = int(totals.get("TOTAL_CONVERSIONS", 0))
        impressions = int(totals.get("IMPRESSION_1", 0))
        clicks = int(totals.get("CLICK_1", 0))
        roas = round(conv_value / spend, 2) if spend > 0 else 0.0

        # ── Campaign breakdown ───────────────────────────────────────────────
        campaigns_resp = self._get(
            f"ad_accounts/{account_id}/campaigns",
            {"entity_statuses": "ACTIVE", "page_size": 25},
        )

        campaigns = []
        for camp in campaigns_resp.get("items", []):
            camp_id = camp.get("id", "")
            try:
                camp_analytics = self._get(
                    f"ad_accounts/{account_id}/campaigns/analytics",
                    {
                        "start_date": date_from,
                        "end_date": date_to,
                        "campaign_ids": camp_id,
                        "columns": "SPEND_IN_DOLLAR,TOTAL_CONVERSION_VALUE_IN_MICRO_DOLLAR,IMPRESSION_1,CLICK_1",
                        "granularity": "TOTAL",
                    },
                )
                c_data = camp_analytics.get("data", [{}])[0] if camp_analytics.get("data") else {}
                c_spend = float(c_data.get("SPEND_IN_DOLLAR", 0))
                c_value = float(c_data.get("TOTAL_CONVERSION_VALUE_IN_MICRO_DOLLAR", 0)) / 1_000_000
                campaigns.append(
                    {
                        "name": camp.get("name", ""),
                        "status": camp.get("status", ""),
                        "spend": round(c_spend, 2),
                        "conversion_value": round(c_value, 2),
                        "roas": round(c_value / c_spend, 2) if c_spend > 0 else 0.0,
                    }
                )
            except Exception as exc:
                logger.warning("Could not fetch Pinterest campaign %s analytics: %s", camp_id, exc)

        logger.info(
            "Pinterest fetched: campaigns=%d spend=%.2f roas=%.2f",
            len(campaigns),
            spend,
            roas,
        )

        return {
            "spend": round(spend, 2),
            "roas": roas,
            "conversion_value": round(conv_value, 2),
            "conversions": conversions,
            "impressions": impressions,
            "clicks": clicks,
            "campaigns": campaigns,
            "date_from": date_from,
            "date_to": date_to,
        }
