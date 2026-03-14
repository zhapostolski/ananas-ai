# Ananas AI Platform — Success Metrics
**Last updated:** 2026-03-14
**Purpose:** Define what "working" looks like at Month 1, 2, and 3

---

## Month 1 — Platform is live and reliable

The goal in Month 1 is operational reliability, not insight quality. The brief must arrive every day.

| Metric | Target | How measured |
|---|---|---|
| Agent uptime | ≥95% (≤1 failure/week per agent) | `system_health` table + `agent_logs` |
| Daily brief delivery | Denis receives email every working day before 08:00 | `delivery_log` table |
| Teams channel posting | ≥95% of posts delivered on schedule | `delivery_log` table |
| Output validation pass rate | ≥98% of agent outputs pass schema validation | `agent_logs` status field |
| Mean time to alert on failure | <15 minutes from agent failure to Teams alert | Manual review of `agent_logs` |
| Trustpilot profile claimed | ✅ Done | Manual |
| First Trustpilot responses sent | ≥5 responses in Month 1 | Reputation Agent tracking |
| Coupon dependency ratio visible | Ratio tracked and trending | Marketing Ops Agent |
| Google Shopping impression share tracked | Metric live in daily brief | Performance Agent |

---

## Month 2 — Data quality and team adoption

The goal in Month 2 is that the team actually uses the briefs to make decisions.

| Metric | Target | How measured |
|---|---|---|
| Team brief engagement | ≥5 of 8 team members read their channel daily | Teams analytics |
| Alert-to-action rate | ≥1 action taken per week from an agent alert | Manual log / Jira ticket |
| Coupon dependency ratio trend | Visible trend (up or down — point is awareness) | Marketing Ops Agent |
| Trustpilot response rate | ≥80% of new reviews responded to within 24h | Reputation Agent |
| Trustpilot rating | Trend upward from 2.0 | Reputation Agent |
| Google Shopping | First campaign live or in approved plan | Manual |
| Cart recovery rate | Baseline established — target >20% | CRM Agent |
| Email revenue per send | Baseline established — target >€0.40 | CRM Agent |
| Denis brief satisfaction | Subjective: "useful" on ≥3 of 5 working days | Direct feedback |

---

## Month 3 — Intelligence quality

The goal in Month 3 is that the brief surfaces things the team wouldn't have caught manually.

| Metric | Target | How measured |
|---|---|---|
| Anomalies detected | ≥3 genuine anomalies surfaced in the month | `agent_logs` + team feedback |
| Agent escalations to Opus | ≤5% of runs escalate (keeps cost controlled) | `agent_logs` model_used field |
| Cost per insight | Total monthly cost ÷ actionable alerts | Budget + alert count |
| Contribution margin trend | Tracked week-over-week in executive brief | Marketing Ops Agent |
| Google Shopping impression share | ≥10% (from 0%) | Performance Agent |
| Coupon dependency ratio | Decreasing trend or stable with explanation | Marketing Ops Agent |
| Phase 2 case | Clear business case for at least 2 Phase 2 agents | Review meeting output |

---

## AI system health metrics (ongoing)

Tracked in `config/metrics.json` under `ai_system` group:

| Metric | Target |
|---|---|
| Daily token usage per agent | <200k tokens/agent/day |
| Agent uptime % | ≥95% |
| Automations active / total | Phase 1: 5/5 |
| Cost per insight | <$5 per actionable alert |
| Anomalies detected per week | ≥1 (platform is earning its keep) |

---

## What failure looks like (and what to do)

| Symptom | Likely cause | Action |
|---|---|---|
| Brief missing for 2+ days | Agent failure or Teams API issue | Check `agent_logs`, restart agent, check Microsoft Graph token expiry |
| Brief arrives but feels generic | Prompt quality or data source issue | Review agent system prompt + check MCP data freshness |
| No alerts in 2+ weeks | Either everything is fine (unlikely) or thresholds too loose | Review alert thresholds in agent definitions |
| Opus escalations above 10% | Complexity triggers too sensitive | Tighten escalation rules in `config/model-routing.json` |
| Cost spike | Token caps not enforcing | Check per-agent token cap configuration |

---

## Phase 1 → Phase 2 gate criteria

Phase 2 build should begin when Phase 1 meets all three:

1. Platform has run reliably for 4+ consecutive weeks (agent uptime ≥95%)
2. Denis and ≥3 team members describe the brief as useful in day-to-day decisions
3. At least one revenue or margin action has been directly attributed to a platform alert
