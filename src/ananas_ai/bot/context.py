"""Load agent output context from DB for the Teams bot."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone

from ananas_ai.config import project_root

PHASE1_AGENTS = [
    ("performance-agent", "Performance & Paid Media"),
    ("crm-lifecycle-agent", "CRM & Lifecycle"),
    ("reputation-agent", "Reputation"),
    ("marketing-ops-agent", "Marketing Ops"),
    ("cross-channel-brief-agent", "Cross-Channel Brief"),
]


def _db_path() -> str:
    import os

    return os.environ.get("ANANAS_DB_PATH", str(project_root() / "ananas_ai_dev.db"))


def load_context(lookback_days: int = 2) -> str:
    """Return a compact text block summarising the latest agent outputs.

    The bot feeds this into Claude's system prompt so it can answer
    questions grounded in real data without hallucinating.
    """
    since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )

    try:
        conn = sqlite3.connect(_db_path())
        sections: list[str] = []

        for agent_id, label in PHASE1_AGENTS:
            row = conn.execute(
                """
                SELECT data_json, created_at, model_used
                FROM agent_outputs
                WHERE agent_name = ? AND created_at >= ?
                ORDER BY id DESC LIMIT 1
                """,
                (agent_id, since),
            ).fetchone()

            if not row:
                sections.append(f"## {label}\nNo recent data (last {lookback_days} days).")
                continue

            data_json, created_at, model_used = row
            try:
                data = json.loads(data_json)
            except Exception:
                data = {}

            # Extract the most useful fields
            analysis = data.get("analysis", data.get("headline", ""))
            summary = data.get("summary", {})

            lines = [f"## {label} (run: {created_at[:16]} UTC)"]
            if analysis:
                lines.append(analysis[:800])  # cap to keep context manageable

            # Append key numeric fields from summary dict if present
            if isinstance(summary, dict):
                for k, v in list(summary.items())[:8]:
                    if v not in (None, 0, ""):
                        lines.append(f"- {k}: {v}")

            sections.append("\n".join(lines))

        conn.close()
        return "\n\n".join(sections) if sections else "No agent data available yet."

    except Exception as exc:
        return f"(Context unavailable: {exc})"
