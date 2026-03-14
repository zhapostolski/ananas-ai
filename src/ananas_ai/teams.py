from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def post_message(channel: str, title: str, body: str) -> dict:
    out_dir = Path(__file__).resolve().parents[2] / "examples" / "sample_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"teams_{channel.strip('#')}_{ts}.md"
    path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
    return {"status": "ok", "channel": channel, "path": str(path)}
