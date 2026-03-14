from ananas_ai.agents.base import BaseAgent


class CrossChannelBriefAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="cross-channel-brief-agent", module_name="cross-channel-brief", output_type="brief"
        )

    def build_from_specialists(self, specialist_outputs: list[dict]) -> dict:
        headlines = [o["data"].get("headline") for o in specialist_outputs if o.get("data")]
        return {
            "headline": "Cross-channel marketing brief",
            "source_headlines": headlines,
            "summary": "Daily summary synthesized from phase 1 specialist agents.",
            "priority_flags": [
                "Investigate coupon dependence on revenue quality.",
                "Improve campaign analysis discipline.",
                "Clarify role ownership and accountability.",
            ],
        }
