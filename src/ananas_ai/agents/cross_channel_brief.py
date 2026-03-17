"""Cross-Channel Brief Agent - synthesises all specialist outputs into one executive brief."""

from __future__ import annotations

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)


class CrossChannelBriefAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="cross-channel-brief-agent", module_name="cross-channel-brief", output_type="brief"
        )

    def build_from_specialists(self, specialist_outputs: list[dict]) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        # Extract analysis text or headline from each specialist
        summaries = []
        for o in specialist_outputs:
            data = o.get("data", {})
            agent = o.get("agent_name", "unknown")
            text = data.get("analysis") or data.get("headline") or ""
            if text:
                summaries.append(f"## {agent}\n{text}")

        combined = "\n\n".join(summaries) if summaries else "No specialist data available."

        route = choose_model(self.name, complexity="high")
        system = (
            "You are the Ananas AI Cross-Channel Brief Agent. Ananas is North Macedonia's largest "
            "e-commerce marketplace (250k+ products, 8-person marketing team). "
            "You receive daily briefings from 4 specialist agents and synthesise them into "
            "one concise executive brief for Denis (CMO) and the marketing team. "
            "Known critical issues always worth flagging: "
            "Google Shopping has ZERO campaigns, Trustpilot 2.0 unclaimed, "
            "no lifecycle automations, heavy coupon dependency. "
            "Format: "
            "1. Overall status (1 line) "
            "2. Top 3 highlights across all channels "
            "3. Top 3 risks or gaps "
            "4. Priority actions for today (max 3) "
            "Keep it under 300 words. Executive audience."
        )
        user = f"Specialist briefings:\n\n{combined}\n\nWrite the cross-channel executive brief."

        headline = "Cross-channel marketing brief"
        analysis = ""

        tokens_in, tokens_out, cost = 0, 0, 0.0
        try:
            result = call_model(route.model, system, user)
            analysis = result["text"]
            headline = analysis.split("\n")[0][:100] if analysis else headline
            tokens_in = result["tokens_in"]
            tokens_out = result["tokens_out"]
            cost = result["estimated_cost"]
            logger.info(
                "cross-channel-brief-agent: synthesis complete (%d chars, %d tokens, $%.4f)",
                len(analysis),
                tokens_in + tokens_out,
                cost,
            )
        except Exception as e:
            logger.error("cross-channel-brief-agent: model call failed: %s", e)
            analysis = "Cross-channel brief - model unavailable. Check agent logs."

        # Translate to Macedonian and Serbian for multilingual output
        analysis_mk: str = ""
        analysis_sr: str = ""
        try:
            from ananas_ai.translation import translate_report

            analysis_mk = translate_report(analysis, "mk")
            analysis_sr = translate_report(analysis, "sr")
            logger.info("cross-channel-brief-agent: translations complete (MK, SR)")
        except Exception as e:
            logger.warning("cross-channel-brief-agent: translation failed: %s", e)

        return {
            "headline": headline,
            "analysis": analysis,
            "analysis_mk": analysis_mk,
            "analysis_sr": analysis_sr,
            "source_agents": [o.get("agent_name") for o in specialist_outputs],
            "sources_with_live_data": [
                o.get("agent_name")
                for o in specialist_outputs
                if o.get("data", {}).get("sources_active")
            ],
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "estimated_cost": cost,
        }
