from ananas_ai.agents.base import BaseAgent


class CRMLifecycleAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="crm-lifecycle-agent", module_name="crm-lifecycle")

    def sample_summary(self) -> dict:
        return {
            "headline": "CRM & Lifecycle summary",
            "journeys": ["abandoned-cart", "wish-list", "welcome", "birthday"],
            "notes": [
                "Journey implementation should prioritize measurable recovery impact.",
                "Birthday journey depends on profile field capture and lock rules.",
            ],
        }
