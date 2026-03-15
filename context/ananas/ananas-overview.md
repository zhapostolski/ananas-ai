```markdown
# Ananas — Company Overview
<!-- Living document. Updated incrementally as source materials are added to context/ananas/raw/. -->
<!-- Last updated: 2026-03-13 | Sources processed: 5 -->

---

## 1. Company Profile

- **Full name:** Ananas
- **Founded:** 2021
- **Headquarters:** Serbia (Balkans region)
- **Website:** ananas.rs
- **Market(s) served:** Serbia (primary); regional Balkan expansion planned
- **Business type:** E-commerce marketplace (hybrid — own inventory + third-party sellers)
- **Company size:** ~150–200 employees (est. from org structure)
- **Ownership / structure:** Private; backed by regional investors

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
- **Coupon / discount dependency:** High — coupon-driven sales mask real acquisition efficiency (known issue)
- **GMV vs. net revenue split:** To be populated
- **Contribution margin structure:** To be populated

---

## 4. Key Metrics & KPIs

### Known (from GA4 live data — 2026-03-13)
| Metric | Value |
|---|---|
| Sessions | 464,000 |
| Users | 215,000 |
| Revenue | €13.4M |

### Targets & Benchmarks (from whiteboard — 2026-03-13)
Whiteboard photograph shows a traffic funnel with current state and apparent targets (right-hand column). Figures interpreted as targets or benchmark comparisons:

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
| — | 3,275 | — |
| — | 10,316M | — |
| — | 24,337M | — |
| — | 1.9 | — |
| — | 42,000 | — |
| — | 27,830 | — |

> ⚠️ *Whiteboard figures are partially legible. Numbers in the right-hand column may represent targets, a second market/channel breakdown, or a comparison period. Interpretation should be confirmed with the team. AOV of ~50 (currency assumed RSD thousands or EUR — to clarify).*

**Key funnel ratios visible on whiteboard:**
- Sessions → Page Views → Product Pages → CVR 1% → ~22,000 orders
- AOV ~50 → GMV ~1.1M (monthly)
- App noted separately with figure ~50 (AOV or share)

---

## 5. Marketing Channels & Stack

### Active Channels
| Channel | Status | Notes |
|---|---|---|
| Google Ads | Active | Managed by performance team |
| Google Shopping | **CRITICAL GAP** | 250k products, 0 campaigns |
| Meta Ads | Active | |
| TikTok Ads | Active | |
| LinkedIn Ads | Active | |
| X (Twitter) Ads | Pending | Account creation pending |
| Email / CRM | Active | Platform TBD (HubSpot / ActiveCampaign / Klaviyo) |
| SEO / Organic | Active | Managed via Search Console + Ahrefs/Semrush; SEO traffic target noted on whiteboard |
| Influencer / Creator | Active | Used for product launches and seasonal campaigns |
| Push Notifications | Active | Web and app push |
| Affiliate | Active | Regional affiliate network |

### Channel Mix Notes (from whiteboard left margin — partially legible)
- References to: Google ~4%, Meta ~50%, something ~29%, other channels including email (~5%), direct (~10%), other (~-)
- *Note: figures are partially illegible; to be confirmed with performance team*

### Internal Tools
- Jira, Asana, Confluence, Teams, SharePoint, Outlook, Berry (HR)

### Analytics
- **GA4:** LIVE and integrated
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
  - **Denis** — Country Manager, recipient of daily AI brief; leads regional expansion agenda
  - **CMO / Marketing Director** — oversees full marketing function
  - **Head of Performance** — owns paid media channels
  - **Head of Product / Tech** — owns platform, app, and data infrastructure

---

## 7. Customers & Market

- **Target customer profile:** Broad mass-market; primary demographic 25–45, urban, digitally native; secondary 18–24 (TikTok-driven)
- **Primary geographies:** Serbia (core); Bosnia & Herzegovina, Croatia, North Macedonia (expansion targets)
- **Customer acquisition channels:** Performance (Google, Meta, TikTok), organic search, email, direct/app
- **Retention profile:** Repeat purchase driven by promotions and coupons; lifecycle automation gap limits organic retention
- **NPS / satisfaction:** Low — reflected in Trustpilot 2.0 rating; customer service responsiveness flagged as key driver

---

## 8. Reputation & Trust

- **Trustpilot rating:** 2.0 stars — **CRITICAL**
  - Profile not yet claimed
  - Currently 100% negative reviews visible
  - No response strategy in place yet
- **Google Business Profile:** Active (rating TBD)
- **Key reputation drivers (negative):** Delivery delays, customer service responsiveness, return process friction
- **Planned remediation:** Claim Trustpilot profile; implement review response program; address root-cause service issues

---

## 9. Technology & Infrastructure

- **E-commerce platform:** Proprietary platform (custom-built)
- **Mobile:** iOS and Android apps (live)
- **Backend stack:** Microservices architecture; cloud-hosted (AWS)
- **Frontend stack:** React-based web storefront
- **AI platform:** Ananas AI — AWS EC2, Claude Sonnet/Opus, GPT-4o-mini router; GCP service account (`ananas-ai@boreal-coyote-490215-p5.iam.gserviceaccount.com`) used for Google API integrations (GA4, Search Console, etc.)
- **Data / Analytics:** GA4, internal Orders / Returns / Margin APIs
- **Automation:** No lifecycle email automations currently live (gap)
- **Seller portal:** Self-service onboarding and listing management for marketplace sellers

---

## 10. Current Challenges & Priorities

1. **Trustpilot 2.0 rating** — profile unclaimed, no response program — reputational risk
2. **Google Shopping gap** — 250k products with zero campaigns — major revenue opportunity
3. **Coupon dependency** — marketing-budget coupons driving most sales — masks real efficiency
4. **No email lifecycle automations** — cart recovery, churn flows, welcome series not live
5. **CRM platform TBD** — email platform not yet confirmed
6. **X Ads account** — not yet created
7. **Regional expansion** — Serbia is core market; Balkan expansion (BA, HR, MK) in planning — requires localisation of ops, marketing, and legal
8. **Seller growth** — increasing marketplace seller count and GMV share is a strategic priority
9. **App engagement** — push notification and in-app personalisation underutilised
10. **Traffic scale gap** — whiteboard indicates current users ~600k with a 3× growth target; CVR at 1% and GMV ~1.1M/month suggest significant headroom to improve both traffic and conversion

---

## 11. Brand Voice & Guidelines

- **Brand personality:** Approachable, energetic, locally rooted but modern; positioned as "the Balkan Amazon" with a friendly, helpful tone
- **Tone of voice:** Warm, direct, conversational; avoids corporate stiffness; humorous where appropriate in social/TikTok contexts
- **Visual identity:** Bold colour palette (orange primary); clean product-forward layouts; strong use of promotional/price-led creative
- **Do's and don'ts:**
  - ✅ Highlight value, deals, and convenience
  - ✅ Use local language and cultural references
  - ✅ Be responsive and human in customer comms
  - ❌ Avoid overly formal or distant language
  - ❌ Do not make delivery/service promises that operations cannot fulfil (key reputational risk)

---

## 12. Competitive Landscape

- **Direct competitors:** Kupujemprodajem (C2C/marketplace), eKupi (HR), Shoppster, Mall.rs, and international players (eMag, AliExpress)
- **Market position:** Challenger/growth player in Serbia; aspires to be #1 regional e-commerce platform
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

---

> ⚠️ **Security notice (internal):** A Google Cloud service account private key (`ananas-ai@boreal-coyote-490215-p5.iam.gserviceaccount.com`, key ID `24cf331ae1cc...`) was found in raw source materials. This credential should be treated as **potentially compromised** and rotated immediately via Google Cloud Console. Do not store or distribute the raw JSON file.

---

*This document is maintained by Claude Code. To update it, drop new source materials into `context/ananas/raw/` and say "new files in raw".*
```
