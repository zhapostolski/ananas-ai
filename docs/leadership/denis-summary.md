# Ananas AI Platform — For Denis
**Role context:** Country Manager
**Last updated:** 2026-03-14

---

## What this is

A daily intelligence system for the Ananas marketing operation. It collects data from every marketing channel and business system overnight, processes it through specialist AI agents, and delivers a structured brief to your inbox and Teams by 07:40 every morning — before you start your day.

You don't log into a dashboard. You don't ask anyone for a report. It's already there.

---

## What you get every morning

| Time | What arrives | Where |
|---|---|---|
| 07:35 | Marketing team brief — channel performance, CRM signals, reputation flags, ops alerts | Teams `#executive-summary` |
| 07:40 | Executive brief — top 5 signals, one recommendation, cost/margin summary | Your Outlook inbox |

**The executive brief is plain text, mobile-readable, and under 300 words.** It surfaces what changed, what needs attention today, and what the team is already handling.

### What the executive brief always includes

1. **Contribution margin** — not just revenue, the margin that matters
2. **Coupon dependency ratio** — what % of sales required a coupon from our marketing budget
3. **Trustpilot score** — with response rate (target: we respond to every review within 24h)
4. **Google Shopping impression share** — are we visible where our 250k products should be?
5. **Top alert** — the single most important signal from the last 24 hours

---

## The six problems it directly monitors

These are the six known gaps in the current operation. The platform watches all of them daily:

| Problem | What the platform does |
|---|---|
| Google Shopping: 0 campaigns despite 250k products | Performance Agent tracks impression share daily — alerts when visibility drops or improves |
| Trustpilot at 2.0 — profile unclaimed, all reviews negative | Reputation Agent monitors new reviews, flags response rate, tracks sentiment trend |
| Sales driven by marketing-budget coupons — masks real CAC | Marketing Ops Agent tracks coupon dependency ratio — alerts if above threshold |
| No campaign post-launch analysis | Performance Agent covers analysis for all active campaigns |
| No email lifecycle automations live | CRM Agent tracks cart recovery rate, churn signals, email revenue per send daily |
| Weak cross-channel visibility | Cross-Channel Brief synthesises all 5 agents into one morning summary |

---

## What it costs

| Phase | Monthly cost | What you get |
|---|---|---|
| Phase 1 (now) | ~$150/mo | 5 agents, daily briefs, Teams + email delivery |
| Phase 2 (Months 4–9) | ~$250–280/mo | Portal, 11 more agents, Teams bot, meeting intelligence |

**For comparison:** a single Google Shopping campaign launched from the first intelligence brief will recover months of platform cost in the first week.

---

## What you need to approve to start

1. **Budget:** ~$150/mo for Phase 1 infrastructure and AI models
2. **API access:** read-only access to Google Ads, Meta, Trustpilot, and CRM platform (no write access in Phase 1)
3. **Microsoft Graph API:** permission to post to Teams channels and send email via Outlook (standard M365 — no new licensing)
4. **AWS:** EC2 instance provisioning (or Hetzner as a faster alternative at ~€45/mo)

**Your time commitment:** reading the brief. That's it for Phase 1.

---

## Timeline to first brief

| Week | Milestone |
|---|---|
| Week 1 | Infrastructure provisioned, database live, integrations configured |
| Week 2 | All 5 agents running with real data |
| Week 3 | Teams + email delivery live, brief format confirmed |
| Week 4 | First full week of daily briefs — calibration and adjustment |
| **Month 2** | Platform stable, team using it daily |

---

## Success criteria — Month 1

The platform is working if, after 30 days:

- [ ] You receive the executive brief every working day before 08:00
- [ ] Trustpilot profile is claimed and first responses are drafted and sent
- [ ] Coupon dependency ratio is visible and trending (up or down — the point is visibility)
- [ ] Google Shopping impression share is tracked and a campaign is either live or in plan
- [ ] At least one agent alert has surfaced something the team didn't already know

---

## Regional expansion

The platform is built to scale. Adding a new market means:
- A new database scope for that market's data
- Agent configurations pointing to that market's ad accounts and business systems
- The same brief format, localised

Phase 1 in MK is the proof of concept. A working Phase 1 is the business case for regional rollout.

---

## Questions you'll likely get from the team

**"Does this replace any tools we use?"** No. It reads from existing tools. It doesn't replace GA4, Google Ads, or your CRM — it reads them and surfaces what matters.

**"Who maintains it?"** One person can operate Phase 1. The platform is designed for a team of 8, not a dedicated ops team.

**"What if an agent fails?"** Teams gets an alert. The portal shows the last successful output with a status banner. Nothing goes silent — failures are visible.

**"Is our data leaving Ananas systems?"** The platform reads your data to generate briefs. No data is stored externally. Everything lives on your AWS EC2 instance.
