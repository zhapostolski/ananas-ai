from __future__ import annotations

import os

from ananas_ai.integrations.base import BaseIntegration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)


class GoogleAdsIntegration(BaseIntegration):
    """
    Google Ads API -- campaign performance across Search, Display, and Video.

    Auth (service account -- preferred):
      GOOGLE_ADS_DEVELOPER_TOKEN   -- from Google Ads API Center
      GOOGLE_ADS_SERVICE_ACCOUNT_FILE -- path to service account JSON key
      GOOGLE_ADS_LOGIN_CUSTOMER_ID -- MCC account ID (digits only, no dashes)
      GOOGLE_ADS_CUSTOMER_IDS      -- comma-separated sub-account IDs to query

    Auth (OAuth2 -- legacy fallback):
      GOOGLE_ADS_CLIENT_ID / GOOGLE_ADS_CLIENT_SECRET / GOOGLE_ADS_REFRESH_TOKEN
      GOOGLE_ADS_CUSTOMER_ID       -- single account ID
    """

    name = "google-ads"

    def _use_service_account(self) -> bool:
        return bool(
            os.environ.get("GOOGLE_ADS_SERVICE_ACCOUNT_FILE")
            or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        )

    def is_configured(self) -> bool:
        if not os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"):
            return False
        if self._use_service_account():
            return bool(
                os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
                and (
                    os.environ.get("GOOGLE_ADS_CUSTOMER_IDS")
                    or os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
                )
            )
        # OAuth2 path
        return all(
            os.environ.get(k)
            for k in [
                "GOOGLE_ADS_CLIENT_ID",
                "GOOGLE_ADS_CLIENT_SECRET",
                "GOOGLE_ADS_REFRESH_TOKEN",
                "GOOGLE_ADS_CUSTOMER_ID",
            ]
        )

    def _client(self):
        from google.ads.googleads.client import GoogleAdsClient  # type: ignore[import]

        if self._use_service_account():
            sa_file = os.environ.get("GOOGLE_ADS_SERVICE_ACCOUNT_FILE") or os.environ.get(
                "GOOGLE_APPLICATION_CREDENTIALS"
            )
            config = {
                "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
                "json_key_file_path": sa_file,
                "login_customer_id": os.environ["GOOGLE_ADS_LOGIN_CUSTOMER_ID"],
                "use_proto_plus": True,
            }
        else:
            config = {
                "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
                "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
                "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
                "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
                "login_customer_id": os.environ.get(
                    "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
                    os.environ["GOOGLE_ADS_CUSTOMER_ID"],
                ),
                "use_proto_plus": True,
            }
        return GoogleAdsClient.load_from_dict(config)

    def _customer_ids(self) -> list[str]:
        """Return list of sub-account IDs to query."""
        multi = os.environ.get("GOOGLE_ADS_CUSTOMER_IDS", "")
        if multi:
            return [c.strip().replace("-", "") for c in multi.split(",") if c.strip()]
        single = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "")
        return [single.replace("-", "")] if single else []

    def fetch(self, date_from: str, date_to: str) -> dict:
        client = self._client()
        service = client.get_service("GoogleAdsService")

        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                metrics.cost_micros,
                metrics.conversions_value,
                metrics.conversions,
                metrics.impressions,
                metrics.clicks
            FROM campaign
            WHERE segments.date BETWEEN '{date_from}' AND '{date_to}'
              AND campaign.status = 'ENABLED'
            ORDER BY metrics.cost_micros DESC
            LIMIT 50
        """

        campaigns: list[dict] = []
        total_spend = 0.0
        total_conv_value = 0.0
        shopping_campaigns: list[dict] = []

        for customer_id in self._customer_ids():
            try:
                response = service.search(customer_id=customer_id, query=query)
                for row in response:
                    spend = row.metrics.cost_micros / 1_000_000
                    conv_value = row.metrics.conversions_value
                    roas = round(conv_value / spend, 2) if spend > 0 else 0
                    total_spend += spend
                    total_conv_value += conv_value

                    camp = {
                        "id": str(row.campaign.id),
                        "name": row.campaign.name,
                        "channel": row.campaign.advertising_channel_type.name,
                        "customer_id": customer_id,
                        "spend": round(spend, 2),
                        "conversions": row.metrics.conversions,
                        "conversion_value": round(conv_value, 2),
                        "roas": roas,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "poas": roas,
                    }
                    campaigns.append(camp)
                    if "SHOPPING" in row.campaign.advertising_channel_type.name:
                        shopping_campaigns.append(camp)
            except Exception as exc:
                logger.warning("Google Ads: skipping account %s: %s", customer_id, exc)

        blended_roas = round(total_conv_value / total_spend, 2) if total_spend > 0 else 0

        logger.info(
            "Google Ads fetched: accounts=%d campaigns=%d spend=%.2f roas=%.2f",
            len(self._customer_ids()),
            len(campaigns),
            total_spend,
            blended_roas,
        )

        return {
            "campaigns": campaigns,
            "total_spend": round(total_spend, 2),
            "total_conversion_value": round(total_conv_value, 2),
            "blended_roas": blended_roas,
            "shopping_campaigns": shopping_campaigns,
            "date_from": date_from,
            "date_to": date_to,
        }
