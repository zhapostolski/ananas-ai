"""Microsoft Teams output — writes formatted cards to file or posts via webhook."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)


def _build_card(title: str, body: str) -> dict:
    """Build a minimal Teams Adaptive Card payload."""
    lines = body.strip().split("\n")
    facts = []
    plain_lines = []

    for line in lines:
        # Lines like "- Key: value" become facts in a FactSet
        if line.startswith("- ") and ": " in line:
            parts = line[2:].split(": ", 1)
            facts.append({"title": parts[0].strip(), "value": parts[1].strip()})
        else:
            plain_lines.append(line)

    body_items: list[dict] = []

    if plain_lines:
        body_items.append({
            "type": "TextBlock",
            "text": "\n".join(plain_lines).strip(),
            "wrap": True,
            "size": "Small",
        })

    if facts:
        body_items.append({
            "type": "FactSet",
            "facts": facts,
        })

    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": title,
                            "weight": "Bolder",
                            "size": "Medium",
                            "wrap": True,
                        },
                        *body_items,
                    ],
                },
            }
        ],
    }


def post_message(channel: str, title: str, body: str) -> dict:
    """Post a message to a Teams channel.

    If TEAMS_WEBHOOK_URL is configured, POSTs to Teams.
    Always writes a local file for debugging / local dev.
    """
    webhook_url = os.environ.get("TEAMS_WEBHOOK_URL", "")
    card = _build_card(title, body)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # Write local file
    out_dir = Path(__file__).resolve().parents[2] / "examples" / "sample_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"teams_{channel.strip('#')}_{ts}.json"
    path.write_text(json.dumps(card, indent=2, ensure_ascii=False), encoding="utf-8")

    if webhook_url:
        try:
            import requests  # noqa: PLC0415

            resp = requests.post(webhook_url, json=card, timeout=15)
            resp.raise_for_status()
            logger.info("teams: posted to %s (HTTP %s)", channel, resp.status_code)
            return {"status": "ok", "channel": channel, "http_status": resp.status_code}
        except Exception as e:
            logger.error("teams: webhook post failed for %s: %s", channel, e)
            return {"status": "error", "channel": channel, "error": str(e)}

    logger.info("teams: wrote %s (no webhook configured)", path.name)
    return {"status": "ok", "channel": channel, "path": str(path)}
