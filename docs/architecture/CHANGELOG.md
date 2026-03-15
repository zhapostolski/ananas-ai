# Architecture Changelog

## 2026-03-15 — v0.3.2 (Output guardrails)

### New files
- `scripts/guardrail_check.py` — output sanity checker; runs before every DB write or Teams/email post
- `docs/decisions/adr-009-guardrails.md` — guardrail procedure: four layers, failure handling, how to extend for new agents
- `.claude/rules/runtime/guardrails.md` — runtime rule enforcing guardrail discipline

### What changed
- All agent outputs must now pass guardrail_check before reaching downstream systems
- Four check layers: structural fields, run_type labelling, per-agent KPI bounds, cross-agent coherence
- Procedure documented for adding new agent bounds and handling sample-mode outputs

---

## 2026-03-14 — v0.3.1 (QA gate + release process)

### Release process
- `deploy.yml` restructured as "Release" workflow: 4 QA jobs (`quality`, `test`, `validate`, `secrets-scan`) run in parallel; `deploy` job blocked behind `needs: [quality, test, validate, secrets-scan]`
- `Makefile` `release` target added: runs full local QA gate before tagging and pushing — broken code cannot reach EC2 or GitHub

### Code quality
- Applied `ruff format` to all files; CI now enforces format check on every push and tag

---

## 2026-03-14 — v0.3.0 (Claude + OpenAI integration, agent wiring)

### New files
- `src/ananas_ai/model_client.py` — unified Claude + OpenAI client with automatic fallback; returns `{text, model_used, fallback}`

### Agent changes
- `agents/base.py` — added `run(date_from, date_to)` stub so all agents share the interface
- `agents/performance.py` — `run()` wired with Claude call; Shopping IS=0 critical context in system prompt
- `agents/marketing_ops.py` — `run()` wired with Claude call; tracking health + Search Console analysis
- `agents/crm_lifecycle.py` — rewritten: Sales Snap API stub, `KNOWN_GAPS` + `JOURNEYS` constants (all 6 lifecycle journeys `not_live`), Claude call
- `agents/reputation.py` — rewritten: Trustpilot API stub, `TRUSTPILOT_KNOWN_STATE` (2.0 rating, unclaimed), Claude call
- `agents/cross_channel_brief.py` — rewritten: calls Claude with `complexity="high"` (Opus escalation), synthesises all specialist `analysis` fields

### CLI changes
- `cli.py` `run_brief()` now calls `agent.run()` for all 4 specialists before building the brief; each specialist result is persisted and posted to its own Teams channel

### Teams output
- `teams.py` rewritten: produces Teams Adaptive Card JSON; posts to `TEAMS_WEBHOOK_URL` when configured, always writes local debug file; parses `- Key: value` lines into FactSet

### Dependencies
- `pyproject.toml` — added `openai>=1.50.0`

---

## 2026-03-14 — v0.2.4 (EC2 bootstrap + CI fixes)

### Infrastructure
- EC2 t3.small provisioned via Terraform in eu-central-1, Elastic IP 52.29.60.185
- PostgreSQL installed, schema bootstrapped
- SSM agent installed; GitHub Actions deploy via SSM send-command (SSH port closed)
- 5 secrets loaded in AWS Secrets Manager: Anthropic key, GA4 paths, DB config

### CI fixes
- mypy: fixed 9 type errors across integrations and persistence
- TruffleHog: switched to before/after SHA comparison
- Config validation: fixed `docs/budget/budget.md` path

---

## 2026-03-14 — v3 (presentation readiness + automation)

### New documents
- `docs/budget/budget.md` → complete Phase 1/2 cost breakdown with AWS vs Hetzner comparison and ROI framing
- `docs/leadership/denis-summary.md` → full rewrite for Country Manager lens: daily brief format, success criteria, regional expansion context
- `docs/presentation/monday-presentation.md` → exec-ready presentation narrative for Denis + marketing team approval meeting
- `docs/operations/success-metrics.md` → Month 1/2/3 success criteria with measurable KPIs and Phase 2 gate conditions
- `context/ananas/ananas-overview.md` → living company knowledge base, auto-updated via file watcher
- `context/ananas/SOURCES.md` → source processing log
- `.env.example` → environment variable template

### New infrastructure
- `scripts/watch_context.py` → automated file watcher: detects files dropped in `context/ananas/raw/`, calls Claude API, updates overview
- `~/.config/systemd/user/ananas-context-watcher.service` → systemd user service, runs on WSL2 boot, auto-restarts on failure
- `scripts/setup_watcher_service.sh` → one-time service setup script

### Dependency updates
- `pyproject.toml` → added: anthropic, watchdog, pypdf, python-docx, openpyxl, pillow

### Config corrections
- Denis role corrected to Country Manager (not executive stakeholder) across all docs

---

## 2026-03-14 — v2 (full GPT conversation audit + gap implementation)

### Config changes
- `config/metrics.json` → v2: added 8 new metric groups (marketplace, promo_simulator, app_metrics, ai_system); added contribution margin waterfall, POAS per campaign, Shopping impression share, coupon dependency ratio, CLV/CAC, cost per insight, automations active/total, app DAU/MAU, push opt-in rate
- `config/model-routing.json` → v2: formally added OpenAI GPT-4o-mini as 3rd routing tier; added per-agent model assignments; added token cap values; added batch processing policy
- `config/agents.json` → v2: added 11 Phase 2 agents (category-growth, supplier-intelligence, demand-forecasting, promo-simulator, product-feed, organic-merchandising, influencer-partnership, traditional-media-correlation, employer-branding, meeting-intelligence, knowledge-retrieval); all Phase 1 agents updated with router_model field
- `config/integrations-matrix.json` → v2: added Trustpilot API endpoint; added LinkedIn Ads and X Ads explicitly; moved Search Console to Phase 1; added app analytics (Firebase/Adjust), social publishing (Hootsuite), traditional media (Campaign Calendar Sheet), supplier API, inventory API, product catalog API, Berry HR noted
- `config/schedules.json` → v2: added Phase 2 weekly schedule; added Phase 2 on-demand agents; added system jobs

### Agent definition changes (`.claude/agents/`)
- All 5 Phase 1 agents: updated model field to `claude-sonnet-4-5`; added business context, specific metric targets, escalation triggers, structured output formats
- `performance-agent.md`: added Shopping impression share priority, POAS per campaign, coupon distortion context
- `reputation-agent.md`: added Trustpilot 2.0 critical context, API endpoint, response time target, alert triggers
- `marketing-ops-agent.md`: added coupon dependency ratio priority, contribution margin waterfall, return rate by category
- `crm-lifecycle-agent.md`: added lifecycle flow gap context, cart recovery targets, churn window tracking, email revenue per send target
- `cross-channel-brief-agent.md`: added Denis email spec, contribution margin lead framing, waterfall reference, coupon context, mobile-readable brief format
- Created 11 new Phase 2 agent definitions

### CLAUDE.md
- Updated to v2: added 3-tier model table, Phase 1 and Phase 2 agent tables, critical business context section, updated config file references

### Architecture doc
- `architecture-v1.md` → updated to v2 content: full architecture tree, infrastructure flow, metric coverage table, Phase 2 priority ranking, v2 change log

---

## 2026-03-13 — GA4 live integration tested
- GA4 Data API v1beta connected and validated
- Live proof: 464,844 sessions, 215,232 users, 2,925 conversions, €13.36M revenue
- Google Cloud project: ananas-ai-ga4-test
- Auth: ADC via gcloud application-default login

## 2026-03-07 — v1 initial build
- Populated architecture pack with Phase 1 architecture, budget, roadmap, rules, agents, and config files
- Added CLAUDE.md and project-scoped Claude Code structure
- Added 5 specialist subagent definitions
- Added validation script and integration matrix
- Added SQL schema (6 tables)
