# Week 1 Action Plan — Head of Marketing @ Ananas.mk

**Purpose:** What to do in the first 5 working days, in parallel with platform build.
These are the highest-impact actions that don't require platform infrastructure.

---

## Day 1 (Monday)

### Marketing team
- [ ] Meet each team member 1:1 (30 min each) — understand current workload, tool access, ownership
- [ ] Map who owns what: performance campaigns, email, social, content, SEO agency liaison
- [ ] Request Jira, Confluence, Teams, SharePoint access for all team members
- [ ] Check which lifecycle email flows are currently active in CRM platform
- [ ] Confirm CRM platform name (HubSpot / ActiveCampaign / Klaviyo / other)

### Trustpilot — DO THIS DAY 1
- [ ] Go to business.trustpilot.com and claim Ananas.mk profile
- [ ] Verify ownership (DNS or email)
- [ ] Write first response to oldest unresponded negative review
- [ ] Set daily reminder to respond to new reviews within 24h
- **Why day 1:** Every day without responses compounds the trust damage

### Google Ads
- [ ] Get access to Google Ads account
- [ ] Confirm Shopping feed exists and which products are in it
- [ ] If no Shopping feed: flag as Week 1 priority — create feed for top 1,000 products minimum

---

## Day 2 (Tuesday)

### GA4 and analytics
- [ ] Get GA4 access
- [ ] Confirm GA4 property ID (expected: 374249510)
- [ ] Pull last 30 days baseline: sessions, users, conversions, revenue by channel
- [ ] Check event tracking: are all key events firing? (purchase, add_to_cart, begin_checkout)
- [ ] Identify any tracking gaps → add to Marketing Ops Agent alert list

### Email/CRM audit
- [ ] List all active email flows (automation sequences)
- [ ] Note what is NOT active: cart abandonment, win-back, post-purchase, onboarding
- [ ] Pull last month email performance: open rate, click rate, revenue
- [ ] Confirm unsubscribe rate and list health

---

## Day 3 (Wednesday)

### Coupon audit
- [ ] Pull report: what % of orders in last 30 days used a coupon?
- [ ] Separate coupon cost from media spend in reporting
- [ ] Understand who issues coupons: marketing only, or also operations/commercial?
- [ ] Flag if coupon dependency ratio > 30% — this is the Marketing Ops Agent's #1 alert

### Campaign post-analysis
- [ ] Pull list of all active and recent campaigns (last 60 days)
- [ ] Check which campaigns have a post-launch analysis document
- [ ] Set a team standard: every campaign gets a results brief within 7 days of end
- [ ] Create a Confluence template for campaign post-mortems

---

## Day 4 (Thursday)

### Google Shopping
- [ ] If no Shopping campaigns exist: create first campaign with top 100 products
- [ ] Set daily budget and target ROAS (start conservative)
- [ ] Submit shopping feed to Google Merchant Center if not done
- [ ] Note: Google Shopping Impression Share will become a daily metric in the platform

### Platform build
- [ ] Begin AWS provisioning (EC2, S3, Secrets Manager, Route 53)
- [ ] OR provision Hetzner CPX41 if AWS is delayed
- [ ] Install PostgreSQL, apply schema
- [ ] Confirm GA4 service account and move from ADC to service account

---

## Day 5 (Friday)

### Weekly review baseline
- [ ] Prepare first marketing team weekly review
- [ ] Pull numbers manually (before platform is live) for: spend, ROAS, sessions, conversions, revenue
- [ ] Present to Denis: what you found, what you're fixing, platform timeline
- [ ] Set recurring weekly marketing review meeting (Fridays 09:00 or as agreed)

### Platform
- [ ] Teams posting connector tested
- [ ] Executive email to Denis tested (send a test)
- [ ] Performance Agent run-agent dry-run tested with mock data

---

## Platform go-live target: End of Week 3

| Week | Milestone |
|---|---|
| Week 1 | Team audit, Trustpilot claimed, Shopping first campaign, AWS provisioned |
| Week 2 | All integrations connected and tested, agents running in dry-run |
| Week 3 | Agents live with real data, Teams posting live, Denis brief live |
| Week 4 | First full operating week — monitor, fix, stabilize |
