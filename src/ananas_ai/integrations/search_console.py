from __future__ import annotations

import os

from ananas_ai.integrations.base import BaseIntegration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)


class SearchConsoleIntegration(BaseIntegration):
    """
    Google Search Console via the Webmasters API.

    Required env vars:
      SEARCH_CONSOLE_SITE_URL  — verified property URL, e.g. https://ananas.mk/
      GA4_CREDENTIALS          — shared service account JSON (same as GA4)
    """

    name = "search-console"

    def is_configured(self) -> bool:
        if not os.environ.get("SEARCH_CONSOLE_SITE_URL"):
            return False
        creds_path = os.environ.get("GA4_CREDENTIALS")
        return not (creds_path and not os.path.exists(creds_path))

    def _service(self):
        from google.oauth2 import service_account  # type: ignore[import]
        from googleapiclient.discovery import build  # type: ignore[import]

        creds_path = os.environ.get("GA4_CREDENTIALS")
        if creds_path:
            creds = service_account.Credentials.from_service_account_file(
                creds_path,
                scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
            )
        else:
            import google.auth  # type: ignore[import]

            creds, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
            )
        return build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    def fetch(self, date_from: str, date_to: str) -> dict:
        service = self._service()
        site_url = os.environ["SEARCH_CONSOLE_SITE_URL"]

        def query(dimensions, row_limit=10):
            return (
                service.searchanalytics()
                .query(
                    siteUrl=site_url,
                    body={
                        "startDate": date_from,
                        "endDate": date_to,
                        "dimensions": dimensions,
                        "rowLimit": row_limit,
                        "dataState": "all",
                    },
                )
                .execute()
            )

        # ── Overview ────────────────────────────────────────────────────────
        overview = query([], row_limit=1)
        totals = overview.get("rows", [{}])[0]
        total_clicks = int(totals.get("clicks", 0))
        total_impressions = int(totals.get("impressions", 0))
        avg_ctr = round(totals.get("ctr", 0) * 100, 2)
        avg_position = round(totals.get("position", 0), 1)

        # ── Top queries ──────────────────────────────────────────────────────
        queries_resp = query(["query"], row_limit=20)
        top_queries = [
            {
                "query": r["keys"][0],
                "clicks": int(r["clicks"]),
                "impressions": int(r["impressions"]),
                "ctr_pct": round(r["ctr"] * 100, 2),
                "position": round(r["position"], 1),
            }
            for r in queries_resp.get("rows", [])
        ]

        # ── Top pages ────────────────────────────────────────────────────────
        pages_resp = query(["page"], row_limit=10)
        top_pages = [
            {
                "page": r["keys"][0],
                "clicks": int(r["clicks"]),
                "impressions": int(r["impressions"]),
                "position": round(r["position"], 1),
            }
            for r in pages_resp.get("rows", [])
        ]

        logger.info(
            "Search Console fetched: clicks=%d impressions=%d avg_pos=%.1f",
            total_clicks,
            total_impressions,
            avg_position,
        )

        return {
            "total_clicks": total_clicks,
            "total_impressions": total_impressions,
            "avg_ctr_pct": avg_ctr,
            "avg_position": avg_position,
            "top_queries": top_queries,
            "top_pages": top_pages,
            "site_url": site_url,
            "date_from": date_from,
            "date_to": date_to,
        }
