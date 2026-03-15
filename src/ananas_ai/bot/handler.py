"""Teams bot message handler -- routes questions to Claude with agent context."""

from __future__ import annotations

import re

from botbuilder.core import ActivityHandler, TurnContext  # type: ignore[import]
from botbuilder.schema import Activity, ActivityTypes  # type: ignore[import]

from ananas_ai.bot.context import load_context
from ananas_ai.logging_config import get_logger
from ananas_ai.model_client import call_model

logger = get_logger(__name__)

SYSTEM_PROMPT = """\
You are the Ananas AI assistant, an internal analytics bot for Ananas, North Macedonia's largest \
e-commerce marketplace with 250k+ products.

You have access to the latest outputs from all AI agents running daily on the platform. \
Answer questions concisely and accurately based on this data. Always cite which agent or \
date the data came from. If a question is outside the data available, say so clearly \
rather than guessing.

Key business context to keep in mind:
- Trustpilot rating is 2.0 and the profile is not yet claimed (CRITICAL risk)
- Google Shopping campaigns: ZERO active despite 250k+ products (major revenue gap)
- Heavy coupon dependency masks real acquisition efficiency
- No email lifecycle automations are live (cart recovery, churn prevention all missing)
- Team size: 8 people across performance, CRM, content, and ops

Today's agent data:
{context}
"""

# Strip the @mention e.g. "<at>Ananas AI</at> what is the ROAS?" -> "what is the ROAS?"
_MENTION_RE = re.compile(r"<at>[^<]*</at>\s*", re.IGNORECASE)


def _clean(text: str) -> str:
    return _MENTION_RE.sub("", text).strip()


class AnanasBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext) -> None:
        user_text = _clean(turn_context.activity.text or "")

        if not user_text:
            await turn_context.send_activity("Hi! Ask me anything about today's marketing data.")
            return

        logger.info(
            "bot: question from %s: %s", turn_context.activity.from_property.name, user_text[:120]
        )

        # Typing indicator
        await turn_context.send_activity(Activity(type=ActivityTypes.typing))

        try:
            context = load_context(lookback_days=2)
            system = SYSTEM_PROMPT.format(context=context)
            result = call_model(
                model="claude-sonnet-4-6",
                system=system,
                user=user_text,
                max_tokens=1024,
            )
            reply = result["text"]
            logger.info(
                "bot: replied (%d tokens, $%.4f, fallback=%s)",
                result["tokens_in"] + result["tokens_out"],
                result["estimated_cost"],
                result["fallback"],
            )
        except Exception as exc:
            logger.error("bot: error generating reply: %s", exc)
            reply = "Sorry, I couldn't process that right now. Please try again in a moment."

        await turn_context.send_activity(reply)

    async def on_members_added_activity(self, members_added, turn_context: TurnContext) -> None:
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    "Hello! I'm the Ananas AI assistant. Ask me about today's performance, "
                    "CRM health, reputation status, or any marketing KPIs."
                )
