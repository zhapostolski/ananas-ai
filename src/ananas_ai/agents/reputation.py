from ananas_ai.agents.base import BaseAgent

class ReputationAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="reputation-agent", module_name="reputation")

    def sample_summary(self) -> dict:
        return {
            "headline": "Reputation summary",
            "sources": ["trustpilot", "google-business"],
            "notes": [
                "Review monitoring should be tied to customer support themes.",
                "Escalate sharp negative sentiment changes immediately."
            ]
        }
