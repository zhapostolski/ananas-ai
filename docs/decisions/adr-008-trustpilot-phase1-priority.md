# ADR-008 — Trustpilot API as Phase 1 Critical Connector

## Status
Accepted — 2026-03-14

## Context
Trustpilot is currently at 2.0 stars on the Ananas.mk profile. The profile is not yet claimed. There are 100% negative reviews with no responses.

This is not a cosmetic problem. Trustpilot score directly affects:
- paid media conversion rates (users research before buying)
- CPA efficiency across all paid channels
- organic trust signals and brand perception

A dedicated Reputation Agent was already planned for Phase 1. Without the Trustpilot API connector, that agent has no live data source for its primary function.

## Decision
Trustpilot API (`api.trustpilot.com/v1`) is a Phase 1 critical connector.

Specific actions required before Batch 4:
1. Claim the Ananas.mk Trustpilot profile
2. Register for Trustpilot Business API access
3. Configure API key in Secrets Manager
4. Test connector: review pull, response rate, sentiment

## Consequences
- Trustpilot Business account required (free tier may be sufficient for read access)
- API key added to Secrets Manager
- Reputation Agent becomes fully functional with live Trustpilot data in Phase 1
- Response rate and sentiment metrics active from Day 1

## Priority note
This is the highest-reputational-risk item in the entire Phase 1 scope. It must be addressed in Week 1, not Week 8. Every day without claiming and responding costs trust.
