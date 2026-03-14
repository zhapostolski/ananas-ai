# Integrations Guide — Phase 1

## GA4 — LIVE ✅

**Auth:** Application Default Credentials (local dev) → Service Account (production)
**Property ID:** 374249510
**Scope:** `https://www.googleapis.com/auth/analytics.readonly`
**API:** Google Analytics Data API v1beta

**Production setup:**
1. Create service account in Google Cloud project `ananas-ai-ga4-test`
2. Grant service account access to GA4 property 374249510
3. Download service account JSON
4. Store in Secrets Manager: `ananas-ai/ga4-service-account`
5. Set env var: `GOOGLE_APPLICATION_CREDENTIALS` → fetched from Secrets Manager at runtime

**Verified output (2026-03-13):**
- Sessions: 464,844
- Users: 215,232
- Conversions: 2,925
- Revenue: €13,362,847

---

## Google Ads + Google Shopping

**Auth:** Service account with Google Ads API access
**Scope:** Google Ads API read-only
**Key Shopping metric:** Impression Share — currently 0% (no campaigns)

**Setup steps:**
1. Enable Google Ads API in Google Cloud project
2. Create OAuth2 client or service account
3. Link to Ananas Google Ads account (MCC or direct)
4. Store in Secrets Manager: `ananas-ai/google-ads-credentials`
5. Test: pull last 7 days spend + impression share

---

## Trustpilot API — CRITICAL ⚠️

**Current status:** 2.0 stars, profile unclaimed, 100% negative reviews
**API base:** `https://api.trustpilot.com/v1`
**Auth:** API key (Business account required)

**Setup steps:**
1. Claim Ananas.mk profile at business.trustpilot.com — DO THIS WEEK
2. Register for Trustpilot Business API
3. Generate API key
4. Store in Secrets Manager: `ananas-ai/trustpilot-api-key`
5. Test endpoints:
   - `GET /v1/business-units/{businessUnitId}/reviews` — review pull
   - `GET /v1/business-units/{businessUnitId}` — profile + score

**Key metrics to pull:**
- `trustScore` (current rating)
- `numberOfReviews.total`
- Reviews pending response (filter: `replied=false`)
- Average response time

---

## Google Search Console

**Auth:** Service account (same Google Cloud project as GA4)
**Scope:** `https://www.googleapis.com/auth/webmasters.readonly`
**Property:** `sc-domain:ananas.mk`

**Setup steps:**
1. Add service account as verified owner or restricted user in Search Console
2. Store credentials in Secrets Manager: `ananas-ai/search-console-credentials`
3. Test: pull top 10 queries by clicks for last 28 days

**Key metrics:**
- Total clicks (organic)
- Total indexed pages
- Top queries by impressions
- Pages with clicks but zero indexed status (crawl issues)

---

## Microsoft Teams Posting

**Auth:** Microsoft Graph API — app registration in Azure AD (Entra ID)
**Scopes needed:** `ChannelMessage.Send`, `Group.Read.All`
**Method:** Bot Framework or Graph API direct post

**Setup steps:**
1. Register app in Azure AD (Entra ID)
2. Grant admin consent for Graph API scopes
3. Store in Secrets Manager: `ananas-ai/teams-app-credentials`
4. Create six channels (if not existing): see schedules.json for channel list
5. Test: post test message to #marketing-ops

---

## Outlook Email (Denis brief)

**Auth:** Microsoft Graph API — same app registration as Teams
**Scopes needed:** `Mail.Send`
**Recipient:** denis@ananas.mk

**Setup steps:**
1. Add `Mail.Send` scope to existing Entra ID app registration
2. Test: send test email to Denis before go-live
3. Subject format: `Ananas Marketing Intelligence — {YYYY-MM-DD}`

---

## CRM / Email Platform

**Status:** Platform to be confirmed with team (HubSpot / ActiveCampaign / Klaviyo / other)
**Auth:** API key
**Key data needed:**
- Cart abandonment rate
- Cart recovery rate + revenue recovered
- Email open rate, click rate, revenue per send
- Active subscribers (opened/clicked in last 90 days)
- Unsubscribe rate

**Setup steps:**
1. Confirm platform with team in Week 1
2. Generate read-only API key
3. Store in Secrets Manager: `ananas-ai/crm-api-key`
4. Map platform-specific field names to canonical metrics in config/integrations-matrix.json

---

## Secrets Manager — full key list (Phase 1)

| Secret name | Contents |
|---|---|
| `ananas-ai/ga4-service-account` | Google service account JSON |
| `ananas-ai/google-ads-credentials` | Google Ads OAuth2/service account |
| `ananas-ai/search-console-credentials` | Search Console service account |
| `ananas-ai/trustpilot-api-key` | Trustpilot Business API key |
| `ananas-ai/teams-app-credentials` | Entra ID app client ID + secret |
| `ananas-ai/crm-api-key` | CRM/email platform API key |
| `ananas-ai/openai-api-key` | OpenAI API key (GPT-4o-mini router) |
| `ananas-ai/anthropic-api-key` | Anthropic API key (Sonnet + Opus) |
| `ananas-ai/db-credentials` | PostgreSQL user + password |
