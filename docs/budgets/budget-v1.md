# Budget — v2
**Last updated:** 2026-03-14

## Budget logic
Three cost layers:
1. Fixed cloud infrastructure (EC2, storage, DNS, CDN)
2. Variable model and API usage (tokens per agent run)
3. Third-party tool costs (Trustpilot API, Ahrefs/Semrush, etc.)

The main variable cost is model token usage. This is why the architecture uses a 3-tier model routing strategy, per-run token caps, and controlled Opus usage.

---

## Phase 1 infrastructure — AWS (primary path)

| Component | Monthly cost |
|---|---|
| EC2 t3.xlarge (on-demand) | ~$120 |
| 200 GB gp3 EBS volume | ~$16 |
| S3 backups + versioning | ~$3–5 |
| Secrets Manager | ~$2 |
| Route 53 hosted zone | ~$1 |
| CloudFront (low traffic) | ~$2–5 |
| CloudWatch (basic) | ~$3–5 |
| **AWS fixed total** | **~$147–$154/mo** |

> EC2 Reserved Instance (1-year, no upfront) reduces to ~$68/mo — recommended after Month 3 if platform is stable.

---

## Phase 1 infrastructure — Hetzner (fast-lane backup)

| Component | Monthly cost |
|---|---|
| CPX41 (8 vCPU, 16 GB RAM) | €29.99 |
| Additional storage (if needed) | €3–5 |
| Storage Box BX11 (backups) | €3.19 |
| **Hetzner fixed total** | **~€37–38/mo** |

Use Hetzner if AWS provisioning is delayed by internal approval cycles. Identical codebase — same config, same agents, same schema.

---

## Model usage — 3-tier routing

### Tier costs (per million tokens)
| Model | Input | Output |
|---|---|---|
| OpenAI GPT-4o-mini (router) | $0.15 | $0.60 |
| Claude Sonnet (default) | $3.00 | $15.00 |
| Claude Opus (escalation) | $5.00 | $25.00 |

### Daily agent run estimates (Phase 1, 5 agents)
| Scenario | Sonnet tokens/day | Opus tokens/day | Router tokens/day | Daily model cost |
|---|---|---|---|---|
| Lean | ~40k | ~5k | ~20k | ~$1.75 |
| Moderate | ~100k | ~15k | ~50k | ~$4.80 |
| Heavy | ~200k | ~30k | ~100k | ~$9.60 |

---

## Scenario A — Lean / controlled launch (~$220/mo AWS)

| Line item | Monthly |
|---|---|
| AWS fixed infra | $147–$154 |
| OpenAI router | ~$2 |
| Claude Sonnet | ~$52 |
| Claude Opus | ~$15 |
| **Total** | **~$216–$223** |

**Working budget line: $250/month**

---

## Scenario B — Moderate / realistic operating mode (~$380/mo AWS)

| Line item | Monthly |
|---|---|
| AWS fixed infra | $147–$154 |
| OpenAI router | ~$5 |
| Claude Sonnet | ~$145 |
| Claude Opus | ~$45 |
| Ahrefs/Semrush (if needed) | ~$50–$99 |
| **Total** | **~$352–$448** |

**Working budget line: $400/month**

---

## Scenario C — Heavy / high adoption (~$620/mo AWS)

| Line item | Monthly |
|---|---|
| AWS fixed infra | $147–$154 |
| OpenAI router | ~$10 |
| Claude Sonnet | ~$290 |
| Claude Opus | ~$90 |
| Ahrefs/Semrush | ~$99 |
| **Total** | **~$636–$643** |

**Upper safe limit: $650/month — review required if exceeded**

---

## Annual view

| Scenario | Monthly | Annual |
|---|---|---|
| Lean | $250 | ~$3,000 |
| Moderate | $400 | ~$4,800 |
| Heavy | $650 | ~$7,800 |
| Hetzner fast-lane (first 3 months) | €75 | ~€225 total bridge |

---

## Phase 2 budget additions (estimate)

Phase 2 adds 11 agents but most are weekly (not daily), so token cost grows modestly.

| Additional Phase 2 cost | Monthly estimate |
|---|---|
| 11 weekly agents (~2 agents/day average) | +$60–120 Sonnet |
| Opus escalation increase | +$20–40 |
| App analytics API (Firebase/Adjust) | TBC |
| Social publishing API (Hootsuite) | ~$49–$99 |
| **Phase 2 addition** | **+$130–$260/mo** |

**Phase 2 working budget: $550/month moderate, $900/month heavy**

---

## Budget governance
- Log model_used and estimated_cost for every agent run (agent_logs table)
- Weekly token usage report sent to Denis channel (cost per insight metric)
- If daily token cost exceeds $15/day on moderate scenario → review escalation triggers
- EC2 Reserved Instance after Month 3 if platform stable (saves ~$52/mo)
