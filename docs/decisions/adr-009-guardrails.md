# ADR-009: Output Guardrails — Procedure and Implementation

**Status:** Accepted
**Date:** 2026-03-15
**Author:** Platform

---

## Context

Agent outputs flow from Claude Sonnet into PostgreSQL and then into Teams channels and executive email. There is currently no layer that validates whether those outputs are sensible before they reach stakeholders. A model can:

- Return structurally valid JSON with nonsensical KPI values (€0 revenue, 9000% CTR)
- Return sample/hardcoded data without labelling it as such
- Omit critical fields silently
- Reference the wrong agent or date range

The risk is low in Phase 1 because outputs are manually reviewed before the system goes live, but grows as more agents are added and the system runs unattended.

---

## Decision

Every agent output must pass a **guardrail check** before being written to the database or posted to any output channel (Teams, email, portal). The check runs in the agent execution pipeline, after the model returns a response and before any downstream write.

The checker is implemented in `scripts/guardrail_check.py` and can be called as a script or imported as a module.

---

## Guardrail Layers

There are four layers, applied in order:

### Layer 1 — Structural
Verify that all required envelope fields are present and non-null:
`agent_name`, `module_name`, `output_type`, `date_from`, `date_to`, `data_json`, `version`, `model_used`, `created_at`, `run_type`

A missing `run_type` is always a hard failure. An output with no `agent_name` cannot be routed.

### Layer 2 — run_type labelling
`run_type` must be either `"live"` or `"sample"`. Sample outputs routed to Teams must include a `[SAMPLE]` label in the message body. This prevents hardcoded test data from appearing as real intelligence to stakeholders.

### Layer 3 — KPI range checks
Per-agent numeric bounds are declared in `AGENT_RULES` inside the checker. Any value outside its declared range is a hard failure. The bounds are conservative (not tight) — they catch obvious model errors, not normal business variance.

| Agent | Example bounds |
|---|---|
| performance-agent | ROAS 0-200, POAS 0-50, impression_share 0-100% |
| crm-lifecycle-agent | cart_abandonment_rate 0-100%, email_open_rate 0-100% |
| reputation-agent | Trustpilot rating 1.0-5.0 (required), response_rate 0-100% |
| marketing-ops-agent | coupon_dependency_ratio 0-1.0, uptime 0-100% |

### Layer 4 — Cross-agent coherence
The `cross-channel-brief-agent` output must reference all four source agents. If any are missing, the brief is incomplete and must not be posted.

---

## Failure handling

| Result | Action |
|---|---|
| PASSED | Write to DB, post to channel |
| PASSED with warnings | Write to DB, post to channel, log warnings |
| FAILED | Do not write to DB, do not post. Log failure with full error list. Trigger dead-man alert if failures exceed 2 consecutive runs. |

Failures are not silently swallowed. They must appear in the platform operations log and increment `guardrail_failures_today` in `metrics.json / ai_system`.

---

## Procedure: Adding guardrails for a new agent

When a new agent is added to the platform:

1. Add the agent name and its KPI bounds to `AGENT_RULES` in `guardrail_check.py`
2. Mark which fields are `required=True` (fields that must always be present for the output to be meaningful)
3. Write at least one passing and one failing fixture in `tests/guardrails/`
4. Run `python scripts/guardrail_check.py` against the fixture as part of the CI/pre-commit check
5. Update this ADR's bounds table above

This must happen in the same batch as the agent config change (per `CLAUDE.md` working rules).

---

## Procedure: Adjusting bounds

Bounds should be adjusted when:
- A legitimate business metric consistently hits a boundary (e.g. ROAS exceeds 200 during a major sale)
- A new data source changes the expected range of a metric

Bounds must **not** be loosened to make a failing check pass unless the underlying business case is documented here.

---

## Procedure: Handling sample-mode outputs

All Phase 2 agents start in `run_type: sample`. The guardrail checker will:
- Allow the output to pass
- Emit a warning
- Require the Teams message to include `[SAMPLE DATA]` in the header

When a live API is connected and validated, `run_type` is switched to `"live"`. This switch requires a manual confirmation step — it must not happen automatically.

---

## What guardrails do NOT cover

- Semantic quality of narrative text (e.g. whether the insight is actually useful)
- Hallucinated reasoning that is numerically within range
- Data source freshness (handled separately by the dead-man heartbeat)
- Model latency or cost (handled by token caps and `metrics.json / ai_system`)

These are out of scope for the guardrail layer. They belong in agent-level prompt design and operational monitoring.

---

## Consequences

- Every agent run has a clear pass/fail gate before touching downstream systems
- Sample-mode outputs cannot silently reach stakeholders as if they were live
- Adding a new agent requires explicitly declaring its KPI bounds — this forces the builder to think about what "valid output" means for that agent
- Guardrail failures are observable in the ops log and will page on consecutive failures
