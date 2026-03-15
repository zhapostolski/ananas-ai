from __future__ import annotations

import os

from ananas_ai.integrations.base import BaseIntegration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)


class GA4Integration(BaseIntegration):
    """
    Google Analytics 4 via the Google Analytics Data API.

    Required env vars:
      GA4_PROPERTY_ID   - numeric property ID, e.g. "properties/123456789"
      GA4_CREDENTIALS   - path to service account JSON, OR use ADC (gcloud auth)
    """

    name = "ga4"

    def is_configured(self) -> bool:
        if not os.environ.get("GA4_PROPERTY_ID"):
            return False
        creds_path = os.environ.get("GA4_CREDENTIALS")
        return not (creds_path and not os.path.exists(creds_path))

    def fetch(self, date_from: str, date_to: str) -> dict:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )

        creds_path = os.environ.get("GA4_CREDENTIALS")
        if creds_path:
            os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", creds_path)

        property_id = os.environ["GA4_PROPERTY_ID"]
        if not property_id.startswith("properties/"):
            property_id = f"properties/{property_id}"

        client = BetaAnalyticsDataClient()

        # ── Overview metrics ────────────────────────────────────────────────
        overview_req = RunReportRequest(
            property=property_id,
            date_ranges=[DateRange(start_date=date_from, end_date=date_to)],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="purchaseRevenue"),
                Metric(name="transactions"),
                Metric(name="sessionConversionRate"),
            ],
        )
        overview = client.run_report(overview_req)
        row = overview.rows[0].metric_values if overview.rows else [None] * 5  # type: ignore[list-item]

        def val(r, i, cast=float):
            try:
                return cast(r[i].value)
            except Exception:
                return 0

        sessions = val(row, 0, int)
        users = val(row, 1, int)
        revenue = round(val(row, 2), 2)
        transactions = val(row, 3, int)
        conversion_rate = round(val(row, 4) * 100, 2)

        # ── Channel breakdown ───────────────────────────────────────────────
        channel_req = RunReportRequest(
            property=property_id,
            date_ranges=[DateRange(start_date=date_from, end_date=date_to)],
            dimensions=[Dimension(name="sessionDefaultChannelGroup")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="purchaseRevenue"),
            ],
            order_bys=[{"metric": {"metric_name": "purchaseRevenue"}, "desc": True}],
            limit=10,
        )
        channel_resp = client.run_report(channel_req)
        channels = [
            {
                "channel": r.dimension_values[0].value,
                "sessions": int(r.metric_values[0].value),
                "revenue": round(float(r.metric_values[1].value), 2),
            }
            for r in channel_resp.rows
        ]

        # ── Top landing pages ────────────────────────────────────────────────
        pages_req = RunReportRequest(
            property=property_id,
            date_ranges=[DateRange(start_date=date_from, end_date=date_to)],
            dimensions=[Dimension(name="landingPage")],
            metrics=[Metric(name="sessions"), Metric(name="bounceRate")],
            order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}],
            limit=5,
        )
        pages_resp = client.run_report(pages_req)
        top_pages = [
            {
                "page": r.dimension_values[0].value,
                "sessions": int(r.metric_values[0].value),
                "bounce_rate": round(float(r.metric_values[1].value) * 100, 1),
            }
            for r in pages_resp.rows
        ]

        logger.info(
            "GA4 fetched: sessions=%d users=%d revenue=%.2f",
            sessions,
            users,
            revenue,
        )

        return {
            "sessions": sessions,
            "users": users,
            "revenue": revenue,
            "transactions": transactions,
            "conversion_rate_pct": conversion_rate,
            "channels": channels,
            "top_pages": top_pages,
            "date_from": date_from,
            "date_to": date_to,
        }
