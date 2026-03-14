# Phase 2 Roadmap
**Last updated:** 2026-03-14
**Horizon:** Months 4–9

## Outcome
A full AI marketing intelligence portal at ai.ananas.mk with:
- 11 additional specialist agents (weekly + on-demand)
- Full portal with module-based views and Entra ID SSO
- Interactive Teams bot (retrieval, promo simulation, knowledge search)
- Broader live integrations (all paid channels, supplier API, app analytics)
- Meeting intelligence and institutional knowledge retrieval

## Priority ranking (business impact for Ananas specifically)
| Priority | Agent / Feature | Rationale |
|---|---|---|
| 1 | Portal application | Needed to present Phase 1 outputs properly to the team |
| 2 | Category Growth Agent | Most important marketplace intelligence layer |
| 3 | Supplier Intelligence Agent | Direct commercial revenue lever |
| 4 | Promo Simulator Agent | Pre-launch margin safety — high-frequency decision |
| 5 | Product Feed Agent | 250k catalog quality → Shopping scale |
| 6 | Demand Forecasting Agent | React before competitors |
| 7 | Organic & Merchandising Agent | Full SEO automation + feed monitoring |
| 8 | Meeting Intelligence | Meeting → Jira → Confluence automation |
| 9 | Knowledge Retrieval Agent | Institutional memory search |
| 10 | Influencer & Partnership Agent | Creator ROI tracking |
| 11 | Traditional Media Correlation | TV/OOH/Radio lift measurement |
| 12 | Employer Branding Agent | LinkedIn + talent pipeline |
| 13 | App Analytics | Pending MK app launch (Firebase/Adjust) |
| 14 | Social Publishing MCP | Hootsuite integration |

## Batch P2-1 — Portal foundation
- Next.js portal scaffolded from existing Ananas frontend stack
- Entra ID SSO integration (same as production apps)
- Next.js middleware: session validation, role checks, module access
- GraphQL / Read API connected to PostgreSQL
- Basic module pages: Performance, CRM, Reputation, Ops, Cross-Channel Brief
- Graceful degradation: last-known-good + status banner
- Deployed to ai.ananas.mk (Route 53 → CloudFront → EC2 or container)
- Built with Claude Code — engineering team review/fixes only

## Batch P2-2 — Category and supplier intelligence
- Category Growth Agent: live (Categories API + GA4 + Margin API + Returns API)
- Supplier Intelligence Agent: live (Supplier API + Orders API)
- Category-level metrics flowing to portal (portal module: Category Growth)
- Supplier marketing potential report: weekly, Teams #marketing-ops
- Commercial team briefed on findings weekly

## Batch P2-3 — Promo simulator and product feed
- Promo Simulator Agent: on-demand via portal and Teams bot
- Promo simulation results displayed in portal module
- Product Feed Agent: weekly scan of 250k catalog
- Feed health score and disapproval alerts flowing to #marketing-ops
- Content team workflow: product fix queue from agent output

## Batch P2-4 — Teams bot
- Teams bot service live (Microsoft Bot Framework)
- Commands: /brief, /promo-sim [category] [discount%], /search [query], /status
- Bot logs interactions to bot_interactions table
- Bot does NOT write to business systems — read and retrieve only
- Knowledge Retrieval Agent integrated with bot /search command

## Batch P2-5 — Demand forecasting and organic
- Demand Forecasting Agent: live (GA4 site search + Search Console + Categories API)
- Organic & Merchandising Agent: full activation (Ahrefs/Semrush MCP live)
- Demand spike alerts to #marketing-ops and #marketing-performance
- Seasonal calendar built from first 6 months of data

## Batch P2-6 — Meeting intelligence and knowledge base
- Meeting Intelligence Agent: audio intake folder live
- Whisper transcription → structured summary → Jira tasks automated
- Confluence integration: meeting summaries saved to marketing space
- Knowledge Retrieval Agent: Confluence + Jira + campaign archive search
- Portal knowledge module: searchable institutional memory

## Batch P2-7 — Remaining agents and stabilization
- Influencer & Partnership Agent: live
- Traditional Media Correlation Agent: live (requires campaign calendar sheet)
- Employer Branding Agent: live (LinkedIn)
- Full Phase 2 review and CHANGELOG update
- Phase 3 planning initiated with Denis and leadership

## Phase 2 integrations to activate
| Integration | Auth | Notes |
|---|---|---|
| All paid channel MCPs | Various | Most likely live from Phase 1 |
| Supplier API | Internal service account | Requires backend team to expose |
| Product Catalog API | Internal service account | Requires backend team to expose |
| Inventory API | Internal service account | Low priority — Phase 2 end |
| Firebase / Adjust | Service account | Pending MK app launch |
| Hootsuite / Buffer | OAuth2 | Requires Hootsuite account setup |
| Campaign Calendar Sheet | Google Sheets SA | Manual input from marketing team |
| Berry HR | TBD | Phase 2 end or Phase 3 |
