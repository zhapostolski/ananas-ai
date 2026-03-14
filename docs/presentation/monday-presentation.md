# Ananas AI Platform — Monday Presentation
**Audience:** Denis (Country Manager) + Marketing Team (8 people)
**Goal:** Approval to build Phase 1
**Last updated:** 2026-03-14

---

## Opening (2 min)

**The problem we're solving isn't data — it's signal.**

We have GA4. We have Google Ads. We have a CRM. We have Trustpilot. We have Meta, TikTok, LinkedIn. But every morning someone has to log into each one, figure out what changed, decide what matters, and write it up. That takes hours. Most days it doesn't happen at all.

The result: decisions made on yesterday's instinct, not this morning's data.

**Ananas AI fixes this.** Five specialist agents run overnight, collect data from every channel, and deliver a structured brief to Denis's inbox and the team's Teams channels before 08:00 — every working day, automatically.

---

## The six things we already know are wrong (3 min)

We don't need AI to tell us we have problems. We already know them. What we need is daily visibility so they actually get fixed.

| Known problem | Why it's not getting fixed today |
|---|---|
| **Google Shopping: 0 campaigns, 250k products** | No one is watching impression share daily |
| **Trustpilot 2.0 — profile unclaimed** | No alert when a new review appears |
| **Coupons driving most sales — masking real CAC** | Coupon dependency ratio not tracked |
| **No email lifecycle automations** | Cart recovery revenue sitting untouched |
| **No campaign post-launch analysis** | Learnings not captured systematically |
| **Cross-channel blind spots** | No single view across all channels |

The platform doesn't solve these overnight. It makes them impossible to ignore.

---

## What Phase 1 delivers (5 min)

### Five specialist agents, running daily

| Time | Agent | What it covers | Teams channel |
|---|---|---|---|
| 06:00 | Performance | GA4, Google Ads, Shopping, Meta, TikTok, LinkedIn, X | `#marketing-performance` |
| 06:30 | CRM & Lifecycle | Cart recovery, email revenue, churn signals | `#marketing-crm` |
| 07:00 | Reputation | Trustpilot, Google Business — every review, every rating change | `#marketing-reputation` |
| 07:15 | Marketing Ops | Coupon dependency, tracking health, contribution margin | `#marketing-ops` |
| 07:30 | Cross-Channel Brief | Synthesis of all four → Denis email + executive summary | `#executive-summary` |

### What Denis gets
- Email by 07:40 — plain text, under 300 words, mobile-readable
- Always includes: contribution margin, coupon dependency ratio, Trustpilot score, Shopping impression share, top alert

### What the team gets
- One Teams channel per domain — no noise, just what's relevant to each person's role
- Each post under 400 words — readable in under 2 minutes

---

## How it works (3 min — technical, keep brief)

```
Marketing systems (GA4, Google Ads, Meta, Trustpilot...)
        ↓
  5 specialist AI agents (overnight cron, 06:00–07:30)
        ↓
  3-tier model routing: GPT-4o-mini router → Claude Sonnet → Claude Opus
        ↓
  PostgreSQL (structured outputs, logs, metrics history)
        ↓
  Teams channels + Denis email (07:35–07:40)
        ↓
  Portal at ai.ananas.mk (Phase 2 — deep analysis on demand)
```

**Key design decisions:**
- **Read-only** in Phase 1 — the platform never touches your business systems
- **AWS EC2** — runs on your infrastructure, data stays internal
- **Specialist-first** — each agent is an expert in its domain, not a generic chatbot
- **Three models, one purpose** — cheap router for decisions, Sonnet for analysis, Opus only for complex synthesis

---

## Cost (1 min)

| | Monthly | Annual |
|---|---|---|
| Phase 1 (AWS) | ~$150 | ~$1,800 |
| Phase 1 (Hetzner — faster to start) | ~€45 | ~€540 |
| Phase 2 (portal + 11 more agents) | ~$280 | ~$3,360 |

**One Google Shopping campaign launched from the first brief pays for Phase 1 in week one.**

---

## What we're asking for today (1 min)

1. **Budget approval:** ~$150/mo for Phase 1
2. **API access:** read-only to Google Ads, Meta, Trustpilot, CRM (standard API access, no new tools)
3. **Microsoft Graph API:** Teams posting + Outlook email (already in M365 license)
4. **AWS:** EC2 instance (or Hetzner if faster)
5. **Green light to build**

---

## Timeline (1 min)

| Week | What's live |
|---|---|
| Week 1 | Infrastructure + database + integrations |
| Week 2 | All 5 agents running with real data |
| Week 3 | Teams + email delivery confirmed |
| Week 4 | First full week of daily briefs — Denis receives first executive brief |
| Month 2 | Platform stable, team running on it daily |
| Months 4–9 | Phase 2: portal, 11 more agents, Teams bot, meeting intelligence |

---

## Success criteria — Month 1

The build is successful if after 30 days:

- Denis receives a brief every working morning before 08:00
- Trustpilot profile is claimed and response program is live
- Coupon dependency ratio is tracked and visible in trend
- Google Shopping impression share is monitored and a campaign is in plan or live
- At least one agent alert surfaces something the team didn't catch manually

---

## Phase 2 teaser (30 sec — only if time allows)

Phase 1 is the intelligence layer. Phase 2 makes it interactive and regional:
- **Portal** at ai.ananas.mk — deep-dive modules for each team member's domain
- **Teams bot** — ask questions, get answers from your own data
- **11 more agents** — category growth, supplier intelligence, promo simulator, meeting intelligence
- **Regional expansion** — same platform, new market configuration

---

## Anticipated questions

**"Can't we just use a dashboard?"**
Dashboards require someone to open them. This delivers intelligence to where the team already works — Teams and email — before the day starts.

**"What about data security?"**
Read-only access to business systems. All data processed and stored on Ananas infrastructure (AWS EC2). No data sent to third parties beyond the AI model APIs (Anthropic, OpenAI), which process inputs but don't store them.

**"Who builds and maintains this?"**
Phase 1 is designed to be operated by one person. The platform is config-driven — changing a schedule, adding a metric, or adjusting an alert is a config file change, not a code change.

**"What if it's wrong?"**
Every agent output is validated before it goes to the database. If an agent fails, Teams gets an alert and the last successful output is shown with a timestamp. The system fails loudly, not silently.

**"What about other markets?"**
Phase 1 MK is the proof of concept. The architecture supports multi-market from the start — adding a new market is a configuration change, not a rebuild.
