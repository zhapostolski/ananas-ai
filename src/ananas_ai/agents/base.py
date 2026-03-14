from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ananas_ai.model_router import choose_model


@dataclass
class BaseAgent:
    name: str
    module_name: str
    output_type: str = "daily-summary"

    def sample_summary(self) -> dict[str, Any]:
        return {}

    def run(self, date_from: str, date_to: str) -> dict[str, Any]:
        return self.sample_summary()

    def build_payload(
        self, data: dict[str, Any], date_from: str, date_to: str, complexity: str = "normal"
    ) -> dict[str, Any]:
        route = choose_model(self.name, complexity=complexity)
        return {
            "agent_name": self.name,
            "module_name": self.module_name,
            "output_type": self.output_type,
            "date_from": date_from,
            "date_to": date_to,
            "model_used": route.model,
            "version": "brand-new",
            "data": data,
        }
