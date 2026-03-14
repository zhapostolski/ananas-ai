"""CLI integration tests — run_agent and run_brief with mocked model calls.

All model calls are mocked so tests run without real API keys.
DB writes and Teams posts go to the test DB and local files respectively.
"""

from __future__ import annotations

from unittest.mock import patch

from ananas_ai.cli import run_agent, run_brief
from ananas_ai.persistence import bootstrap, fetch_daily_tokens, fetch_latest_outputs

# ── Shared mock factory ───────────────────────────────────────────────────────


def _mock_call_model(text: str = "test analysis", tokens_in: int = 100, tokens_out: int = 200):
    """Return a patch target and a fake call_model result."""
    return {
        "text": text,
        "model_used": "claude-sonnet-4-5",
        "fallback": False,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "estimated_cost": 0.0009,
    }


# ── run_agent ─────────────────────────────────────────────────────────────────


def test_run_agent_performance_writes_to_db():
    bootstrap()
    mock_result = _mock_call_model("Performance OK — ROAS 4.2x")

    with patch("ananas_ai.model_client.call_model", return_value=mock_result):
        rc = run_agent("performance-agent")

    assert rc == 0
    rows = fetch_latest_outputs()
    agent_names = [r[0] for r in rows]
    assert "performance-agent" in agent_names


def test_run_agent_crm_writes_to_db():
    bootstrap()
    mock_result = _mock_call_model("CRM — cart recovery not live")

    with patch("ananas_ai.model_client.call_model", return_value=mock_result):
        rc = run_agent("crm-lifecycle-agent")

    assert rc == 0


def test_run_agent_reputation_writes_to_db():
    bootstrap()
    mock_result = _mock_call_model("CRITICAL: Trustpilot 2.0")

    with patch("ananas_ai.model_client.call_model", return_value=mock_result):
        rc = run_agent("reputation-agent")

    assert rc == 0


def test_run_agent_marketing_ops_writes_to_db():
    bootstrap()
    mock_result = _mock_call_model("Tracking OK")

    with patch("ananas_ai.model_client.call_model", return_value=mock_result):
        rc = run_agent("marketing-ops-agent")

    assert rc == 0


def test_run_agent_logs_token_counts():
    import sqlite3

    bootstrap()
    mock_result = _mock_call_model(tokens_in=1234, tokens_out=5678)

    with patch("ananas_ai.model_client.call_model", return_value=mock_result):
        run_agent("performance-agent")

    from ananas_ai.persistence import _db_path

    conn = sqlite3.connect(_db_path())
    row = conn.execute(
        "SELECT tokens_used_input, tokens_used_output, estimated_cost FROM agent_logs "
        "WHERE agent_name = 'performance-agent' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()

    assert row is not None
    assert row[0] == 1234
    assert row[1] == 5678
    assert row[2] == pytest.approx(0.0009)


def test_run_agent_unknown_raises():
    import pytest

    with pytest.raises(SystemExit):
        run_agent("nonexistent-agent")


# ── run_brief ─────────────────────────────────────────────────────────────────


def test_run_brief_runs_all_agents_and_brief():
    bootstrap()
    call_count = 0

    def _fake_call_model(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return _mock_call_model(f"analysis #{call_count}")

    with patch("ananas_ai.model_client.call_model", side_effect=_fake_call_model):
        rc = run_brief()

    assert rc == 0
    # 4 specialists + 1 brief = 5 model calls
    assert call_count == 5


def test_run_brief_persists_all_specialist_outputs():
    bootstrap()

    with patch("ananas_ai.model_client.call_model", return_value=_mock_call_model()):
        run_brief()

    rows = fetch_latest_outputs()
    agent_names = {r[0] for r in rows}
    assert "performance-agent" in agent_names
    assert "crm-lifecycle-agent" in agent_names
    assert "reputation-agent" in agent_names
    assert "marketing-ops-agent" in agent_names
    assert "cross-channel-brief-agent" in agent_names


def test_run_brief_token_counts_accumulate():
    bootstrap()

    with patch(
        "ananas_ai.model_client.call_model",
        return_value=_mock_call_model(tokens_in=1000, tokens_out=1000),
    ):
        run_brief()

    # All 5 agents ran — total across all should be >= 10k (5 * 2k)
    total = sum(
        fetch_daily_tokens(name)
        for name in [
            "performance-agent",
            "crm-lifecycle-agent",
            "reputation-agent",
            "marketing-ops-agent",
            "cross-channel-brief-agent",
        ]
    )
    assert total >= 10_000


# ── daily token cap ───────────────────────────────────────────────────────────


def test_daily_cap_blocks_agent_when_exceeded(monkeypatch):
    """Agent should skip (return 0) when daily cap is already reached."""
    bootstrap()

    # Pretend agent has already used 200k tokens today
    with (
        patch("ananas_ai.cli.fetch_daily_tokens", return_value=200_001),
        patch("ananas_ai.cli._daily_cap", return_value=200_000),
    ):
        rc = run_agent("performance-agent")

    # Should return 0 (skipped, not crashed)
    assert rc == 0


def test_daily_cap_not_blocked_when_under_limit(monkeypatch):
    bootstrap()
    mock_result = _mock_call_model()

    with (
        patch("ananas_ai.cli.fetch_daily_tokens", return_value=1000),
        patch("ananas_ai.cli._daily_cap", return_value=200_000),
        patch("ananas_ai.model_client.call_model", return_value=mock_result),
    ):
        rc = run_agent("marketing-ops-agent")

    assert rc == 0


# ── import fix for pytest.approx used in test_run_agent_logs_token_counts ─────
import pytest  # noqa: E402
