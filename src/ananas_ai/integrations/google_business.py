"""Google Business Profile integration -- reviews, rating, and sentiment data.

Required env vars:
  GA4_CREDENTIALS        -- path to Google service account JSON (shared with GA4)
  GBP_ACCOUNT_ID         -- Google Business Profile account ID (e.g. accounts/123456789)
  GBP_LOCATION_ID        -- Location numeric ID (e.g. 987654321, without "locations/" prefix)

The service account must be added as a Manager in business.google.com for the
location. Uses the current mybusinessreviews v1 API (mybusiness v4 is deprecated).
"""

from __future__ import annotations

import os

from ananas_ai.integrations.base import BaseIntegration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

_REVIEWS_DISCOVERY = "https://mybusinessreviews.googleapis.com/$discovery/rest?version=v1"


class GoogleBusinessIntegration(BaseIntegration):
    name = "google-business-profile"

    def is_configured(self) -> bool:
        creds = os.environ.get("GA4_CREDENTIALS")
        account = os.environ.get("GBP_ACCOUNT_ID")
        location = os.environ.get("GBP_LOCATION_ID")
        if not (creds and account and location):
            return False
        from pathlib import Path

        return Path(creds).exists()

    def fetch(self, date_from: str, date_to: str) -> dict:
        from google.oauth2 import service_account  # type: ignore[import]
        from googleapiclient.discovery import build  # type: ignore[import]

        creds_path = os.environ["GA4_CREDENTIALS"]
        raw_location = os.environ["GBP_LOCATION_ID"]
        location_id = raw_location.removeprefix("locations/")

        scopes = ["https://www.googleapis.com/auth/business.manage"]
        credentials = service_account.Credentials.from_service_account_file(
            creds_path, scopes=scopes
        )

        service = build(
            "mybusinessreviews",
            "v1",
            credentials=credentials,
            discoveryServiceUrl=_REVIEWS_DISCOVERY,
            cache_discovery=False,
        )

        location_name = f"locations/{location_id}"

        reviews_resp = (
            service.locations().reviews().list(parent=location_name, pageSize=50).execute()
        )

        reviews = reviews_resp.get("reviews", [])
        total = reviews_resp.get("totalReviewCount", len(reviews))
        avg_rating = reviews_resp.get("averageRating", 0.0)

        recent = []
        for r in reviews[:10]:
            recent.append(
                {
                    "rating": r.get("starRating", ""),
                    "comment": r.get("comment", "")[:200],
                    "reply": bool(r.get("reviewReply")),
                    "create_time": r.get("createTime", ""),
                }
            )

        unanswered = sum(1 for r in reviews if not r.get("reviewReply"))

        logger.info(
            "Google Business fetched: rating=%.1f total=%d unanswered=%d",
            avg_rating,
            total,
            unanswered,
        )

        return {
            "average_rating": avg_rating,
            "total_reviews": total,
            "unanswered_reviews": unanswered,
            "response_rate_pct": round((1 - unanswered / max(len(reviews), 1)) * 100, 1),
            "recent_reviews": recent,
            "date_from": date_from,
            "date_to": date_to,
        }
