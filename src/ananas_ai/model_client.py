"""Unified model client - Claude (primary) with OpenAI fallback.

Usage:
    from ananas_ai.model_client import call_model
    result = call_model(model="claude-sonnet-4-6", system=SYSTEM, user=prompt)

Returns:
    {
        "text": str,
        "model_used": str,
        "fallback": bool,
        "tokens_in": int,
        "tokens_out": int,
        "estimated_cost": float,   # USD
    }

Falls back to GPT-4.1 if Claude fails (rate limit, quota, outage).
Per-run token caps loaded from config/model-routing.json controls block.
"""

from __future__ import annotations

import os
from typing import Any

from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

# ── Token caps (per single call, input + output combined) ─────────────────────
# Loaded from config/model-routing.json controls block.
# Defaults are conservative - overridden by config when available.
_PER_RUN_CAP_SONNET = 50_000
_PER_RUN_CAP_OPUS = 30_000

# ── Pricing table (USD per million tokens) ────────────────────────────────────
# Matches config/model-routing.json approx_cost_per_mtok_* fields.
_PRICES: dict[str, tuple[float, float]] = {
    "claude-opus": (5.00, 25.00),
    "claude-sonnet": (3.00, 15.00),
    "gpt-4.1-mini": (0.40, 1.60),  # gpt-4.1-mini pricing
    "gpt-4.1-nano": (0.10, 0.40),  # gpt-4.1-nano pricing
    "gpt-4.1": (2.00, 8.00),  # gpt-4.1 pricing
    "gpt-4o-mini": (0.15, 0.60),  # kept for legacy fallback
    "gpt-4o": (5.00, 15.00),  # kept for legacy fallback
}

# ── OpenAI fallback model map ─────────────────────────────────────────────────
# gpt-4.1 is the latest OpenAI model (released April 2025).
# Sonnet → gpt-4.1 (comparable capability tier)
# Opus   → gpt-4.1 (best available fallback)
CLAUDE_TO_OPENAI: dict[str, str] = {
    "claude-sonnet-4-5": "gpt-4.1",
    "claude-sonnet-4-6": "gpt-4.1",
    "claude-opus-4-5": "gpt-4.1",
    "claude-opus-4-6": "gpt-4.1",
}


def _load_caps() -> tuple[int, int]:
    """Load per-run token caps from config. Falls back to module defaults."""
    try:
        from ananas_ai.config import load_settings

        controls = load_settings().model_routing.get("controls", {})
        sonnet = int(controls.get("per_run_token_cap_sonnet", _PER_RUN_CAP_SONNET))
        opus = int(controls.get("per_run_token_cap_opus", _PER_RUN_CAP_OPUS))
        return sonnet, opus
    except Exception:
        return _PER_RUN_CAP_SONNET, _PER_RUN_CAP_OPUS


def _per_run_cap(model: str) -> int:
    sonnet_cap, opus_cap = _load_caps()
    return opus_cap if "opus" in model.lower() else sonnet_cap


def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """Return estimated USD cost for a model call."""
    model_lower = model.lower()
    price_in, price_out = 3.00, 15.00  # default: Sonnet prices
    for key, (pin, pout) in _PRICES.items():
        if key in model_lower:
            price_in, price_out = pin, pout
            break
    return round((tokens_in * price_in + tokens_out * price_out) / 1_000_000, 6)


def _sanitize(text: str) -> str:
    """Strip characters that cause downstream issues (em/en dashes from LLM output)."""
    return text.replace("\u2014", "-").replace("\u2013", "-")


def _call_claude(model: str, system: str, user: str, max_tokens: int) -> tuple[str, int, int]:
    """Call Claude. Returns (text, tokens_in, tokens_out)."""
    import anthropic  # type: ignore[import]

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text_block = next((b for b in msg.content if b.type == "text"), None)
    text = _sanitize(str(text_block.text) if text_block else "")  # type: ignore[union-attr]
    tokens_in = int(msg.usage.input_tokens)
    tokens_out = int(msg.usage.output_tokens)
    return text, tokens_in, tokens_out


def _call_openai(model: str, system: str, user: str, max_tokens: int) -> tuple[str, int, int]:
    """Call OpenAI. Returns (text, tokens_in, tokens_out)."""
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
    text = _sanitize(str(resp.choices[0].message.content))
    tokens_in = int(resp.usage.prompt_tokens) if resp.usage else 0
    tokens_out = int(resp.usage.completion_tokens) if resp.usage else 0
    return text, tokens_in, tokens_out


def call_model(
    model: str,
    system: str,
    user: str,
    max_tokens: int = 4096,
    allow_fallback: bool = True,
) -> dict[str, Any]:
    """Call Claude with automatic OpenAI fallback.

    Enforces per-run token cap (logs warning if exceeded - does not abort,
    since we cannot know input size before the call).

    Returns:
        {
            "text": str,
            "model_used": str,
            "fallback": bool,
            "tokens_in": int,
            "tokens_out": int,
            "estimated_cost": float,
        }
    """
    cap = _per_run_cap(model)

    # ── Try Claude first ──────────────────────────────────────────────────────
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            text, tokens_in, tokens_out = _call_claude(model, system, user, max_tokens)
            total = tokens_in + tokens_out
            cost = estimate_cost(model, tokens_in, tokens_out)
            logger.info(
                "model_client: %s - %d in / %d out / $%.4f (cap %d)",
                model,
                tokens_in,
                tokens_out,
                cost,
                cap,
            )
            if total > cap:
                logger.warning(
                    "model_client: per-run token cap exceeded - %d tokens used, cap is %d",
                    total,
                    cap,
                )
            return {
                "text": text,
                "model_used": model,
                "fallback": False,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "estimated_cost": cost,
            }
        except Exception as e:
            logger.warning("model_client: Claude failed (%s), trying OpenAI fallback", e)

    # ── OpenAI fallback ───────────────────────────────────────────────────────
    if allow_fallback and os.environ.get("OPENAI_API_KEY"):
        openai_model = CLAUDE_TO_OPENAI.get(model, "gpt-4o")
        try:
            text, tokens_in, tokens_out = _call_openai(openai_model, system, user, max_tokens)
            cost = estimate_cost(openai_model, tokens_in, tokens_out)
            logger.info(
                "model_client: %s (fallback) - %d in / %d out / $%.4f",
                openai_model,
                tokens_in,
                tokens_out,
                cost,
            )
            return {
                "text": text,
                "model_used": openai_model,
                "fallback": True,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "estimated_cost": cost,
            }
        except Exception as e:
            logger.error("model_client: OpenAI fallback also failed: %s", e)

    raise RuntimeError("No model available - check ANTHROPIC_API_KEY and OPENAI_API_KEY")
