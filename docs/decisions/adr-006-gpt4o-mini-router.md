# ADR-006 — OpenAI GPT-4o-mini as Lightweight Routing Tier

## Status
Accepted — 2026-03-14

## Context
The original ADR-003 model routing policy named a "low-cost routing model" but did not specify which model. In v2, we formally identify and configure OpenAI GPT-4o-mini as the router.

Routing decisions happen on every agent run: intent classification, complexity pre-check, normalization of raw MCP data before it enters the Sonnet prompt. These are cheap, high-frequency calls — running them on Claude Sonnet adds unnecessary cost.

## Decision
Use **OpenAI GPT-4o-mini** (`gpt-4o-mini`) as the router model for:
- Intent classification (what type of analysis is this agent run?)
- Complexity pre-check (should this run escalate to Opus?)
- Data normalization (clean and standardize raw MCP outputs before Sonnet ingestion)
- Quick data validation (are required fields present before loading into context?)

Claude Sonnet handles all actual agent execution. Claude Opus handles escalations only.

## Cost rationale
| Decision | Tokens/day (moderate) | Cost/day |
|---|---|---|
| Router on GPT-4o-mini | ~50k | ~$0.17 |
| Same calls on Claude Sonnet | ~50k | ~$0.75 |
| **Monthly saving** | | **~$17/month** |

Modest savings in Phase 1, but the pattern scales well into Phase 2 when agent count increases.

## Consequences
- Requires OpenAI API key in Secrets Manager alongside Anthropic key
- model_used field in agent_logs must support both 'claude-sonnet' and 'gpt-4o-mini' values
- If OpenAI routing call fails, fallback is to proceed directly to Claude Sonnet (no escalation)
- Router prompt must be kept simple — GPT-4o-mini is not used for complex reasoning

## Review trigger
If GPT-4o-mini routing quality causes measurable errors (wrong complexity classification, poor normalization), review and consider moving to o3-mini or directly to Sonnet for the routing step.
