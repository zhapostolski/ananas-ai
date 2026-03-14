# ADR-003 3-Tier Model Routing

## Status
Accepted — implemented March 2026

## Context
Running every agent on Claude Opus would cost ~5–8× more per day than using Sonnet. Most daily briefing tasks (performance summary, CRM status, reputation check) do not require Opus-level reasoning. At the same time, the cross-channel brief synthesising all four specialist outputs needs stronger synthesis capability.

A single-model approach was rejected: using Sonnet everywhere risks quality loss on complex synthesis; using Opus everywhere is unnecessarily expensive for classification and routine summarisation.

## Decision
3-tier routing implemented in `src/ananas_ai/model_router.py` and `config/model-routing.json`:

| Tier | Model | Use case |
|---|---|---|
| Router | OpenAI GPT-4o-mini | Lightweight classification, pre-checks (not yet fully wired) |
| Default | Claude Sonnet | All 5 Phase 1 agents, standard daily execution |
| Escalation | Claude Opus | Cross-channel brief (`complexity=high`), executive synthesis |

Fallback: if Claude is unavailable (rate limit, outage), agents fall back to OpenAI GPT-4.1 automatically via `model_client.py`.

Per-run token caps enforced: 50k tokens for Sonnet, 30k for Opus. Per-day cap: 200k tokens per agent.

## Consequences
- **+** Cost-optimised: ~$0.02–0.05/day for all 5 agents at current volume
- **+** Fallback path means platform keeps running during Claude outages
- **+** Token caps prevent runaway costs from prompt injection or unusually large inputs
- **−** GPT-4o-mini router tier not yet fully wired into agent decision path (Phase 2)
- **Review trigger:** If Sonnet quality is insufficient for any agent → escalate that agent to Opus via `agent_model_assignments` in config
