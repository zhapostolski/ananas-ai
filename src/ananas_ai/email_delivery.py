"""Email delivery via Microsoft Graph API (primary) or AWS SES (fallback).

Primary: Microsoft Graph API using client credentials (app-only auth).
  Sends from ai@ananas.mk using an Entra ID app with Mail.Send permission.

Required env vars for Graph:
  GRAPH_TENANT_ID      -- Azure tenant ID
  GRAPH_CLIENT_ID      -- App registration client ID
  GRAPH_CLIENT_SECRET  -- App registration client secret
  EMAIL_FROM_ADDRESS   -- sender address (e.g. ai@ananas.mk)
  EMAIL_TO_ADDRESS     -- comma-separated recipients

Fallback: AWS SES (used if Graph vars are missing).
  EMAIL_FROM_ADDRESS must be a verified SES sender.

Setup (Graph, one-time):
  1. Create ai@ananas.mk in Microsoft 365 admin
  2. Register an app in Entra ID (no redirect URI needed)
  3. Add API permission: Microsoft Graph > Application > Mail.Send
  4. Grant admin consent
  5. Create a client secret
  6. Set the 4 env vars above
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

SES_REGION = os.environ.get("AWS_REGION", "eu-central-1")


def _is_graph_configured() -> bool:
    return bool(
        os.environ.get("GRAPH_TENANT_ID")
        and os.environ.get("GRAPH_CLIENT_ID")
        and os.environ.get("GRAPH_CLIENT_SECRET")
        and os.environ.get("EMAIL_FROM_ADDRESS")
        and os.environ.get("EMAIL_TO_ADDRESS")
    )


def _is_ses_configured() -> bool:
    return bool(os.environ.get("EMAIL_FROM_ADDRESS") and os.environ.get("EMAIL_TO_ADDRESS"))


def is_configured() -> bool:
    return _is_graph_configured() or _is_ses_configured()


def _clean(text: str) -> str:
    return text.replace("\u2014", "-").replace("\u2013", "-")


def _html(body: str) -> str:
    escaped = body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f"<pre style='font-family:sans-serif;white-space:pre-wrap;font-size:14px'>{escaped}</pre>"
    )


# ---------------------------------------------------------------------------
# Graph API sender
# ---------------------------------------------------------------------------
def _send_graph(subject: str, body: str, from_addr: str, to_addrs: list[str]) -> dict:
    """Send via Microsoft Graph API using client credentials."""
    import json
    import urllib.parse
    import urllib.request

    tenant_id = os.environ["GRAPH_TENANT_ID"]
    client_id = os.environ["GRAPH_CLIENT_ID"]
    client_secret = os.environ["GRAPH_CLIENT_SECRET"]

    # 1. Get access token
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }
    ).encode()

    req = urllib.request.Request(token_url, data=token_data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=15) as resp:
        token_resp = json.loads(resp.read())
    access_token = token_resp["access_token"]

    # 2. Send mail via Graph
    send_url = f"https://graph.microsoft.com/v1.0/users/{from_addr}/sendMail"
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

    req2 = urllib.request.Request(send_url, data=payload, method="POST")
    req2.add_header("Authorization", f"Bearer {access_token}")
    req2.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req2, timeout=15) as resp2:
        # 202 Accepted = success, no body
        status = resp2.status

    logger.info("email: Graph sent to %s (HTTP %s)", to_addrs, status)
    return {"status": "ok", "recipients": to_addrs, "provider": "graph"}


# ---------------------------------------------------------------------------
# SES fallback
# ---------------------------------------------------------------------------
def _send_ses(subject: str, body: str, from_addr: str, to_addrs: list[str]) -> dict:
    """Send via AWS SES."""
    import boto3  # noqa: PLC0415

    ses = boto3.client("ses", region_name=SES_REGION)
    resp = ses.send_email(
        Source=f"Ananas AI <{from_addr}>",
        Destination={"ToAddresses": to_addrs},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {
                "Html": {"Data": _html(body), "Charset": "UTF-8"},
                "Text": {"Data": body, "Charset": "UTF-8"},
            },
        },
    )
    msg_id = resp["MessageId"]
    logger.info("email: SES sent to %s (MessageId: %s)", to_addrs, msg_id)
    return {"status": "ok", "recipients": to_addrs, "message_id": msg_id, "provider": "ses"}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def send_brief(title: str, body: str, today: date | None = None) -> dict:
    """Send the daily brief email.

    Tries Graph API first (ai@ananas.mk), falls back to SES, then writes local file.
    """
    if today is None:
        today = date.today()

    title = _clean(title)
    body = _clean(body)
    subject = f"{title} -- {today.strftime('%Y-%m-%d')}"

    if not is_configured():
        return _write_local(subject, body)

    from_addr = os.environ["EMAIL_FROM_ADDRESS"]
    to_addrs = [a.strip() for a in os.environ["EMAIL_TO_ADDRESS"].split(",") if a.strip()]

    # Try Graph first
    if _is_graph_configured():
        try:
            return _send_graph(subject, body, from_addr, to_addrs)
        except Exception as e:
            logger.warning("email: Graph failed (%s), trying SES fallback", e)

    # SES fallback
    try:
        return _send_ses(subject, body, from_addr, to_addrs)
    except Exception as e:
        logger.error("email: SES also failed: %s", e)
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
