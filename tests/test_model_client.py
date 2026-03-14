"""Tests for model_client — token tracking, fallback, cost estimation, cap warnings."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ananas_ai.model_client import call_model, estimate_cost

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_anthropic_response(text: str, tokens_in: int = 100, tokens_out: int = 200) -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text
    msg = MagicMock()
    msg.content = [block]
    msg.usage.input_tokens = tokens_in
    msg.usage.output_tokens = tokens_out
    return msg


def _make_openai_response(text: str, tokens_in: int = 80, tokens_out: int = 120) -> MagicMock:
    resp = MagicMock()
    resp.choices[0].message.content = text
    resp.usage.prompt_tokens = tokens_in
    resp.usage.completion_tokens = tokens_out
    return resp


# ── estimate_cost ─────────────────────────────────────────────────────────────


def test_estimate_cost_sonnet():
    # 1000 in + 1000 out at $3.00/$15.00 per MTok
    # = (1000*3 + 1000*15) / 1_000_000 = 18_000 / 1_000_000 = $0.018
    cost = estimate_cost("claude-sonnet-4-5", 1000, 1000)
    assert abs(cost - 0.018) < 1e-9


def test_estimate_cost_opus():
    # 1000 in + 1000 out at $5.00/$25.00 per MTok
    # = (1000*5 + 1000*25) / 1_000_000 = 30_000 / 1_000_000 = $0.030
    cost = estimate_cost("claude-opus-4-5", 1000, 1000)
    assert abs(cost - 0.030) < 1e-9


def test_estimate_cost_gpt4o_mini():
    # 1000 in + 1000 out at $0.15/$0.60 per MTok
    # = (1000*0.15 + 1000*0.60) / 1_000_000 = 750 / 1_000_000 = $0.00075
    cost = estimate_cost("gpt-4o-mini", 1000, 1000)
    assert abs(cost - 0.00075) < 1e-9


def test_estimate_cost_zero_tokens():
    assert estimate_cost("claude-sonnet-4-5", 0, 0) == 0.0


# ── call_model — Claude success path ─────────────────────────────────────────


def test_call_model_returns_token_counts(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_anthropic_response(
        "hello", tokens_in=500, tokens_out=300
    )
    with patch("anthropic.Anthropic", return_value=mock_client):
        result = call_model("claude-sonnet-4-5", "system", "user")

    assert result["text"] == "hello"
    assert result["model_used"] == "claude-sonnet-4-5"
    assert result["fallback"] is False
    assert result["tokens_in"] == 500
    assert result["tokens_out"] == 300
    assert result["estimated_cost"] > 0


def test_call_model_estimated_cost_matches_formula(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _make_anthropic_response(
        "x", tokens_in=1000, tokens_out=1000
    )
    with patch("anthropic.Anthropic", return_value=mock_client):
        result = call_model("claude-sonnet-4-5", "s", "u")

    expected = estimate_cost("claude-sonnet-4-5", 1000, 1000)
    assert abs(result["estimated_cost"] - expected) < 1e-9


# ── call_model — Claude → OpenAI fallback ────────────────────────────────────


def test_call_model_falls_back_to_openai_on_claude_error(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-oai-test")

    # Patch at the module level — avoids needing openai installed locally
    with (
        patch("ananas_ai.model_client._call_claude", side_effect=RuntimeError("rate limit")),
        patch(
            "ananas_ai.model_client._call_openai",
            return_value=("fallback response", 80, 120),
        ),
    ):
        result = call_model("claude-sonnet-4-5", "system", "user")

    assert result["fallback"] is True
    assert result["model_used"] == "gpt-4.1"
    assert result["text"] == "fallback response"
    assert result["tokens_in"] == 80
    assert result["tokens_out"] == 120


def test_fallback_not_triggered_when_disallowed(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-oai-test")

    with (
        patch("ananas_ai.model_client._call_claude", side_effect=RuntimeError("down")),
        pytest.raises(RuntimeError, match="No model available"),
    ):
        call_model("claude-sonnet-4-5", "s", "u", allow_fallback=False)


def test_no_keys_raises_runtime_error(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="No model available"):
        call_model("claude-sonnet-4-5", "system", "user")


# ── per-run cap warning ───────────────────────────────────────────────────────


def test_per_run_cap_exceeded_logs_warning(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    # 60k tokens exceeds 50k Sonnet cap
    with patch(
        "ananas_ai.model_client._call_claude",
        return_value=("big response", 40_000, 20_000),
    ):
        import ananas_ai.model_client as mc

        with patch.object(mc.logger, "warning") as mock_warn:
            result = call_model("claude-sonnet-4-5", "s", "u")

    assert result["tokens_in"] == 40_000
    # warning should have been called with the cap exceeded message
    warning_messages = " ".join(str(c) for c in mock_warn.call_args_list).lower()
    assert "cap exceeded" in warning_messages


def test_per_run_cap_not_warned_when_within_limit(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    with patch(
        "ananas_ai.model_client._call_claude",
        return_value=("small", 100, 200),
    ):
        import ananas_ai.model_client as mc

        with patch.object(mc.logger, "warning") as mock_warn:
            call_model("claude-sonnet-4-5", "s", "u")

    warning_messages = " ".join(str(c) for c in mock_warn.call_args_list).lower()
    assert "cap exceeded" not in warning_messages


# ── OpenAI-only path ─────────────────────────────────────────────────────────


def test_openai_only_no_anthropic_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-oai-test")

    with patch("ananas_ai.model_client._call_openai", return_value=("oai only", 50, 100)):
        result = call_model("claude-sonnet-4-5", "s", "u")

    assert result["fallback"] is True
    assert result["tokens_in"] == 50
    assert result["tokens_out"] == 100
