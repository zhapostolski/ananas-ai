from __future__ import annotations
from dataclasses import dataclass
from .config import load_settings

@dataclass
class RouteDecision:
    model: str
    reason: str

def choose_model(agent_name: str, complexity: str = "normal", force_opus: bool = False) -> RouteDecision:
    settings = load_settings()
    default = settings.model_routing["agent_defaults"].get(agent_name, settings.model_routing["default_execution_model"])
    if force_opus or complexity in {"high", "executive", "deep-dive"}:
        return RouteDecision(model=settings.model_routing["escalation_model"], reason="Escalation for high complexity")
    return RouteDecision(model=default, reason="Default execution path")
