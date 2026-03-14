"""Unified model client — Claude (primary) with OpenAI fallback.

Usage:
    from ananas_ai.model_client import call_model
    result = call_model(model="claude-sonnet-4-5", system=SYSTEM, user=prompt)

Falls back to GPT-4o if Claude fails (rate limit, quota, outage).
"""

from __future__ import annotations

import os
from typing import Any

from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

# Token caps per run (from config/model-routing.json)
MAX_TOKENS_SONNET = 4096
MAX_TOKENS_OPUS = 4096

# OpenAI equivalents for fallback
CLAUDE_TO_OPENAI: dict[str, str] = {
    "claude-sonnet-4-5": "gpt-4o",
    "claude-sonnet-4-6": "gpt-4o",
    "claude-opus-4-5": "gpt-4o",
    "claude-opus-4-6": "gpt-4o",
}


def _call_claude(model: str, system: str, user: str, max_tokens: int) -> str:
    import anthropic  # type: ignore[import]

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text_block = next((b for b in msg.content if b.type == "text"), None)
    return str(text_block.text) if text_block else ""  # type: ignore[union-attr]


def _call_openai(model: str, system: str, user: str, max_tokens: int) -> str:
    import openai  # type: ignore[import]

    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return str(resp.choices[0].message.content)


def call_model(
    model: str,
    system: str,
    user: str,
    max_tokens: int = MAX_TOKENS_SONNET,
    allow_fallback: bool = True,
) -> dict[str, Any]:
    """Call Claude with automatic OpenAI fallback.

    Returns:
        {"text": str, "model_used": str, "fallback": bool}
    """
    # Try Claude first
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            text = _call_claude(model, system, user, max_tokens)
            logger.info("model_client: %s responded (%d chars)", model, len(text))
            return {"text": text, "model_used": model, "fallback": False}
        except Exception as e:
            logger.warning("model_client: Claude failed (%s), trying OpenAI fallback", e)

    # OpenAI fallback
    if allow_fallback and os.environ.get("OPENAI_API_KEY"):
        openai_model = CLAUDE_TO_OPENAI.get(model, "gpt-4o")
        try:
            text = _call_openai(openai_model, system, user, max_tokens)
            logger.info("model_client: %s (fallback) responded (%d chars)", openai_model, len(text))
            return {"text": text, "model_used": openai_model, "fallback": True}
        except Exception as e:
            logger.error("model_client: OpenAI fallback also failed: %s", e)

    raise RuntimeError("No model available — check ANTHROPIC_API_KEY and OPENAI_API_KEY")
