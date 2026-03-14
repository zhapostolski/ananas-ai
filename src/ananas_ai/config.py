from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(rel_path: str) -> dict[str, Any]:
    path = project_root() / rel_path
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


@dataclass(frozen=True)
class Settings:
    project_overview: dict[str, Any]
    agents: dict[str, Any]
    model_routing: dict[str, Any]
    schedules: dict[str, Any]
    integrations: dict[str, Any]
    metrics: dict[str, Any]
    output_channels: dict[str, Any]


def load_settings() -> Settings:
    return Settings(
        project_overview=load_json("config/project-overview.json"),
        agents=load_json("config/agents.json"),
        model_routing=load_json("config/model-routing.json"),
        schedules=load_json("config/schedules.json"),
        integrations=load_json("config/integrations-matrix.json"),
        metrics=load_json("config/metrics.json"),
        output_channels=load_json("config/output-channels.json"),
    )


def load_agent_channels() -> dict[str, tuple[str, str]]:
    """Return {agent_name: (channel, display_title)} from output-channels.json."""
    channels = load_json("config/output-channels.json")
    result: dict[str, tuple[str, str]] = {}
    for _key, cfg in channels.get("teams_channels", {}).items():
        agent = cfg.get("agent")
        if agent:
            result[agent] = (cfg["channel"], cfg["display_title"])
    return result
