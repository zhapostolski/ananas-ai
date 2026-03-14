# Ananas AI Platform — Budget
**Last updated:** 2026-03-14
**Scope:** Phase 1 operating cost + Phase 2 projection

---

## Phase 1 monthly cost (5 agents, daily cron, Teams + email output)

### Infrastructure (AWS)

| Component | Spec | Monthly cost |
|---|---|---|
| EC2 t3.xlarge | 4 vCPU / 16GB RAM — runtime + PostgreSQL | ~$120 |
| EBS storage | 100GB gp3 (OS + DB + logs) | ~$8 |
| S3 backups | Nightly DB dump, versioned, ~5GB/mo | ~$1 |
| CloudWatch | Custom alarms + log retention | ~$5 |
| AWS Secrets Manager | 5 secrets (API keys, DB creds) | ~$2 |
| Data transfer | Outbound to Teams/email (minimal) | ~$1 |
| **Infrastructure total** | | **~$137/mo** |

> **Hetzner alternative:** CPX41 (8 vCPU / 16GB, €29/mo) + Storage Box BX11 (€3/mo) = **~€32/mo infra**. Same model costs apply. Suitable if AWS procurement is slow to start.

---

### AI model costs (Phase 1 — 5 agents, 30 days)

| Model | Usage | Monthly cost |
|---|---|---|
| Claude Sonnet 4.6 (default) | 5 agents × ~7k tokens/run × 30 days = ~1M tokens | ~$8 |
| Claude Opus 4.6 (escalation only) | ~2–3 escalations/week × 20k tokens = ~250k tokens | ~$4 |
| OpenAI GPT-4o-mini (router) | Routing + classification, ~150k tokens/mo | <$1 |
| **Model total** | | **~$13/mo** |

> Token costs drop further with prompt caching enabled on stable system prompts (configured in `config/model-routing.json`). Estimated 30–40% reduction on Sonnet input tokens after first week.

---

### External API costs

| Service | Notes | Cost |
|---|---|---|
| Google Ads API | Free (usage quotas apply) | $0 |
| Meta Marketing API | Free (usage quotas apply) | $0 |
| Trustpilot API | Free tier sufficient for Phase 1 | $0 |
| Google Analytics Data API | Free | $0 |
| Microsoft Graph API (Teams/Email) | Included in Microsoft 365 license | $0 |
| **API total** | | **$0** |

---

### Phase 1 total

| | AWS path | Hetzner path |
|---|---|---|
| Infrastructure | ~$137/mo | ~€32/mo |
| AI models | ~$13/mo | ~$13/mo |
| External APIs | $0 | $0 |
| **Total** | **~$150/mo** | **~€45/mo** |
| **Annual** | **~$1,800/yr** | **~€540/yr** |

---

## Phase 2 cost additions (portal + 11 additional agents)

| Addition | Monthly delta |
|---|---|
| Larger EC2 or second instance (portal + heavier agents) | +$50–80 |
| More model usage (11 agents, some weekly, some on-demand) | +$20–40 |
| Vercel / CloudFront for portal hosting (ai.ananas.mk) | +$20 |
| Additional S3 storage (meeting audio, knowledge archive) | +$5 |
| **Phase 2 total** | **~$250–280/mo** |

---

## ROI framing

The platform is not a cost centre — it surfaces revenue gaps and operational losses that are currently invisible. Context:

| Gap currently visible | Estimated revenue/cost impact |
|---|---|
| Google Shopping: 0 campaigns, 250k products | Revenue opportunity lost daily — first campaign pays for Phase 1 in Month 1 |
| Trustpilot 2.0 unclaimed — suppresses paid media efficiency | Negative reviews reduce ad CTR and conversion rate |
| Coupon dependency masking real CAC | Margin erosion unquantified without daily monitoring |
| No cart recovery automation | Industry standard: 5–15% of abandoned carts recoverable |
| No email lifecycle flows | Email CRM revenue gap — no welcome, churn, or win-back series |

**Payback:** One recovered Google Shopping impression share percentage point or one claimed and responded Trustpilot review campaign covers months of platform cost.

---

## Budget assumptions

- Engineering time not included (platform built and maintained internally)
- No third-party MCP licensing fees — all integrations use official free-tier APIs
- Token estimates based on Phase 1 agent scope; may vary ±30% depending on data volume
- AWS pricing based on us-east-1 on-demand rates; Reserved Instance (1yr) reduces EC2 by ~35%
