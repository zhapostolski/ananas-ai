"""Email delivery via Microsoft Graph API.

Sends the daily brief to configured recipients using the same Azure AD
app registration as Teams (TEAMS_CLIENT_ID / TEAMS_CLIENT_SECRET / TEAMS_TENANT_ID).

Required env vars:
  TEAMS_CLIENT_ID       -- Azure AD app client ID
  TEAMS_CLIENT_SECRET   -- Azure AD app client secret
  TEAMS_TENANT_ID       -- Azure AD tenant ID
  OUTLOOK_FROM_ADDRESS  -- sender address (must be a mailbox the app has Mail.Send for)
  OUTLOOK_TO_ADDRESS    -- comma-separated recipient addresses

The Azure AD app must have the Graph API application permission: Mail.Send
"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

GRAPH_TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
GRAPH_SEND_URL = "https://graph.microsoft.com/v1.0/users/{sender}/sendMail"


def is_configured() -> bool:
    required = [
        "TEAMS_CLIENT_ID",
        "TEAMS_CLIENT_SECRET",
        "TEAMS_TENANT_ID",
        "OUTLOOK_FROM_ADDRESS",
        "OUTLOOK_TO_ADDRESS",
    ]
    return all(os.environ.get(k) for k in required)


def _get_token() -> str:
    import requests  # noqa: PLC0415

    tenant = os.environ["TEAMS_TENANT_ID"]
    resp = requests.post(
        GRAPH_TOKEN_URL.format(tenant=tenant),
        data={
            "grant_type": "client_credentials",
            "client_id": os.environ["TEAMS_CLIENT_ID"],
            "client_secret": os.environ["TEAMS_CLIENT_SECRET"],
            "scope": "https://graph.microsoft.com/.default",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]  # type: ignore[no-any-return]


def _build_payload(subject: str, body_text: str, to_addresses: list[str]) -> dict:
    html_body = "<br>".join(body_text.splitlines())
    return {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "toRecipients": [
                {"emailAddress": {"address": addr}} for addr in to_addresses
            ],
        },
        "saveToSentItems": "false",
    }


def send_brief(title: str, body: str, today: date | None = None) -> dict:
    """Send the daily brief email.

    Falls back to writing a local file if not configured or if the send fails.
    """
    if today is None:
        today = date.today()

    subject = f"{title} -- {today.strftime('%Y-%m-%d')}"

    if not is_configured():
        return _write_local(subject, body)

    from_addr = os.environ["OUTLOOK_FROM_ADDRESS"]
    to_addrs = [a.strip() for a in os.environ["OUTLOOK_TO_ADDRESS"].split(",") if a.strip()]

    try:
        import requests  # noqa: PLC0415

        token = _get_token()
        payload = _build_payload(subject, body, to_addrs)
        resp = requests.post(
            GRAPH_SEND_URL.format(sender=from_addr),
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        logger.info("email: sent to %s (HTTP %s)", to_addrs, resp.status_code)
        return {"status": "ok", "recipients": to_addrs, "http_status": resp.status_code}
    except Exception as e:
        logger.error("email: send failed: %s", e)
        local = _write_local(subject, body)
        return {"status": "error", "error": str(e), "path": local.get("path")}


def _write_local(subject: str, body: str) -> dict:
    out_dir = Path(__file__).resolve().parents[2] / "examples" / "sample_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"email_brief_{ts}.txt"
    path.write_text(f"Subject: {subject}\n\n{body}", encoding="utf-8")
    logger.info("email: wrote %s (not configured)", path.name)
    return {"status": "ok", "path": str(path)}
