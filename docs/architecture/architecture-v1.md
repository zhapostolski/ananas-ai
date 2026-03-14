# Ananas AI Platform — Architecture v2
**Last updated:** 2026-03-14
**Status:** Final draft for Denis and marketing team review

---

## 1. Executive overview

Ananas AI Platform is a marketing-first internal intelligence system built on the existing Ananas stack and AWS infrastructure. It is the daily intelligence layer for marketing: a place where the team and leadership can see what changed, where risk exists, where opportunity exists, and what requires attention today.

The platform collects marketing data from the systems the team already uses, processes it through specialist AI agents, stores results in a structured database, and distributes outputs through two interfaces:
- **Portal** at `ai.ananas.mk` — structured modules for deep analysis
- **Microsoft Teams** — morning summaries and lightweight bot engagement

---

## 2. Business context

The platform does not start from an abstract AI concept. It starts from the current operating reality:

| Observed issue | Business impact |
|---|---|
| No Google Shopping campaigns despite 250k+ products | Revenue opportunity lost daily |
| Trustpilot at 2.0 — profile not yet claimed | Suppresses paid media efficiency |
| Sales heavily driven by free coupons from marketing budget | Margin erosion, distorted performance |
| Not all campaigns analyzed post-launch | Slow learning, wasted spend |
| Weak ownership across channels | Accountability gaps |
| No email lifecycle automation | Revenue sitting untouched |

The platform addresses these through structured daily intelligence, not more manual work.

---

## 3. Core design principles

1. Use the existing Ananas stack (Next.js, TypeScript, AWS)
2. Specialist-first — no permanent orchestrator in the hot path
3. Portal-first for structured analysis; Teams-first for communication
4. Read-only access to business systems in Phase 1
5. Validate every output before it becomes part of the system of record
6. Treat prompts, metrics, routing rules, and schedules as versioned configuration
7. Three-tier model routing: cheap router → Sonnet default → Opus escalation
8. One EC2 host in Phase 1 — lean, understandable, operable

---

## 4. Architecture tree

```
Ananas AI Platform v2
│
├── User Access Layer
│   ├── ai.ananas.mk (Route 53 → CloudFront → portal)
│   ├── Microsoft Entra ID (SSO)
│   └── Role-based access (Marketing User, Marketing Manager, Executive Viewer, Admin)
│
├── Portal Layer [Phase 2]
│   ├── Performance
│   ├── CRM & Lifecycle
│   ├── Organic & Merchandising
│   ├── Marketing Ops
│   ├── Reputation
│   ├── Cross-Channel Brief
│   ├── Category Growth [Phase 2]
│   ├── Supplier Intelligence [Phase 2]
│   ├── Demand Forecast [Phase 2]
│   ├── Promo Simulator [Phase 2]
│   └── Knowledge Search [Phase 2]
│
├── Thin Control Layer
│   ├── Next.js middleware (NOT a separate gateway)
│   ├── Session validation
│   ├── Role checks
│   ├── Module access rules
│   └── Request logging / audit hooks
│
├── Read API Layer
│   └── GraphQL / REST read service (portal reads only)
│
├── Data Layer (PostgreSQL on EC2)
│   ├── agent_outputs
│   ├── agent_logs
│   ├── metrics_history
│   ├── system_health
│   ├── delivery_log
│   └── bot_interactions
│
├── Runtime Layer (AWS EC2 t3.xlarge)
│   ├── Specialist agents (cron-scheduled)
│   ├── Multi-model router
│   ├── Output validator
│   ├── Teams posting worker
│   ├── Teams bot service
│   ├── Executive email worker
│   └── Health + logging scripts
│
├── Multi-Model Routing Layer
│   ├── OpenAI GPT-4o-mini (routing / classification / normalization)
│   ├── Claude Sonnet (default production execution)
│   └── Claude Opus (escalation — complex synthesis only)
│
├── Phase 1 Specialist Agents (daily, cron)
│   ├── Performance Agent        06:00 → GA4, Google Ads, Shopping, Meta, TikTok, LinkedIn, X
│   ├── CRM & Lifecycle Agent    06:30 → Email platform, cart recovery, churn
│   ├── Reputation Agent         07:00 → Trustpilot, Google Business
│   ├── Marketing Ops Agent      07:15 → KPI integrity, tracking QA, coupon dependency
│   └── Cross-Channel Brief      07:30 → Synthesis → Teams + email to Denis
│
├── Phase 2 Specialist Agents
│   ├── Organic & Merchandising Agent   (Search Console, Ahrefs, product feed)
│   ├── Category Growth Agent           (marketplace-specific intelligence)
│   ├── Supplier Intelligence Agent     (co-marketing opportunities)
│   ├── Demand Forecasting Agent        (demand spikes from search + category signals)
│   ├── Promo Simulator Agent           (pre-launch margin/GMV impact estimation)
│   ├── Product Feed Agent              (250k catalog quality + Shopping readiness)
│   ├── Influencer & Partnership Agent  (creator ROI, co-marketing)
│   ├── Traditional Media Correlation   (TV/OOH/Radio lift correlation)
│   ├── Employer Branding Agent         (LinkedIn, talent pipeline)
│   ├── Meeting Intelligence Agent      (transcripts → summaries → Jira tasks)
│   └── Knowledge Retrieval Agent       (Confluence + campaign memory search)
│
├── MCP Integration Layer
│   ├── Performance MCPs
│   │   ├── Google Ads ✓
│   │   ├── Google Shopping ✓ (CRITICAL — no campaigns currently)
│   │   ├── Meta Ads ✓
│   │   ├── LinkedIn Ads ✓
│   │   ├── X Ads ✓ (account creation pending)
│   │   ├── TikTok Ads ✓
│   │   └── GA4 ✓ LIVE (tested 2026-03-13: 464k sessions, 215k users, €13.4M revenue)
│   ├── Search & Organic MCPs [Phase 1]
│   │   ├── Google Search Console ✓
│   │   └── Ahrefs / Semrush ✓
│   ├── CRM MCPs
│   │   └── Email / CRM platform ✓
│   ├── Reputation MCPs
│   │   ├── Trustpilot API ✓ (CRITICAL — 2.0 rating, unclaimed)
│   │   └── Google Business Profile ✓
│   ├── Internal Work MCPs
│   │   ├── Teams posting ✓
│   │   ├── Teams bot ✓
│   │   ├── Outlook / Email via Graph ✓
│   │   ├── Jira ✓
│   │   └── Confluence ✓
│   ├── Business Data MCPs [Phase 1 partial]
│   │   ├── Orders API
│   │   ├── Returns API
│   │   ├── Margin API
│   │   └── Categories API
│   └── Phase 2 MCPs
│       ├── Product Catalog API
│       ├── Supplier API
│       ├── Inventory API
│       ├── Firebase / Adjust (app — pending MK launch)
│       ├── Hootsuite / Buffer (social publishing)
│       └── Campaign Calendar Sheet (traditional media)
│
├── Outputs & Delivery
│   ├── Teams: #marketing-performance
│   ├── Teams: #marketing-crm
│   ├── Teams: #marketing-reputation
│   ├── Teams: #marketing-ops
│   ├── Teams: #marketing-summary
│   ├── Teams: #executive-summary
│   ├── Email: Denis (executive brief)
│   └── Portal modules (detailed analysis)
│
└── Reliability Layer
    ├── CloudWatch (EC2 + custom alarms)
    ├── S3 (nightly DB dump + versioning)
    ├── EBS snapshots (weekly)
    ├── Secrets Manager (all credentials)
    ├── Output schema validation (before every DB write)
    ├── Per-agent token caps
    └── system_health table (DB-backed health state)
```

---

## 5. Infrastructure flow

```
Users
  ↓
ai.ananas.mk
  ↓
Next.js Portal (AWS CloudFront + EKS/ALB)
  ↓
Microsoft Entra ID + Next.js Middleware
  ↓
GraphQL / Read API
  ↓
PostgreSQL (on EC2)
  ↑
Claude Runtime (EC2 t3.xlarge)
  ↑
Multi-Model Router (GPT-4o-mini → Sonnet → Opus)
  ↑
Phase 1 Specialist Agents (cron 06:00–07:30)
  ↑
MCP Integration Layer (11+ connectors)
  ↑
Marketing / Business / Internal Systems
  ↓
Outputs: Teams channels + Email + Portal
  ↓
CloudWatch / S3 Backups / Secrets Manager
```

---

## 6. Multi-model routing (3-tier budget design)

| Tier | Model | Purpose | Approx cost/MTok input |
|---|---|---|---|
| Router | OpenAI GPT-4o-mini | Intent classification, routing, normalization | $0.15 |
| Default | Claude Sonnet | All 5 Phase 1 agents, standard execution | $3.00 |
| Escalation | Claude Opus | Complex synthesis, executive reasoning only | $5.00 |

**Why GPT-4o-mini as router:** routing and classification calls are frequent but cheap. Using Sonnet for every routing decision wastes budget. The router handles pre-checks, then Sonnet does the actual work.

**Token controls:**
- Per-run token cap: 50k Sonnet / 30k Opus
- Per-day token cap per agent: 200k
- All model usage logged to `agent_logs`
- Prompt caching enabled for stable context

---

## 7. Phase 1 agent detail

### Performance Agent (06:00)
- **Sources:** GA4 ✓LIVE, Google Ads, Google Shopping, Meta, TikTok, LinkedIn, X
- **Key metrics:** POAS per campaign, blended ROAS, Google Shopping Impression Share, CPC trend, CVR by device/channel
- **Critical note:** Google Shopping Impression Share is specifically tracked because Ananas has 250k products with ZERO Shopping campaigns currently
- **Teams output:** `#marketing-performance`

### CRM & Lifecycle Agent (06:30)
- **Sources:** CRM/email platform
- **Key metrics:** Cart abandonment rate (target <65%), cart recovery rate (target >20%), email revenue per send (target >€0.40), churn rate at 30/60/90 days
- **Teams output:** `#marketing-crm`

### Reputation Agent (07:00)
- **Sources:** Trustpilot API, Google Business Profile
- **Key metrics:** Review count, response rate (target 100%), average response time (target <24h), sentiment trend
- **Critical note:** Trustpilot currently at 2.0 with 100% negative reviews — profile not yet claimed
- **Alerts:** New negative review, response rate below 80%, rating drop
- **Teams output:** `#marketing-reputation`

### Marketing Ops Agent (07:15)
- **Sources:** GA4, Orders API, Returns API
- **Key metrics:** Coupon dependency ratio (CRITICAL), tracking health, campaign analysis coverage
- **Critical note:** Coupon dependency ratio is a priority metric because current sales are heavily driven by marketing-budget coupons — this masks real acquisition efficiency
- **Alerts:** Coupon dependency above threshold, missing tracking events
- **Teams output:** `#marketing-ops`

### Cross-Channel Brief Agent (07:30)
- **Sources:** outputs from all 4 agents above (from DB)
- **Outputs:** Marketing team brief → `#marketing-summary`, Executive brief → `#executive-summary` + email to Denis
- **Model:** Sonnet default, escalates to Opus for complex executive synthesis

---

## 8. Metric coverage in Phase 1

| Category | Coverage | Notes |
|---|---|---|
| Paid acquisition (all channels) | ✅ Full | Google Ads, Shopping, Meta, TikTok, LinkedIn, X |
| GA4 analytics | ✅ Full | LIVE and tested |
| Google Shopping Impression Share | ✅ Full | NEW — added based on gap analysis |
| CRM / lifecycle | ✅ Full | Cart recovery, email revenue, churn |
| Reputation | ✅ Full | Trustpilot + Google Business |
| Coupon dependency | ✅ Full | NEW — critical monitoring metric |
| POAS per campaign | ✅ Full | NEW — campaign-level, not just blended |
| Contribution margin waterfall | ✅ Full | NEW — Finance-aligned step-by-step |
| Search / organic | ✅ Phase 1 | Search Console + Ahrefs |
| Category-level profitability | 🟡 Partial | Depends on business API access |
| Product feed health | 🟡 Partial | Moved to Phase 2 agent |
| Supplier intelligence | ❌ Phase 2 | Category Growth + Supplier agents |
| Demand forecasting | ❌ Phase 2 | Demand Forecasting agent |
| Promo simulator | ❌ Phase 2 | On-demand agent |
| App metrics | ❌ Phase 2 | Pending MK app launch |
| Social publishing | ❌ Phase 2 | Hootsuite MCP |
| Traditional media lift | ❌ Phase 2 | Correlation agent |

---

## 9. Reliability and governance

**Backups:**
- Nightly PostgreSQL dump → encrypted S3 with versioning
- Daily EBS snapshots (7 daily / 4 weekly / 3 monthly retention)
- Restore test should be performed periodically

**Secrets:**
- All credentials in AWS Secrets Manager
- No secrets in GitHub repo or EC2 environment files
- Service accounts for all production integrations
- User ADC for local development only

**Output validation:**
- Every agent output validated against JSON schema before DB write
- Required fields enforced (agent_name, date_range, module, output_type, data)
- Validation failures: rejected, logged, Teams alert if critical

**Health monitoring:**
- CloudWatch for EC2/system alarms
- `system_health` table tracks per-component status
- Teams alert on: agent failure, missing run, brief failure, connector error

**Graceful degradation:**
- Portal shows last successful output + timestamp + status banner
- Never shows blank page on agent failure

---

## 10. Phase 2 priorities

Ranked by business impact for Ananas specifically:

1. **Portal application** — Claude Code implementation with FE/BE skills
2. **Category Growth Agent** — most important marketplace intelligence
3. **Supplier Intelligence Agent** — marketplace revenue lever
4. **Promo Simulator** — pre-launch margin safety
5. **Product Feed Agent** — 250k catalog quality for Shopping
6. **Demand Forecasting** — react before competitors
7. **Organic & Merchandising Agent** — full SEO automation
8. **Meeting Intelligence** — meeting summaries → Jira
9. **Knowledge Retrieval** — institutional memory
10. **Influencer & Partnership Agent** — creator ROI tracking
11. **Traditional Media Correlation** — offline lift measurement
12. **Employer Branding Agent** — LinkedIn + talent pipeline
13. **App Analytics** — pending MK app launch (Firebase/Adjust)
14. **Social Publishing MCP** — Hootsuite integration

---

## 11. Infrastructure comparison: AWS vs Hetzner

| | AWS (Primary) | Hetzner (Fast-lane backup) |
|---|---|---|
| Runtime host | EC2 t3.xlarge (~$120/mo) | CPX41 8vCPU/16GB (~€30/mo) |
| Database | PostgreSQL on EC2 | PostgreSQL on same server |
| Secrets | Secrets Manager | Encrypted env + restricted IAM |
| Backups | S3 + EBS snapshots | Storage Box BX11 (~€3/mo) |
| Monitoring | CloudWatch | DB-backed + Teams alerts |
| Auth | Entra ID SSO | Same Entra ID |
| Portal hosting | EKS/CloudFront | Same domain, separate deploy |
| Governance | Full enterprise | Lean but solid |
| When to use | Standard path | When AWS tickets/approvals block speed |
| Total Phase 1 infra | ~$150–220/mo | ~€60–100/mo |

---

## 12. Repository governance

All architectural decisions must update:
1. `config/agents.json` — agent definitions
2. `config/metrics.json` — KPI definitions
3. `config/model-routing.json` — model assignments
4. `config/schedules.json` — run times
5. `config/integrations-matrix.json` — connector specs
6. `docs/architecture/architecture-v1.md` — this document
7. `docs/architecture/CHANGELOG.md` — what changed and why

---

## 13. What was added in v2 (this revision)

Based on full GPT conversation audit:

- **OpenAI GPT-4o-mini** added as the 3rd model tier (routing layer)
- **Google Shopping Impression Share** added as explicit Phase 1 metric
- **POAS per campaign** — campaign-level, not just blended
- **Contribution margin waterfall** — Finance-aligned step-by-step formula
- **Coupon dependency ratio** — critical monitoring metric per operational audit
- **Google Search Console** — moved from Phase 2 to Phase 1
- **Trustpilot API spec** — added to integrations matrix with endpoint
- **CLV/CAC ratio** — added with 3:1 target
- **Cost per Insight** — AI system operational metric
- **Automations Active/Total** — AI system health metric
- **Category Growth Agent** — fully specified Phase 2 agent
- **Supplier Intelligence Agent** — Phase 2 marketplace agent
- **Demand Forecasting Agent** — Phase 2 agent
- **Promo Simulator Agent** — Phase 2 on-demand agent
- **Product Feed Agent** — Phase 2 agent for 250k catalog
- **Influencer & Partnership Agent** — Phase 2
- **Traditional Media Correlation Agent** — Phase 2
- **Employer Branding Agent** — Phase 2
- **Hootsuite/Buffer MCP** — Phase 2 social publishing
- **Firebase/Adjust** — Phase 2 pending MK app launch
- **X Ads** — noted as Phase 1 with account creation pending
- **Berry HR** — noted as existing HR system (relevant for employer branding)
- **Promo simulator metrics** — new metrics group
- **App metrics** — Phase 2 metrics group added

