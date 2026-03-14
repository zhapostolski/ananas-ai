from __future__ import annotations
from pathlib import Path
import json
from dataclasses import dataclass
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()

def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

def load_json(rel_path: str) -> Dict[str, Any]:
    path = project_root() / rel_path
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

@dataclass(frozen=True)
class Settings:
    project_overview: Dict[str, Any]
    agents: Dict[str, Any]
    model_routing: Dict[str, Any]
    schedules: Dict[str, Any]
    integrations: Dict[str, Any]
    metrics: Dict[str, Any]

def load_settings() -> Settings:
    return Settings(
        project_overview=load_json("config/project-overview.json"),
        agents=load_json("config/agents.json"),
        model_routing=load_json("config/model-routing.json"),
        schedules=load_json("config/schedules.json"),
        integrations=load_json("config/integrations-matrix.json"),
        metrics=load_json("config/metrics.json"),
    )
