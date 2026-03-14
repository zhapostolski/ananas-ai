"""Email delivery via AWS SES.

Sends the daily brief using AWS SES -- no extra credentials needed beyond
the IAM role already attached to EC2 (or AWS_* env vars locally).

Required env vars:
  EMAIL_FROM_ADDRESS  -- verified SES sender (e.g. zharko.apostolski@ananas.mk)
  EMAIL_TO_ADDRESS    -- comma-separated recipients

The sender address must be verified in SES. Run once to verify:
  aws ses verify-email-identity --email-address your@email.com --region eu-central-1
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

SES_REGION = os.environ.get("AWS_REGION", "eu-central-1")


def is_configured() -> bool:
    return bool(os.environ.get("EMAIL_FROM_ADDRESS") and os.environ.get("EMAIL_TO_ADDRESS"))


def send_brief(title: str, body: str, today: date | None = None) -> dict:
    """Send the daily brief email via SES.

    Falls back to writing a local file if not configured or send fails.
    """
    if today is None:
        today = date.today()

    subject = f"{title} -- {today.strftime('%Y-%m-%d')}"

    if not is_configured():
        return _write_local(subject, body)

    from_addr = os.environ["EMAIL_FROM_ADDRESS"]
    to_addrs = [a.strip() for a in os.environ["EMAIL_TO_ADDRESS"].split(",") if a.strip()]

    try:
        import boto3  # noqa: PLC0415

        ses = boto3.client("ses", region_name=SES_REGION)
        html_body = "<br>".join(body.splitlines())

        resp = ses.send_email(
            Source=from_addr,
            Destination={"ToAddresses": to_addrs},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Html": {"Data": html_body, "Charset": "UTF-8"},
                    "Text": {"Data": body, "Charset": "UTF-8"},
                },
            },
        )
        msg_id = resp["MessageId"]
        logger.info("email: sent to %s (MessageId: %s)", to_addrs, msg_id)
        return {"status": "ok", "recipients": to_addrs, "message_id": msg_id}
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
