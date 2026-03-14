# Access Requirements

This document lists every credential and access permission the Ananas AI Platform requires, how to obtain it, and where to store it.

> **Storage rule:** All secrets go into AWS Secrets Manager on EC2. For local development, copy them into your `.env` file (never commit `.env`).

---

## Quick-start: minimum viable credentials

To run the platform locally with sample data only:
```
ANTHROPIC_API_KEY=sk-ant-...     # Claude API (required)
OPENAI_API_KEY=sk-proj-...       # OpenAI fallback + Whisper (required)
```

Everything else enables live data. Agents fall back to sample data if a source's credentials are missing.

---

## AI Model APIs

### Anthropic (Claude)
- **Env var:** `ANTHROPIC_API_KEY`
- **Used by:** all 5 agents (default execution model), transcribe-meeting
- **How to get:** console.anthropic.com → API Keys → Create Key
- **Permissions needed:** Messages API access (standard)
- **Cost:** ~$0.02–0.05/day for Phase 1 (Sonnet default, Opus for brief only)

### OpenAI
- **Env var:** `OPENAI_API_KEY`
- **Used by:** fallback when Claude is unavailable, `ananas-ai-transcribe` (gpt-4o-transcribe)
- **How to get:** platform.openai.com → API Keys → Create
- **Permissions needed:** Chat Completions + Audio Transcriptions

---

## Google

### Google Analytics 4 (GA4)
- **Env vars:** `GA4_PROPERTY_ID`, `GA4_CREDENTIALS` (path to service account JSON)
- **Used by:** performance-agent
- **Status:** LIVE and tested (2026-03-13)
- **How to get:**
  1. Google Cloud Console → IAM & Admin → Service Accounts → Create
  2. Grant role: **Viewer** on the GA4 project
  3. Create JSON key → download → store path in `GA4_CREDENTIALS`
  4. GA4 Admin → Property → Property Access Management → Add user (service account email) with **Viewer** role
  5. Copy Property ID (numeric) → `GA4_PROPERTY_ID`

### Google Search Console
- **Env vars:** `SEARCH_CONSOLE_SITE_URL`, `GA4_CREDENTIALS` (same service account as GA4)
- **Used by:** organic-merchandising-agent (Phase 2)
- **How to get:**
  1. Reuse the same service account from GA4
  2. Search Console → Settings → Users and permissions → Add user (service account email) → Full
  3. Set `SEARCH_CONSOLE_SITE_URL=https://ananas.mk/` (include trailing slash)

### Google Ads
- **Env vars:** `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_REFRESH_TOKEN`, `GOOGLE_ADS_CUSTOMER_ID`
- **Used by:** performance-agent
- **How to get:**
  1. Apply for a Google Ads Developer Token at developers.google.com/google-ads (Manager account required)
  2. Google Cloud Console → OAuth 2.0 Client ID (type: Desktop or Web) → get `CLIENT_ID` and `CLIENT_SECRET`
  3. Run OAuth flow to get `REFRESH_TOKEN` (use `google-auth-oauthlib` or Postman)
  4. `GOOGLE_ADS_CUSTOMER_ID` = the 10-digit account ID (no dashes)

---

## Meta (Facebook / Instagram)

### Meta Ads
- **Env vars:** `META_ACCESS_TOKEN`, `META_AD_ACCOUNT_ID`
- **Used by:** performance-agent
- **How to get:**
  1. developers.facebook.com → My Apps → Create App (type: Business)
  2. Add Marketing API product
  3. Generate a **System User** token (Business Manager → System Users) with `ads_read` permission
  4. `META_AD_ACCOUNT_ID` = `act_XXXXXXXXXX` (found in Ads Manager URL)

---

## Microsoft (Teams + Outlook)

### Teams Webhook
- **Env var:** `TEAMS_WEBHOOK_URL`
- **Used by:** all agents (output posting)
- **How to get:**
  1. Open the target Teams channel (e.g. `#marketing-performance`)
  2. Channel settings → Connectors → Incoming Webhook → Configure
  3. Name it "Ananas AI" → copy the webhook URL
  4. Repeat for each output channel: `#marketing-performance`, `#marketing-crm`, `#marketing-reputation`, `#marketing-ops`, `#marketing-summary`, `#executive-summary`
  5. Store individual webhook URLs in `config/output-channels.json` — or set one default in `TEAMS_WEBHOOK_URL`

### Outlook Email (Denis summary)
- **Env vars:** `OUTLOOK_FROM_ADDRESS`, `OUTLOOK_TO_ADDRESS` (and optionally `MS_GRAPH_CLIENT_ID`, `MS_GRAPH_CLIENT_SECRET`, `MS_GRAPH_TENANT_ID`)
- **Used by:** cross-channel-brief-agent (email Denis)
- **How to get:**
  1. Azure Portal → App Registrations → New → grant `Mail.Send` permission
  2. Add client secret → store `MS_GRAPH_CLIENT_ID`, `MS_GRAPH_CLIENT_SECRET`, `MS_GRAPH_TENANT_ID`
  3. Set sender and recipient addresses

---

## Trustpilot

### Trustpilot API
- **Env vars:** `TRUSTPILOT_API_KEY`, `TRUSTPILOT_BUSINESS_UNIT_ID`
- **Used by:** reputation-agent
- **Status:** Profile not yet claimed — CRITICAL (2.0 rating, no management access)
- **How to get:**
  1. Claim the Ananas profile at support.trustpilot.com (requires business email)
  2. Once claimed: Business Portal → Integrations → API → Create API key
  3. `TRUSTPILOT_BUSINESS_UNIT_ID` = ID from your profile URL (`trustpilot.com/review/ananas.mk`) — get from API or portal

---

## Sales Snap (CRM / Email)

### Sales Snap API
- **Env vars:** `SALES_SNAP_API_KEY`, `SALES_SNAP_BASE_URL`
- **Used by:** crm-lifecycle-agent
- **Default base URL:** `https://app.sales-snap.com/api/v1`
- **How to get:**
  1. Sales Snap admin panel → Settings → API Access → Generate key
  2. Key needs read access to: contacts, campaigns, orders, segments

---

## Pinterest Ads

### Pinterest API
- **Env vars:** `PINTEREST_ACCESS_TOKEN`, `PINTEREST_AD_ACCOUNT_ID`
- **Used by:** performance-agent
- **How to get:**
  1. developers.pinterest.com → My Apps → Create → type: Web
  2. Request `ads:read` scope
  3. Generate access token via OAuth
  4. `PINTEREST_AD_ACCOUNT_ID` = numeric ID from Pinterest Ads Manager URL

---

## AWS Infrastructure

### EC2 / Runtime Host
- **Access:** SSH key or AWS Systems Manager Session Manager (preferred — no open ports)
- **IAM role attached to EC2 instance** (no env vars needed on EC2 if using instance role):
  - `secretsmanager:GetSecretValue` on `arn:aws:secretsmanager:eu-central-1:*:secret:ananas-ai/*`
  - `s3:PutObject` on the backup bucket
  - `logs:CreateLogGroup`, `logs:PutLogEvents` on CloudWatch

### AWS Secrets Manager
All production credentials are stored as individual secrets under `ananas-ai/`:
```
ananas-ai/anthropic-api-key
ananas-ai/openai-api-key
ananas-ai/google-ads-credentials
ananas-ai/meta-ads-credentials
ananas-ai/trustpilot-api-key
ananas-ai/sales-snap-api-key
ananas-ai/teams-webhook-url
```

---

## Local development `.env` template

```bash
# ── AI Models ───────────────────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...

# ── Google ──────────────────────────────────────────────────
GA4_PROPERTY_ID=123456789
GA4_CREDENTIALS=/path/to/service-account.json
SEARCH_CONSOLE_SITE_URL=https://ananas.mk/
GOOGLE_ADS_DEVELOPER_TOKEN=
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=
GOOGLE_ADS_REFRESH_TOKEN=
GOOGLE_ADS_CUSTOMER_ID=

# ── Meta ────────────────────────────────────────────────────
META_ACCESS_TOKEN=
META_AD_ACCOUNT_ID=act_

# ── Pinterest ───────────────────────────────────────────────
PINTEREST_ACCESS_TOKEN=
PINTEREST_AD_ACCOUNT_ID=

# ── Microsoft ───────────────────────────────────────────────
TEAMS_WEBHOOK_URL=https://...webhook.office.com/...

# ── CRM ─────────────────────────────────────────────────────
SALES_SNAP_API_KEY=
SALES_SNAP_BASE_URL=https://app.sales-snap.com/api/v1

# ── Reputation ──────────────────────────────────────────────
TRUSTPILOT_API_KEY=
TRUSTPILOT_BUSINESS_UNIT_ID=

# ── Platform ────────────────────────────────────────────────
ANANAS_DB_PATH=                  # leave blank for default ./ananas_ai_dev.db
LOG_LEVEL=INFO
```

---

## Priority order for Phase 1

| Priority | Credential | Blocks |
|---|---|---|
| 1 | `ANTHROPIC_API_KEY` | Everything — agents won't run without it |
| 2 | `OPENAI_API_KEY` | Fallback + meeting transcription |
| 3 | `TEAMS_WEBHOOK_URL` | Output posting to Teams |
| 4 | `GA4_PROPERTY_ID` + `GA4_CREDENTIALS` | Performance agent live data |
| 5 | `SALES_SNAP_API_KEY` | CRM agent live data |
| 6 | `TRUSTPILOT_API_KEY` | Reputation agent live data (requires claiming profile first) |
| 7 | Google Ads credentials | Google Ads live data |
| 8 | `META_ACCESS_TOKEN` | Meta Ads live data |
