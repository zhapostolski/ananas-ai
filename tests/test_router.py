from __future__ import annotations

from ananas_ai.model_router import choose_model


def test_default_route_returns_sonnet():
    result = choose_model("performance-agent")
    assert "sonnet" in result.model.lower()


def test_escalation_returns_opus():
    result = choose_model("cross-channel-brief-agent", complexity="high")
    assert "opus" in result.model.lower()


def test_unknown_agent_falls_back_to_default():
    result = choose_model("nonexistent-agent")
    assert result.model  # just a non-empty string


def test_force_opus_overrides():
    result = choose_model("performance-agent", force_opus=True)
    assert "opus" in result.model.lower()


def test_executive_complexity_escalates():
    result = choose_model("performance-agent", complexity="executive")
    assert "opus" in result.model.lower()
