from __future__ import annotations

from ananas_ai.persistence import (
    bootstrap,
    fetch_latest_outputs,
    insert_agent_output,
    log_agent_run,
    upsert_health,
)

SAMPLE_PAYLOAD = {
    "agent_name": "performance-agent",
    "module_name": "performance",
    "output_type": "daily-summary",
    "date_from": "2026-03-01",
    "date_to": "2026-03-01",
    "data": {"headline": "test"},
    "model_used": "claude-sonnet",
    "version": "test",
}


def test_bootstrap_is_idempotent():
    bootstrap()
    bootstrap()


def test_insert_and_fetch():
    bootstrap()
    insert_agent_output(SAMPLE_PAYLOAD)
    rows = fetch_latest_outputs()
    assert len(rows) >= 1
    assert rows[0][0] == "performance-agent"


def test_log_agent_run_ok():
    bootstrap()
    log_agent_run("performance-agent", "sample", "claude-sonnet", "ok", duration_ms=123)


def test_log_agent_run_error():
    bootstrap()
    log_agent_run("performance-agent", "sample", "claude-sonnet", "error", error_message="oops")


def test_upsert_health_ok():
    bootstrap()
    upsert_health("performance-agent", "ok", "All good")


def test_upsert_health_error():
    bootstrap()
    upsert_health("performance-agent", "error", "Something broke")


def test_upsert_health_idempotent():
    bootstrap()
    upsert_health("reputation-agent", "ok", "First")
    upsert_health("reputation-agent", "ok", "Second")
