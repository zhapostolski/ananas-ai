# Ananas AI Platform — Project Instructions (v2)

## What this project is
This repository documents and implements the Ananas AI Platform — a marketing-first internal intelligence system built on the existing Ananas stack and AWS infrastructure.

**Phase 1 (active):** 5 specialist agents, daily cron runtime, Teams + email outputs, KPI dashboard, AWS EC2 infrastructure.
**Phase 2 (planned):** Full portal at ai.ananas.mk, 11 additional agents, broader live integrations, Teams bot, meeting intelligence, knowledge retrieval.

The platform consists of:
- A Next.js portal on `ai.ananas.mk` (Phase 2)
- An AWS EC2 runtime running 5 specialist agents on cron (Phase 1)
- MCP integrations to marketing, business, and collaboration systems
- A PostgreSQL datastore for outputs, logs, metrics, and health state
- Teams channel posting (Phase 1) and Teams bot (Phase 2)
- 3-tier model routing: GPT-4o-mini router → Claude Sonnet default → Claude Opus escalation

## Architecture priorities
1. Preserve the existing Ananas stack and conventions
2. Keep Phase 1 lean, readable, and easy to operate by one person
3. Specialist-first — no permanent orchestrator in the hot path
4. Validate every output before it touches the database
5. Treat prompts, metrics, routing rules, and schedules as versioned config — not hardcoded logic
6. Portal is the primary deep-analysis interface
7. Teams is the primary communication interface — lighter than the portal
8. All business system access is read-only in Phase 1

## Model routing — 3-tier design
| Tier | Model | Purpose |
|---|---|---|
| Router | OpenAI GPT-4o-mini | Intent classification, normalization, pre-checks |
| Default | Claude Sonnet | All 5 Phase 1 agents, standard execution |
| Escalation | Claude Opus | Complex synthesis, executive reasoning only |

Use GPT-4o-mini for any lightweight decision that does not require full reasoning quality.
Never use Opus as the default — only when Sonnet quality is provably insufficient.

## Phase 1 agents (active — daily cron)
| Time | Agent | Outputs |
|---|---|---|
| 06:00 | performance-agent | #marketing-performance |
| 06:30 | crm-lifecycle-agent | #marketing-crm |
| 07:00 | reputation-agent | #marketing-reputation |
| 07:15 | marketing-ops-agent | #marketing-ops |
| 07:30 | cross-channel-brief-agent | #marketing-summary + #executive-summary + email Denis |

## Phase 2 agents (planned)
organic-merchandising, category-growth, supplier-intelligence, demand-forecasting,
promo-simulator, product-feed, influencer-partnership, traditional-media-correlation,
employer-branding, meeting-intelligence, knowledge-retrieval

## Critical business context (always keep in mind)
- Trustpilot: 2.0 rating, profile not yet claimed — CRITICAL reputation risk
- Google Shopping: ZERO campaigns despite 250k+ products — major revenue gap
- Coupon dependency: sales heavily driven by marketing-budget coupons — masks real acquisition efficiency
- No email lifecycle automations currently — cart recovery, churn flows not live
- Team size: 8 people (2 designers, 3 performance, 1 content/social, 1 CRM, 1 TBD)
- Internal tools: Jira, Asana, Confluence, Teams, SharePoint, Outlook, Berry (HR)
- GA4: LIVE and tested (2026-03-13: 464k sessions, 215k users, €13.4M revenue)

## Working rules
- Read `docs/architecture/architecture-v1.md` before making architecture changes
- Read `docs/project-summary.md` before major implementation or redesign
- Keep new decisions in `docs/decisions/` as ADRs
- When changing agents, also update: config/agents.json, config/schedules.json, config/model-routing.json, .claude/agents/, CHANGELOG
- When changing metrics, update config/metrics.json
- When changing integrations, update config/integrations-matrix.json
- Do not introduce a heavy gateway without an ADR
- Do not introduce write actions to business systems in Phase 1 without an ADR

## Cost controls
- Per-run token cap: 50k Sonnet / 30k Opus
- Per-day token cap per agent: 200k
- Log model_used and estimated_cost for every run
- Prompt caching enabled for stable system prompts
- Batch processing allowed for historical backfills only

## Documentation discipline
Any meaningful platform change must update:
1. Relevant config files
2. architecture-v1.md or a new ADR in docs/decisions/
3. CHANGELOG.md
4. Diagrams if structure changed

## Where to start
1. `docs/architecture/architecture-v1.md` — full architecture reference
2. `docs/project-summary.md` — business context
3. `config/agents.json` — all agents, phases, sources, outputs
4. `config/metrics.json` — all KPI definitions and formulas
5. `config/model-routing.json` — 3-tier model assignments
6. `config/integrations-matrix.json` — all MCP connectors by domain
7. `.claude/agents/` — Claude Code subagent definitions
