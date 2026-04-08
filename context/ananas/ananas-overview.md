```markdown
# Ananas — Company Overview
<!-- Living document. Updated incrementally as source materials are added to context/ananas/raw/. -->
<!-- Last updated: 2026-03-14 | Sources processed: 9 -->

---

## 1. Company Profile

- **Full name:** Ananas
- **Founded:** 2021
- **Headquarters:** Serbia (Balkans region); primary AI platform market: North Macedonia
- **Website:** ananas.rs / ananas.mk
- **Market(s) served:** Serbia (primary); regional Balkan expansion planned; North Macedonia referenced as Phase 1 AI platform market and primary document addressee
- **Business type:** E-commerce marketplace (hybrid — own inventory + third-party sellers)
- **Company size:** ~150–200 employees (est. from org structure)
- **Ownership / structure:** Private; Delta Holding markets referenced as parent/affiliated group (regional rollout context)
- **Market position (MK):** Described as North Macedonia's largest e-commerce marketplace

---

## 2. Products & Categories

- **Core product categories:** Electronics, Home & Living, Fashion, Beauty & Health, Sports, Toys, Food & Groceries, Auto, Garden
- **Number of SKUs / catalog size:** 250,000+ products
- **Own brand vs. third-party:** Primarily third-party sellers on marketplace model; some own-inventory categories
- **Key suppliers / brands:** Wide range of local and international brands across categories
- **Catalog management approach:** Seller self-service portal + internal catalog team

---

## 3. Business Model & Revenue

- **Revenue model:** Marketplace commission + direct retail hybrid
- **Primary revenue streams:** Seller commissions, direct product sales, advertising/promoted listings, logistics services (fulfillment)
- **Pricing strategy:** Competitive pricing; promotional/discount-led acquisition
- **Coupon / discount dependency:** High — coupon-driven sales mask real acquisition efficiency (known critical issue; monitored daily by AI platform)
- **Contribution margin structure:** Tracked as a waterfall: revenue → gross → contribution; monitored by Marketing Ops Agent daily
- **GMV vs. net revenue split:** To be populated

---

## 4. Key Metrics & KPIs

### Known (from GA4 live data — 2026-03-13)
| Metric | Value |
|---|---|
| Sessions | 464,000 |
| Users | 215,000 |
| Revenue | €13.4M |

### Targets & Benchmarks (from whiteboard — 2026-03-13)
| Metric | Current / Noted Value | Target / Benchmark |
|---|---|---|
| Users | 600k × 3 (i.e. target ~1.8M) | — |
| Sessions | 1,800,000 | — |
| Page Views | 3,500,000 | 3 (×?) |
| Product Page Views | 2.2M | — |
| CVR (Conversion Rate) | 1% | — |
| Orders (QTY) | 22,000 | — |
| AOV | 50 | — |
| GMV | 1,100,000 (monthly est.) | — |
| SEO (sessions or users) | — | 630 (unit TBD) |

> ⚠️ *Whiteboard figures are partially legible. Numbers in the right-hand column may represent targets, a second market/channel breakdown, or a comparison period. Interpretation should be confirmed with the team. AOV of ~50 (currency assumed RSD thousands or EUR — to clarify).*

### AI Platform Monitored KPIs (tracked daily from Phase 1)
| Domain | Key Metrics Tracked |
|---|---|
| Performance | POAS per campaign, blended ROAS, CPC trend, CVR by device/channel, GA4 sessions/users/revenue vs. prior period |
| CRM & Lifecycle | Cart abandonment rate, cart recovery rate, email revenue per send, churn rate at 30/60/90 days, active lifecycle automation count |
| Reputation | Trustpilot rating & review count, review response rate (target: 100%), avg response time (target: <24h), sentiment trend, new negative reviews in last 24h |
| Marketing Ops | Coupon dependency ratio, tracking health (GA4 event coverage, missing tags), contribution margin waterfall, KPI integrity |
| Cross-Channel | Top 5 signals across all channels, one prioritised daily recommendation, executive margin/coupon summary |

**Key funnel ratios visible on whiteboard:**
- Sessions → Page Views → Product Pages → CVR 1% → ~22,000 orders
- AOV ~50 → GMV ~1.1M (monthly)
- App noted separately with figure ~50 (AOV or share)

---

## 5. Marketing Channels & Stack

### Active Channels
| Channel | Status | Notes |
|---|---|---|
| Google Ads | Active | Managed by performance team; POAS monitored per campaign |
| Google Shopping | **CRITICAL GAP** | 250k products, 0 campaigns |
| Meta Ads | Active | |
| TikTok Ads | Active | |
| LinkedIn Ads | Active | |
| X (Twitter) Ads | Pending | Account creation pending |
| Email / CRM | Active | Platform TBD (HubSpot / ActiveCampaign / Klaviyo); confirmation of platform is a Phase 1 parallel-track action |
| SEO / Organic | Active | Managed via Search Console + Ahrefs/Semrush; SEO traffic target noted on whiteboard |
| Influencer / Creator | Active | Used for product launches and seasonal campaigns |
| Push Notifications | Active | Web and app push |
| Affiliate | Active | Regional affiliate network |

### Channel Mix Notes (from whiteboard left margin — partially legible)
- References to: Google ~4%, Meta ~50%, something ~29%, other channels including email (~5%), direct (~10%), other (~-)
- *Note: figures are partially illegible; to be confirmed with performance team*

### Internal Tools
- Jira, Asana, Confluence, Teams, SharePoint, Outlook, Berry (HR)
- Jira / Confluence onboarding for the marketing team is a Phase 1 parallel-track action

### Analytics
- **GA4:** LIVE and integrated; service account in use for production AI platform integration
- **GCP Project:** `boreal-coyote-490215-p5` (Google Cloud project hosting the Ananas AI service account)

---

## 6. Team

### Marketing Team
- **Total marketing team size:** 8 people
- **Roles:**
  - 2 Designers
  - 3 Performance marketers
  - 1 Content / Social
  - 1 CRM
  - 1 TBD

### Wider Organisation (from onboarding materials)
- **Structure:** Functional departments — Marketing, Tech/Product, Commercial (Buying & Sellers), Operations/Logistics, Finance, HR, Customer Support
- **Key stakeholders:**
  - **Denis Boskoski** — Country Manager (confirmed full name from master document); recipient of daily AI brief (executive email before 08:00); leads regional expansion agenda; approves AI platform access and budget
  - **Zharko** — AI Platform operator; one person capable of running Phase 1 end-to-end
  - **CMO / Marketing Director** — oversees full marketing function
  - **Head of Performance** — owns paid media channels
  - **Head of Product / Tech** — owns platform, app, and data infrastructure

---

## 7. Customers & Market

- **Target customer profile:** Broad mass-market; primary demographic 25–45, urban, digitally native; secondary 18–24 (TikTok-driven)
- **Primary geographies:** Serbia (core); Bosnia & Herzegovina, Croatia, North Macedonia (expansion targets); MK referenced as Phase 1 AI platform proof-of-concept market
- **Customer acquisition channels:** Performance (Google, Meta, TikTok), organic search, email, direct/app
- **Retention profile:** Repeat purchase driven by promotions and coupons; lifecycle automation gap limits organic retention
- **NPS / satisfaction:** Low — reflected in Trustpilot 2.0 rating; customer service responsiveness flagged as key driver

---

## 8. Reputation & Trust

- **Trustpilot rating:** 2.0 stars — **CRITICAL**
  - Profile not yet claimed
  - Currently 100% negative reviews visible
  - No response strategy in place yet
  - Monitored daily by AI Reputation Agent; alerts on any new negative review within 24h
  - Targets: 100% review response rate; <24h average response time
- **Google Business Profile:** Active (rating TBD); also monitored daily by Reputation Agent
- **Key reputation drivers (negative):** Delivery delays, customer service responsiveness, return process friction
- **Planned remediation:** Claim Trustpilot profile (Phase 1 parallel-track Day 1 action); implement review response program; address root-cause service issues

---

## 9. Technology & Infrastructure

- **E-commerce platform:** Proprietary platform (custom-built)
- **Mobile:** iOS and Android apps (live); Firebase / Adjust app analytics pending MK app launch (Phase 3)
- **Backend stack:** Microservices architecture; cloud-hosted (AWS)
- **Frontend stack:** Next.js, TypeScript (also used for AI platform portal); static assets served via Next.js `/_next/static/media/` pipeline (confirmed from asset URL pattern on ananas.mk)
- **AI platform:** Ananas AI — full platform detail in Section 15 below
- **Data / Analytics:** GA4, internal Orders / Returns / Margin APIs
- **Automation:** No lifecycle email automations currently live (gap; monitored by CRM Agent)
- **Seller portal:** Self-service onboarding and listing management for marketplace sellers

---

## 10. Current Challenges & Priorities

1. **Trustpilot 2.0 rating** — profile unclaimed, no response program — reputational risk; Day 1 action
2. **Google Shopping gap** — 250k products with zero campaigns — major revenue opportunity
3. **Coupon dependency** — marketing-budget coupons driving most sales — masks real efficiency; tracked as priority metric daily
4. **No email lifecycle automations** — cart recovery, churn flows, welcome series not live
5. **CRM platform TBD** — email platform not yet confirmed; audit is a Phase 1 parallel-track action
6. **X Ads account** — not yet created
7. **Regional expansion** — Serbia is core market; Balkan expansion (BA, HR, MK) in planning — requires localisation of ops, marketing, and legal
8. **Seller growth** — increasing marketplace seller count and GMV share is a strategic priority
9. **App engagement** — push notification and in-app personalisation underutilised
10. **Traffic scale gap** — whiteboard indicates current users ~600k with a 3× growth target; CVR at 1% and GMV ~1.1M/month suggest significant headroom to improve both traffic and conversion
11. **Campaign post-launch analysis discipline** — formal post-launch analysis process not yet embedded in team workflow; Phase 1 parallel-track action
12. **Phase 1 AI platform completion** — several integrations and access items pending IT/Azure admin action (see Section 15, Pending Actions)

---

## 11. Brand Voice & Guidelines

- **Brand personality:** Approachable, energetic, locally rooted but modern; positioned as "the Balkan Amazon" with a friendly, helpful tone
- **Tone of voice:** Warm, direct, conversational; avoids corporate stiffness; humorous where appropriate in social/TikTok contexts
- **Visual identity:**
  - **Primary logo colour:** Orange-red (`#FE502A`) — used for the wordmark "ananas"
  - **Accent colour:** Green (`#84BD00`) — used for the decorative bar element above the wordmark (visually evokes pineapple leaves, consistent with the brand name)
  - **Logo layout:** Horizontal lockup; wordmark in lowercase; green bar sits above the "an" portion of the logo
  - **Logo icon asset:** Served as SVG at `/_next/static/media/ananas-logo-icon.e438d94d.svg` on ananas.mk — content-hashed filename confirms standard Next.js static asset pipeline
  - Bold colour palette; clean product-forward layouts; strong use of promotional/price-led creative
- **Do's and don'ts:**
  - ✅ Highlight value, deals, and convenience
  - ✅ Use local language and cultural references
  - ✅ Be responsive and human in customer comms
  - ❌ Avoid overly formal or distant language
  - ❌ Do not make delivery/service promises that operations cannot fulfil (key reputational risk)

---

## 12. Competitive Landscape

- **Direct competitors:** Kupujemprodajem (C2C/marketplace), eKupi (HR), Shoppster, Mall.rs, and international players (eMag, AliExpress)
- **Market position:** North Macedonia's largest e-commerce marketplace (confirmed); challenger/growth player in Serbia; aspires to be #1 regional e-commerce platform
- **Differentiation:** Local brand identity, faster regional logistics vs. international players, broad category coverage, seller ecosystem

---

## 13. Campaigns & Promotions

- **Seasonal peaks:** Black Friday, Christmas/New Year, Summer Sales, Back to School, Valentine's Day, Mother's Day
- **Recurring promotions:** Weekly deals, flash sales, category-specific discount events, loyalty/coupon programs
- **Co-marketing with suppliers:** Joint promotions with key brand suppliers; sponsored placements within the platform
- **Campaign approach:** Heavy reliance on discount/coupon mechanics; creative refresh needed to build brand equity beyond price

---

## 14. Additional Context

- The onboarding document indicates Ananas is in a **scale-up phase**: the core platform is operational, seller base is growing, and the focus is shifting from pure acquisition to retention, brand building, and regional expansion.
- **Mentor/onboarding programme** is in place — suggesting investment in structured knowledge transfer and team capability building, likely related to marketing maturity uplift.
- Customer logistics experience (delivery speed, returns) is identified as a key lever for both retention and reputation improvement.
- Whiteboard session (2026-03-13) shows active internal planning around traffic funnel metrics, with a clear 3× user growth ambition and focus on improving CVR from the current 1% baseline.
- **Delta Holding** is referenced as the broader group within which Ananas operates; Phase 3 of the AI platform is framed as a proof-of-concept for rollout across all Delta Holding markets.

---

## 15. Ananas AI Platform

### Overview
An internal marketing intelligence system (Version 1.0, March 2026). Automated — not a dashboard requiring login. Runs every morning, processes data from all marketing channels, and delivers structured output to Microsoft Teams and email before 07:30. Maintained in GitHub at `github.com/zhapostolski/ananas-ai`. Classified as Internal — Confidential.

**Current status:** Phase 1 is operational. Five specialist agents run daily on AWS EC2, the portal is live, GA4 is integrated and returning real data, and the first users have logged in. Platform is now moving into Phase 2.

**Value proposition:** Every morning by 07:30, every person on the team knows exactly what changed, what is at risk, what needs attention today, and where the opportunity is — without pulling a single report. Estimated cost per actionable insight: under €0.50.

### Design Principles
- Built on existing Ananas stack: Next.js, TypeScript, AWS
- Five specialist agents in Phase 1, each owning one domain; no permanent orchestrator
- Portal-first for deep analysis; Teams-first for daily communication
- Read-only access to all business systems in Phase 1
- All agent outputs validated against JSON schema before database storage; validation failures trigger Teams alert and are never silently ignored
- Prompts, metrics, routing rules, and schedules are versioned config — not hardcoded
- Three-tier model routing: cheap router → Claude Sonnet (default) → Claude Opus (escalation)
- Single EC2 host in Phase 1
- Integrations use Model Context Protocol (MCP), REST APIs, and Google SDKs
- Portal secured by Microsoft Entra ID SSO — no local passwords; role-based access enforced at middleware layer on every route

### Daily Schedule
| Time | Agent | Action |
|---|---|---|
| 06:00 | Performance Agent | GA4, Google Ads, Shopping, Meta, TikTok, LinkedIn |
| 06:30 | CRM & Lifecycle Agent | Cart abandonment, recovery rate, email revenue, churn signals |
| 07:00 | Reputation Agent | Trustpilot and Google Business — new reviews, rating changes |
| 07:15 | Marketing Ops Agent | Coupon dependency ratio, tracking health, KPI integrity |
| 07:30 | Cross-Channel Brief Agent | Synthesises all four outputs; posts to Teams + emails Denis |

### Infrastructure
- **Primary:** AWS EC2 t3.xlarge (eu-central-1), Security Groups, Route 53, CloudFront, S3 (versioned/encrypted backup), Secrets Manager, CloudWatch
- **Fast-lane alternative:** Hetzner CPX41 (8 vCPU / 16GB, ~€29/mo) + Storage Box BX11 (~€3/mo) — identical codebase, used if AWS provisioning is slow
- **Database:** SQLite (Phase 1); PostgreSQL migration planned for Q2 2026 (Phase 2); nightly dump to S3 (Phase 2); daily dump to EC2 host (Phase 1)
- **Portal URL:** `ai.ananas.mk/dashboard`
- **Teams channels:** 6 dedicated channels for agent outputs
- **Process management:** PM2 (auto-restarts portal on crash); CloudWatch monitors EC2 health

### AI Model Routing
- Default: Claude Sonnet (50k tokens/run; 200k/agent/day)
- Escalation: Claude Opus for Cross-Channel Brief synthesis when complexity is high (30k tokens/run)
- Prompt caching enabled for stable system prompts — estimated 30–40% reduction in Sonnet input costs after Week 1
- All model usage and cost logged automatically

### Phase 1 Agents (Live)
Five specialist agents — Performance, CRM & Lifecycle, Reputation, Marketing Ops, Cross-Channel Brief. Each owns one intelligence domain, runs on a defined schedule, connects to specific data sources, and produces a structured output validated against JSON schema before storage and delivery.

### Phase 2 Agents (Planned — Months 4–9)
Customer Segmentation, Pricing Intelligence, Search & Merchandising, Meeting Intelligence, Category Growth, Supplier Intelligence, Demand Forecasting, Promo Simulator, Knowledge Retrieval, Influencer & Partnership (11 additional agents total).

### Phase 3 Agents (Vision — Months 10–18)
Company-wide expansion covering Commercial, Finance, Logistics, HR, and Customer Support domains; Anomaly Detection Agent (near-real-time GMV and conversion monitoring); Attribution / MMM Agent (true incremental revenue measurement per channel).

### The Portal
Next.js application at `ai.ananas.mk`, secured by Microsoft Entra ID SSO. Every module reads precomputed agent outputs from the database — the portal never triggers live AI calls on page load. Includes an AI Chat feature (live) backed by a dynamic system prompt rebuilt on every request with the latest outputs from all five agents.

**Phase 1 portal modules:** Dashboard (live agent outputs)
**Phase 2 portal modules:** Full suite across all agent domains (planned)

### Phase 1 Integrations (read-only)
GA4, Google Ads, Google Shopping, Meta Ads, TikTok Ads, LinkedIn Ads, Trustpilot API, Google Business Profile, Microsoft Teams (Graph API — 6 channels), Outlook (Graph API — email to Denis), CRM/email platform (to be confirmed with team)

### Phase 1 Roadmap (Months 1–3)
| Batch | Status | Scope |
|---|---|---|
| 1 — Foundation | ✅ COMPLETE | GitHub repo, config files, 16 agent definitions, SQL schema, GA4 live integration tested |
| 2 — AWS Infrastructure | Planned | EC2, Security Groups, Route 53, CloudFront, S3, Secrets Manager, CloudWatch; Hetzner parallel |
| 3 — Database & Runtime | Planned | PostgreSQL schema applied, Python runtime, CLI commands, Secrets loaded, nightly backup |
| 4 — Integrations | Planned | GA4 service account, all ad platform connectors, Trustpilot, Teams, Outlook, CRM |
| 5 — Agents Live | Planned | Dry-run → live data; schema validation enforced; Teams + email live; full morning run tested |
| 6 — KPI Dashboard | Planned | Static portal view at ai.ananas.mk/dashboard; graceful degradation on agent failure |
| 7 — Stabilisation | Planned | Token caps tested, backup restore tested, health monitoring confirmed, architecture updated |

**Immediate priorities (next 30 days):**
- Complete all pending integrations and access items (see Pending Actions below)
- Full morning run tested end-to-end on live data
- Denis + marketing team actively using daily brief

**Phase 1 parallel-track (Day 1 marketing quick wins — no platform dependency):**
- Claim and respond to all existing Trustpilot reviews
- Audit email platform — map existing lifecycle flows and gaps
- Establish campaign post-launch analysis discipline
- Begin Jira / Confluence onboarding for marketing team
- Map coupon usage — separate marketing spend from coupon cost in reporting

### Phase 2 Roadmap (Months 4–9)

**Q2 2026 (Months 4–6):**
- `ai.ananas.mk` live with SSL certificate and production domain
- Full team using the portal daily — all 8 marketing team members + Denis
- Customer Segmentation Agent live — RFM segments, churn risk scoring
- Pricing Intelligence Agent live — competitor price monitoring
- Search & Merchandising Agent live — zero-result rate, catalog gap detection
- Meeting Intelligence Agent live — transcripts to Jira tasks
- PostgreSQL migration completed (from SQLite)
- AWS Secrets Manager live — all credentials migrated

**Q3 2026 (Months 7–9):**
- Category Growth Agent live — marketplace revenue and margin ranking
- Supplier Intelligence Agent live — co-marketing opportunity scoring
- Demand Forecasting Agent live — seasonal demand spike detection
- Promo Simulator Agent live — pre-launch discount impact estimation
- Knowledge Retrieval Agent live — Confluence + campaign archive search
- Influencer & Partnership Agent live — creator ROI tracking
- All portal Phase 2 modules live and accessible
- Teams bot v1 live — promo simulation and knowledge retrieval via chat

### Phase 3 Roadmap (Months 10–18)
- Company-wide expansion: Commercial, Finance, CX, Logistics, HR modules
- Anomaly Detection Agent — near-real-time GMV and conversion monitoring
- Attribution / MMM Agent — true incremental revenue measurement per channel
- Multilingual outputs — Macedonian language for all briefs and portal content
- Creative automation layer — AI-generated ad copy and brief drafts
- Self-learning content memory — platform learns from its own history
- Firebase / Adjust app analytics (post MK app launch)
- Phase 1 MK is the proof-of-concept for rollout across all Delta Holding markets

### Pending Actions & Dependencies
Several items are blocking full Phase 1 completion. They require action from IT, Azure administration, or platform account owners. (Detail to be populated from pending actions appendix — flagged as open items requiring follow-up with Denis / IT team.)

### Governance & Reliability
- Every agent output validated against JSON schema before database write; failures logged and trigger Teams alert
- `run_type` field missing/invalid is always a hard failure — nothing written or posted
- Sample-mode outputs labelled `[SAMPLE DATA]` in all Teams messages
- Switching any agent from sample mode to live requires a manual confirmation step — never automated
- All credentials in environment files with restricted permissions on EC2 host; Phase 2 migrates to AWS Secrets Manager
- No credentials stored in GitHub repository or portal frontend code
- Daily SQLite dumps on EC2 host (Phase 1); automated S3 backup added in Phase 2
- Portal shows last successful agent output with timestamp if fresh run fails
- All architectural decisions documented as ADRs in `docs/decisions/`; significant changes require updates to architecture document, `agents.json`, and `CHANGELOG`

### Budget Summary
| Category | Phase 1 (monthly) | Phase 2 (monthly, projected) |
|---|---|---|
| Infrastructure (cloud/storage) | Low (single EC2 t3.xlarge + S3) | Scaled with team growth |
| AI model costs (Anthropic/OpenAI APIs) | Controlled via token caps | Increases with agent count |
| Build investment | Development time (Zharko) | Expanded team contribution |
- Total 18-month investment budget: to be populated (figures not extracted from source tables)
- Cost per actionable insight: estimated under €0.50

### Success Criteria
| Month | Focus | Gate |
|---|---|---|
| 1 | Platform live and reliable | Agent uptime ≥95% |
| 2 | Data quality and team adoption | Denis + ≥3 team members find brief useful |
| 3 | Intelligence quality | ≥1 revenue/margin action directly attributed to a platform alert |

Phase 2 begins only when all three Month 1–3 criteria are met for 4+ consecutive weeks.

### Strategic Milestones
- Phase 1 complete and full team adopted: Month 3
- All 16 agents live, full portal deployed: Month 9
- Company-wide platform, MMM live, Delta Holding rollout begun: Month 18

### Operator
- **Zharko** — sole Phase 1 operator; platform designed to be maintained by one person

---

> ⚠️ **Security notice (internal):** A Google Cloud service account private key (`ananas-ai@boreal-coyote-490215-p5.iam.gserviceaccount.com`, key ID `24cf331ae1cc...`) was found in raw source materials. This credential should be treated as **potentially compromised** and rotated immediately via Google Cloud Console. Do not store or distribute the raw JSON file.

---

*This document is maintained by Claude Code. To update it, drop new source materials into `context/ananas/raw/` and say "new files in raw".*
```
