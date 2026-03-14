# ADR-005 Specialist-First Design — No Permanent Orchestrator

## Status
Accepted — Phase 1 architecture rule

## Context
Early design considered a central orchestrator agent that would receive all queries, route them to specialist agents, and synthesise responses. This pattern (common in multi-agent frameworks) creates a permanent hot-path dependency: every run costs an extra model call, adds latency, and creates a single point of failure.

For Phase 1 — 5 agents, daily cron, one operator — an orchestrator adds complexity without benefit.

## Decision
Specialist agents run independently on schedule. The `cross-channel-brief-agent` is a scheduled synthesis layer (not a runtime orchestrator): it runs after the 4 specialist agents complete and synthesises their stored outputs. No agent routes through another agent in the hot path.

Architecture rules enforced by `CLAUDE.md`:
- Do not introduce a permanent runtime orchestrator
- Specialist agents own their data domain end-to-end
- Cross-domain synthesis happens at the brief layer only

## Consequences
- **+** Each agent can be developed, tested, and deployed independently
- **+** No single-agent failure cascades to other agents
- **+** Lower cost: 5 independent calls vs. 5 calls + orchestrator overhead
- **+** Clear ownership: one agent = one data domain = one Teams channel
- **−** Ad-hoc cross-domain queries (e.g. "why did CRM revenue drop when reputation was poor?") require explicit tooling — no automatic cross-agent routing in Phase 1
- **−** The brief layer is scheduled, not reactive — no real-time synthesis on demand
- **Review trigger:** Phase 2 Teams bot with multi-domain Q&A → add lightweight router using GPT-4o-mini (already in config as tier-1 router, not yet wired)
