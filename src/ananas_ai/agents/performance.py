from ananas_ai.agents.base import BaseAgent


class PerformanceAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="performance-agent", module_name="performance")

    def sample_summary(self) -> dict:
        return {
            "headline": "Paid performance summary",
            "channels": ["google-ads", "meta-ads", "tiktok-ads", "linkedin-ads"],
            "notes": [
                "Check coupon dependency before over-attributing demand to paid media.",
                "Not all campaigns are currently analyzed; learning quality may be incomplete.",
            ],
        }
