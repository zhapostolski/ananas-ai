from __future__ import annotations

import os

import requests

from ananas_ai.integrations.base import BaseIntegration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

GRAPH_BASE = "https://graph.facebook.com/v19.0"


class MetaAdsIntegration(BaseIntegration):
    """
    Meta Ads (Facebook + Instagram) via Meta Marketing API.

    Required env vars:
      META_ACCESS_TOKEN   - system user or page access token
      META_AD_ACCOUNT_ID  - ad account ID, e.g. act_123456789
    """

    name = "meta-ads"

    def is_configured(self) -> bool:
        return bool(os.environ.get("META_ACCESS_TOKEN") and os.environ.get("META_AD_ACCOUNT_ID"))

    def _get(self, path: str, params: dict) -> dict:
        params["access_token"] = os.environ["META_ACCESS_TOKEN"]
        resp = requests.get(f"{GRAPH_BASE}/{path}", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]

    def fetch(self, date_from: str, date_to: str) -> dict:
        account_id = os.environ["META_AD_ACCOUNT_ID"]
        if not account_id.startswith("act_"):
            account_id = f"act_{account_id}"

        # ── Account-level insights ───────────────────────────────────────────
        account_insights = self._get(
            f"{account_id}/insights",
            {
                "fields": "spend,purchase_roas,actions,action_values,impressions,clicks,cpc,cpm",
                "time_range": f'{{"since":"{date_from}","until":"{date_to}"}}',
                "level": "account",
            },
        )

        data = account_insights.get("data", [{}])[0]
        spend = float(data.get("spend", 0))

        purchase_roas = data.get("purchase_roas", [{}])
        roas = float(purchase_roas[0].get("value", 0)) if purchase_roas else 0.0

        action_values = {a["action_type"]: float(a["value"]) for a in data.get("action_values", [])}
        purchase_value = action_values.get("purchase", 0.0)

        # ── Campaign breakdown ───────────────────────────────────────────────
        campaign_insights = self._get(
            f"{account_id}/insights",
            {
                "fields": "campaign_name,spend,purchase_roas,impressions,clicks,actions",
                "time_range": f'{{"since":"{date_from}","until":"{date_to}"}}',
                "level": "campaign",
                "sort": "spend_descending",
                "limit": 20,
            },
        )

        campaigns = []
        for row in campaign_insights.get("data", []):
            camp_roas_list = row.get("purchase_roas", [{}])
            camp_roas = float(camp_roas_list[0].get("value", 0)) if camp_roas_list else 0.0
            campaigns.append(
                {
                    "name": row.get("campaign_name", ""),
                    "spend": float(row.get("spend", 0)),
                    "roas": round(camp_roas, 2),
                    "impressions": int(row.get("impressions", 0)),
                    "clicks": int(row.get("clicks", 0)),
                }
            )

        logger.info(
            "Meta Ads fetched: campaigns=%d spend=%.2f roas=%.2f",
            len(campaigns),
            spend,
            roas,
        )

        return {
            "spend": round(spend, 2),
            "roas": round(roas, 2),
            "purchase_value": round(purchase_value, 2),
            "impressions": int(data.get("impressions", 0)),
            "clicks": int(data.get("clicks", 0)),
            "cpc": round(float(data.get("cpc", 0)), 3),
            "cpm": round(float(data.get("cpm", 0)), 2),
            "campaigns": campaigns,
            "date_from": date_from,
            "date_to": date_to,
        }
