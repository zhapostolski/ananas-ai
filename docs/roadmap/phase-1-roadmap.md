# Phase 1 Roadmap — v2
**Last updated:** 2026-03-14
**Horizon:** Months 1–3 (first 90 days as Head of Marketing)

## Outcome
A working marketing-first AI intelligence layer that:
- runs five specialist agents every morning (06:00–07:30 MKD)
- posts structured summaries to six Microsoft Teams channels
- sends an executive brief to Denis by 07:35
- stores all outputs, logs, metrics, and health state in PostgreSQL
- is deployed on AWS EC2 (or Hetzner fast-lane if AWS approvals are slow)
- is fully operable by one person (Zharko) with Claude Code as the build accelerator

## Batch 1 — Foundation ✅ COMPLETE
- GitHub repo created: `github.com/zhapostolski/ananas-ai`
- CLAUDE.md and `.claude/` project structure in place
- Config files: agents.json, metrics.json, model-routing.json, integrations-matrix.json, schedules.json
- 16 agent definitions in `.claude/agents/` (5 Phase 1 + 11 Phase 2)
- Architecture docs, ADRs, CHANGELOG, naming standard
- SQL schema defined (6 tables)
- GA4 live integration tested — real data confirmed

## Batch 2 — AWS infrastructure
- Provision EC2 t3.xlarge in eu-central-1 (or eu-south-1 nearest MKD)
- Attach 200 GB gp3 EBS volume
- Configure Security Groups (SSH from fixed IP only, HTTPS from CloudFront)
- Set up Route 53 → CloudFront → EC2 for ai.ananas.mk
- Provision S3 bucket for backups (versioning + encryption enabled)
- Configure Secrets Manager (GA4 service account, API keys, DB credentials)
- Set up CloudWatch basic alarms (CPU, memory, agent failure)
- Hetzner CPX41 provisioned in parallel as fast-lane backup

## Batch 3 — Database and runtime baseline
- PostgreSQL installed and running on EC2
- Schema applied: `sql/schema.sql` (agent_outputs, agent_logs, metrics_history, system_health, delivery_log, bot_interactions)
- Python runtime installed, `.venv` activated
- `cli.py` commands working: doctor, bootstrap-db, check-integrations, run-agent, run-brief, list-latest
- Secrets loaded from AWS Secrets Manager (not .env in production)
- Nightly DB dump to S3 running
- Daily EBS snapshot configured

## Batch 4 — Integrations
- GA4: already LIVE — move from ADC to service account for production
- Google Ads + Google Shopping: MCP connector configured and tested
- Meta Ads: MCP connector configured and tested
- TikTok / LinkedIn: MCP connectors configured
- Google Search Console: service account + connector tested
- Trustpilot API: api-key configured, first pull tested
- Google Business Profile: connector tested
- CRM/email platform: confirmed with team, connector tested
- Microsoft Teams posting: Graph API, six channels configured and posting
- Outlook email: Graph API, Denis email sending tested

## Batch 5 — Agents live
- All five agents running in dry-run mode (mock data, real logic)
- Agents switched to live data one by one, validated against known baseline
- Output schema validation enforced before every DB write
- Teams posting live for all six channels
- Executive email to Denis live
- Full morning run (06:00–07:30) tested end-to-end
- Token caps and cost logging confirmed in agent_logs

## Batch 6 — KPI dashboard (Claude Code)
- KPI dashboard module built (portal-ready)
- Sources: agent_outputs table (precomputed)
- Displays: Performance, CRM, Reputation, Ops, Cross-Channel summary
- Graceful degradation: last-known-good + status banner if agent failed
- Deployed at ai.ananas.mk/dashboard (basic auth or Entra ID lite)

## Batch 7 — Stabilization and handover
- Token caps tested and confirmed
- Restore from backup tested (not assumed from job completion)
- Health monitoring confirmed — CloudWatch + system_health table
- CHANGELOG updated
- Weekly architecture review template used for first review
- Architecture pack updated and ready for Phase 2 planning

## Days 1–30 non-platform priorities (parallel track)
These run alongside the platform build — they are the Day 1 marketing quick wins:
1. Claim and optimize Trustpilot profile — start responding to reviews
2. Launch Google Shopping campaigns — first 1,000 products minimum
3. Audit email platform — identify what lifecycle flows exist, what is missing
4. Set up campaign post-launch analysis discipline with the team
5. Begin Jira/Confluence onboarding for the marketing team
6. Map coupon usage — separate marketing spend from coupon cost in reporting
