# Project Summary — v2
**Last updated:** 2026-03-14

## What this project is
Ananas AI Platform is a marketing-first internal AI intelligence system for Ananas.mk — North Macedonia's largest e-commerce marketplace (~250k products, Delta Holding backed). It combines specialist AI agents, MCP integrations, Teams/email distribution, and a Next.js portal to deliver daily decision-making intelligence to the marketing team and leadership.

## Business context — why this exists now
| Issue | Impact |
|---|---|
| No Google Shopping campaigns (250k products) | Revenue gap every day |
| Trustpilot at 2.0 — profile unclaimed | Suppresses paid media efficiency |
| Sales driven by marketing-budget coupons | Masks real acquisition efficiency |
| No email lifecycle automations live | Revenue sitting untouched |
| Weak campaign post-analysis discipline | Slow learning, wasted spend |

## Phase 1 — committed scope (Months 1–3)
- Domain: `ai.ananas.mk`
- Runtime: AWS EC2 t3.xlarge (Hetzner CPX41 as fast-lane backup)
- Database: PostgreSQL on EC2 (6 tables)
- Five specialist agents: Performance, CRM & Lifecycle, Reputation, Marketing Ops, Cross-Channel Brief
- Daily cron 06:00–07:30 MKD, Teams channel posting, executive email to Denis
- GA4 live and tested (2026-03-13: 464k sessions, 215k users, €13.4M revenue)
- KPI dashboard on portal (Claude Code built)
- No Teams bot in Phase 1 — Phase 2
- No portal in Phase 1 — Phase 2

## Phase 2 — planned scope (Months 4–9)
- Full portal at ai.ananas.mk (Next.js, Entra ID SSO, precomputed reads)
- 11 additional specialist agents (category-growth, supplier-intelligence, demand-forecasting, promo-simulator, product-feed, organic-merchandising, influencer-partnership, traditional-media-correlation, employer-branding, meeting-intelligence, knowledge-retrieval)
- Teams bot (retrieval, promo simulation, knowledge search)
- Broader live integrations: all paid channels, supplier API, product feed, app analytics
- Meeting intelligence (Whisper → Jira)
- Knowledge retrieval (Confluence + campaign archive)

## Phase 3 — vision (Months 10–18)
- Company-wide expansion: Commercial, Finance, Operations, HR, Support
- Self-learning content memory (marketing-brain pattern)
- Multilingual outputs (Macedonian)
- MMM / incrementality measurement
- Video and creative automation layer

## 3-tier model routing
| Tier | Model | Purpose |
|---|---|---|
| Router | OpenAI GPT-4o-mini | Classification, normalization |
| Default | Claude Sonnet | All Phase 1 agents |
| Escalation | Claude Opus | Complex synthesis only |

## Key architectural decisions
- No permanent orchestrator in the hot path (ADR-005)
- No heavy custom gateway — Next.js middleware only (ADR-001)
- Portal reads precomputed outputs, not live AI responses
- MCP-first integration strategy
- All integrations read-only in Phase 1
- Versioned config for prompts, metrics, schemas, routing, schedules
- Search Console in Phase 1 (was Phase 2 — critical for 250k catalog)
- GPT-4o-mini as formal router tier (ADR-006)

## Current implementation status
- Config files v2: complete (agents, metrics, routing, integrations, schedules)
- .claude/agents/: 16 definitions (5 Phase 1 + 11 Phase 2)
- CLAUDE.md: v2 updated
- Architecture doc: v2 complete
- GA4 integration: LIVE
- AWS infrastructure: pending provisioning
- SQL schema: defined (6 tables)

## Repository
`github.com/zhapostolski/ananas-ai` (work account)
Dev environment: WSL2 Ubuntu — `/home/zapostolski/projects/ananas-ai`
