# Runtime Agent and Cost Rules

- Default execution model is Claude Sonnet.
- Opus is only used by explicit escalation rules.
- Lightweight routing and classification should use the low-cost routing model.
- Every agent run must record model used, token usage, duration, and status.
- Enforce per-run and per-day token caps.
- Reject malformed outputs before DB write.
- Cross-Channel Brief Agent runs after all source agents.
