from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone

from .config import project_root
from .logging_config import get_logger

logger = get_logger(__name__)


def _db_path() -> str:
    """Return DB path from env (allows tests to inject :memory: or a tmp file)."""
    return os.environ.get("ANANAS_DB_PATH", str(project_root() / "ananas_ai_dev.db"))


def get_conn() -> sqlite3.Connection:
    return sqlite3.connect(_db_path())


def bootstrap() -> None:
    sql = (project_root() / "sql" / "schema.sql").read_text(encoding="utf-8")
    conn = get_conn()
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def insert_agent_output(payload: dict) -> int:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO agent_outputs (agent_name,module_name,output_type,scope_type,scope_value,date_from,date_to,data_json,version,model_used,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                payload["agent_name"],
                payload["module_name"],
                payload["output_type"],
                payload.get("scope_type"),
                payload.get("scope_value"),
                payload["date_from"],
                payload["date_to"],
                json.dumps(payload["data"]),
                payload.get("version"),
                payload.get("model_used"),
                now_iso(),
            ),
        )
        conn.commit()
        return int(cur.lastrowid or 0)
    finally:
        conn.close()


def log_agent_run(
    agent_name: str,
    run_type: str,
    model_used: str,
    status: str,
    duration_ms: int = 0,
    error_message: str | None = None,
) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO agent_logs (agent_name,run_type,model_used,tokens_used_input,tokens_used_output,estimated_cost,duration_ms,status,error_message,created_at) VALUES (?,?,?,0,0,0,?,?,?,?)",
            (agent_name, run_type, model_used, duration_ms, status, error_message, now_iso()),
        )
        conn.commit()
    finally:
        conn.close()


def upsert_health(component_name: str, status: str, notes: str = "") -> None:
    conn = get_conn()
    ts = now_iso()
    try:
        conn.execute(
            "INSERT INTO system_health (component_name,status,last_success_at,last_error_at,notes) VALUES (?,?,?,?,?) ON CONFLICT(component_name) DO UPDATE SET status=excluded.status,last_success_at=excluded.last_success_at,notes=excluded.notes",
            (
                component_name,
                status,
                ts if status == "ok" else None,
                ts if status == "error" else None,
                notes,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def fetch_latest_outputs() -> list[tuple]:
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT agent_name,module_name,output_type,created_at FROM agent_outputs ORDER BY id DESC LIMIT 20"
        ).fetchall()
    finally:
        conn.close()
