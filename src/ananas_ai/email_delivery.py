"""Email delivery via Microsoft Graph API (delegated auth).

Uses a stored refresh token to send email as the configured user.
No admin consent needed - only user-level Mail.Send permission.

Required env vars:
  GRAPH_TENANT_ID       -- Azure tenant ID
  GRAPH_CLIENT_ID       -- App registration client ID (public client, no secret needed)
  GRAPH_REFRESH_TOKEN   -- Long-lived refresh token (get once via scripts/get_graph_token.py)
  EMAIL_FROM_ADDRESS    -- sender address (e.g. zharko.apostolski@ananas.mk)
  EMAIL_TO_ADDRESS      -- comma-separated recipients

One-time setup:
  1. Add Delegated permissions to the app: Mail.Send + offline_access
  2. Run: python scripts/get_graph_token.py
  3. Copy GRAPH_REFRESH_TOKEN=... into .env on EC2

Fallback: writes a local file if not configured.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

GRAPH_TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
GRAPH_SEND_URL = "https://graph.microsoft.com/v1.0/users/{user}/sendMail"


def _is_configured() -> bool:
    return bool(
        os.environ.get("GRAPH_TENANT_ID")
        and os.environ.get("GRAPH_CLIENT_ID")
        and os.environ.get("GRAPH_REFRESH_TOKEN")
        and os.environ.get("EMAIL_FROM_ADDRESS")
        and os.environ.get("EMAIL_TO_ADDRESS")
    )


def is_configured() -> bool:
    return _is_configured()


def _clean(text: str) -> str:
    return text.replace("\u2014", "-").replace("\u2013", "-")


def _html(body: str) -> str:
    escaped = body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f"<pre style='font-family:sans-serif;white-space:pre-wrap;font-size:14px'>{escaped}</pre>"
    )


def _get_access_token() -> tuple[str, str | None]:
    """Exchange refresh token for access token. Returns (access_token, new_refresh_token)."""
    tenant_id = os.environ["GRAPH_TENANT_ID"]
    client_id = os.environ["GRAPH_CLIENT_ID"]
    refresh_token = os.environ["GRAPH_REFRESH_TOKEN"]

    data = urllib.parse.urlencode(
        {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": refresh_token,
            "scope": "https://graph.microsoft.com/Mail.Send offline_access",
        }
    ).encode()

    req = urllib.request.Request(
        GRAPH_TOKEN_URL.format(tenant=tenant_id),
        data=data,
        method="POST",
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urllib.request.urlopen(req, timeout=15) as resp:
        token_resp = json.loads(resp.read())

    access_token = token_resp["access_token"]
    # Refresh tokens rotate - update in-memory env so the current process has the latest
    new_refresh = token_resp.get("refresh_token")
    if new_refresh and new_refresh != refresh_token:
        os.environ["GRAPH_REFRESH_TOKEN"] = new_refresh
        logger.debug("email: refresh token rotated")

    return access_token, new_refresh


def _send_graph(subject: str, body: str, from_addr: str, to_addrs: list[str]) -> dict:
    """Send via Microsoft Graph API using delegated (refresh token) auth."""
    access_token, _ = _get_access_token()

    payload = json.dumps(
        {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": _html(body),
                },
                "toRecipients": [{"emailAddress": {"address": a}} for a in to_addrs],
                "from": {"emailAddress": {"address": from_addr, "name": "Ananas AI"}},
            },
            "saveToSentItems": False,
        }
    ).encode()

    req = urllib.request.Request(
        GRAPH_SEND_URL.format(user=from_addr),
        data=payload,
        method="POST",
    )
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, timeout=15) as resp:
        status = resp.status  # 202 Accepted

    logger.info("email: Graph sent to %s (HTTP %s)", to_addrs, status)
    return {"status": "ok", "recipients": to_addrs, "provider": "graph"}


def send_brief(title: str, body: str, today: date | None = None) -> dict:
    """Send the daily brief email via Microsoft Graph API."""
    if today is None:
        today = date.today()

    title = _clean(title)
    body = _clean(body)
    subject = f"{title} -- {today.strftime('%Y-%m-%d')}"

    if not _is_configured():
        return _write_local(subject, body)

    from_addr = os.environ["EMAIL_FROM_ADDRESS"]
    to_addrs = [a.strip() for a in os.environ["EMAIL_TO_ADDRESS"].split(",") if a.strip()]

    try:
        return _send_graph(subject, body, from_addr, to_addrs)
    except Exception as e:
        logger.error("email: Graph send failed: %s", e)
        local = _write_local(subject, body)
        return {"status": "error", "error": str(e), "path": local.get("path")}


def _write_local(subject: str, body: str) -> dict:
    from datetime import datetime, timezone

    out_dir = Path(__file__).resolve().parents[2] / "examples" / "sample_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"email_brief_{ts}.txt"
    path.write_text(f"Subject: {subject}\n\n{body}", encoding="utf-8")
    logger.info("email: wrote %s (not configured)", path.name)
    return {"status": "ok", "path": str(path)}
