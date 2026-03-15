# Guardrail Rules

- Every agent output must pass `scripts/guardrail_check.py` before DB write or Teams/email post.
- A missing or invalid `run_type` is always a hard failure — never pass an output without it.
- Sample-mode outputs (`run_type: sample`) must include `[SAMPLE DATA]` in any Teams message body.
- Do not loosen KPI bounds to make a failing check pass — document the business reason in ADR-009 first.
- When adding a new agent, add its `AGENT_RULES` entry to `guardrail_check.py` in the same batch as the agent config.
- Guardrail failures must be logged and must not be silently swallowed.
- Switching an agent from `run_type: sample` to `live` requires a manual confirmation step — never automate this transition.
- See `docs/decisions/adr-009-guardrails.md` for the full procedure.
