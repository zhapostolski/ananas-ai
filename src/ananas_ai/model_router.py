from __future__ import annotations

from dataclasses import dataclass

from .config import load_settings


@dataclass
class RouteDecision:
    model: str
    reason: str


def choose_model(
    agent_name: str, complexity: str = "normal", force_opus: bool = False
) -> RouteDecision:
    settings = load_settings()
    routing = settings.model_routing

    default_model = routing["models"]["default"]["model"]
    escalation_model = routing["models"]["escalation"]["model"]

    # Resolve per-agent assignment if present
    assignment = routing["agent_model_assignments"].get(agent_name, {})
    exec_tier = assignment.get("execution_model", "default")
    agent_model = routing["models"].get(exec_tier, {}).get("model", default_model)

    if force_opus or complexity in {"high", "executive", "deep-dive"}:
        return RouteDecision(model=escalation_model, reason="Escalation for high complexity")

    return RouteDecision(model=agent_model, reason="Default execution path")
