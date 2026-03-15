"""Meeting Intelligence Agent - transcript processing, summaries, Jira tasks.

On-demand agent triggered by file upload (audio or transcript).
Uses OpenAI Whisper for audio transcription, then Claude for structured
summary extraction and action item identification.

Phase 1: accepts .txt transcripts directly (no Whisper needed).
Phase 2: add audio file processing (Whisper via OPENAI_API_KEY).
"""

from __future__ import annotations

import os
from datetime import date
from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

SAMPLE_MEETING_SUMMARY: dict[str, Any] = {
    "meeting_topic": "Q2 Marketing Planning -- Sample",
    "meeting_date": str(date.today()),
    "participants": ["Zharko A.", "Denis K.", "Ana M.", "Stefan P."],
    "duration_minutes": 45,
    "key_decisions": [
        "Launch Google Shopping pilot in Q2 with top 5,000 Electronics SKUs",
        "Activate cart recovery email flow by end of March (CRM team owner: Ana)",
        "Freeze new coupon campaigns until promo-simulator approval is in place",
    ],
    "action_items": [
        {
            "action": "Set up Google Merchant Center account",
            "owner": "Stefan P.",
            "due": "2026-03-22",
            "jira_key": None,
        },
        {
            "action": "Brief CRM agency on cart recovery requirements",
            "owner": "Ana M.",
            "due": "2026-03-18",
            "jira_key": None,
        },
        {
            "action": "Share promo-simulator output for upcoming Easter campaign",
            "owner": "Zharko A.",
            "due": "2026-03-20",
            "jira_key": None,
        },
        {
            "action": "Review Trustpilot response templates draft",
            "owner": "Denis K.",
            "due": "2026-03-17",
            "jira_key": None,
        },
    ],
    "next_meeting": "2026-03-29",
    "confluence_saved": False,
    "jira_tasks_created": 0,
}


class MeetingIntelligenceAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="meeting-intelligence-agent",
            module_name="meeting-intelligence",
            output_type="on-demand-analysis",
        )

    def _whisper_configured(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))

    def _jira_configured(self) -> bool:
        return bool(os.environ.get("JIRA_BASE_URL") and os.environ.get("JIRA_API_TOKEN"))

    def sample_summary(self) -> dict:
        return {
            **SAMPLE_MEETING_SUMMARY,
            "headline": "Meeting Intelligence (sample) -- upload a transcript to process a real meeting",
        }

    def process_transcript(self, transcript_text: str, meeting_topic: str = "Meeting") -> dict:
        """Process a text transcript and extract structured summary + action items."""
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        logger.info(
            "meeting-intelligence-agent: processing transcript (%d chars)", len(transcript_text)
        )

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Meeting Intelligence Agent. "
            "Extract structured information from meeting transcripts for the Ananas marketing team. "
            "Ananas is North Macedonia's largest e-commerce marketplace. "
            "Output format (JSON): "
            '{"meeting_topic": str, "meeting_date": str, "participants": [str], '
            '"key_decisions": [str], "action_items": [{"action": str, "owner": str, "due": str}], '
            '"next_meeting": str or null} '
            "Rules: "
            "- Never fabricate participants -- only include those mentioned by name. "
            "- Flag unclear sections as [inaudible]. "
            "- Action items must have a clear owner. If owner is unclear, write 'TBD'. "
            "- Keep decisions concise (one sentence each). "
            "- Output valid JSON only, no markdown."
        )
        user = f"Meeting topic: {meeting_topic}\n\nTranscript:\n{transcript_text}"

        result = call_model(route.model, system, user)

        import json

        extracted: dict = {}
        try:
            extracted = json.loads(result["text"])
        except json.JSONDecodeError:
            extracted = {
                "raw_analysis": result["text"],
                "parse_error": "Could not parse JSON from model output",
            }

        extracted["model_used"] = result["model_used"]
        extracted["tokens_in"] = result["tokens_in"]
        extracted["tokens_out"] = result["tokens_out"]
        extracted["estimated_cost"] = result["estimated_cost"]
        extracted["sources_live"] = True
        extracted["headline"] = (
            f"Meeting processed: {meeting_topic} -- {len(extracted.get('action_items', []))} action items"
        )
        return extracted

    def run(self, date_from: str, date_to: str) -> dict:
        logger.warning(
            "meeting-intelligence-agent: no transcript provided, returning sample summary"
        )
        raw = self.sample_summary()
        raw["model_used"] = "none"
        raw["tokens_in"] = 0
        raw["tokens_out"] = 0
        raw["estimated_cost"] = 0.0
        raw["sources_live"] = False
        return raw
