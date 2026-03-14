"""Tests for all five Phase 1 agents — sample_summary + build_payload."""

from __future__ import annotations

import pytest

from ananas_ai.agents.crm_lifecycle import CRMLifecycleAgent
from ananas_ai.agents.cross_channel_brief import CrossChannelBriefAgent
from ananas_ai.agents.marketing_ops import MarketingOpsAgent
from ananas_ai.agents.performance import PerformanceAgent
from ananas_ai.agents.reputation import ReputationAgent
from ananas_ai.validator import validate_agent_output

TODAY = "2026-03-14"

AGENT_CLASSES = [
    PerformanceAgent,
    CRMLifecycleAgent,
    ReputationAgent,
    MarketingOpsAgent,
]


@pytest.mark.parametrize("cls", AGENT_CLASSES)
def test_sample_summary_returns_dict(cls):
    agent = cls()
    result = agent.sample_summary()
    assert isinstance(result, dict)


@pytest.mark.parametrize("cls", AGENT_CLASSES)
def test_build_payload_passes_validation(cls):
    agent = cls()
    payload = agent.build_payload(agent.sample_summary(), TODAY, TODAY)
    errors = validate_agent_output(payload)
    assert errors == [], f"{cls.__name__} validation errors: {errors}"


@pytest.mark.parametrize("cls", AGENT_CLASSES)
def test_payload_has_required_keys(cls):
    agent = cls()
    payload = agent.build_payload(agent.sample_summary(), TODAY, TODAY)
    for key in (
        "agent_name",
        "module_name",
        "output_type",
        "date_from",
        "date_to",
        "data",
        "model_used",
    ):
        assert key in payload, f"{cls.__name__} missing key: {key}"


def test_cross_channel_brief_builds_from_specialists():
    brief = CrossChannelBriefAgent()
    specialists = [
        PerformanceAgent().build_payload(PerformanceAgent().sample_summary(), TODAY, TODAY),
        CRMLifecycleAgent().build_payload(CRMLifecycleAgent().sample_summary(), TODAY, TODAY),
        ReputationAgent().build_payload(ReputationAgent().sample_summary(), TODAY, TODAY),
        MarketingOpsAgent().build_payload(MarketingOpsAgent().sample_summary(), TODAY, TODAY),
    ]
    data = brief.build_from_specialists(specialists)
    assert isinstance(data, dict)


def test_cross_channel_brief_payload_valid():
    brief = CrossChannelBriefAgent()
    specialists = [
        PerformanceAgent().build_payload(PerformanceAgent().sample_summary(), TODAY, TODAY),
        CRMLifecycleAgent().build_payload(CRMLifecycleAgent().sample_summary(), TODAY, TODAY),
        ReputationAgent().build_payload(ReputationAgent().sample_summary(), TODAY, TODAY),
        MarketingOpsAgent().build_payload(MarketingOpsAgent().sample_summary(), TODAY, TODAY),
    ]
    data = brief.build_from_specialists(specialists)
    payload = brief.build_payload(data, TODAY, TODAY, complexity="high")
    errors = validate_agent_output(payload)
    assert errors == []
