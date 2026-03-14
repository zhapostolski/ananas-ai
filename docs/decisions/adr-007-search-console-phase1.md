# ADR-007 — Google Search Console Moved to Phase 1

## Status
Accepted — 2026-03-14

## Context
Google Search Console was originally planned for Phase 2. After full audit review, this was reconsidered.

Ananas has 250,000+ products. Without Search Console data, the platform cannot track:
- how many products are indexed in Google
- which pages are getting organic clicks
- what keywords are driving traffic
- whether the SEO agency's deliverables are producing results

This is not a "nice to have" Phase 2 feature. It is basic SEO visibility and directly relevant to the catalog indexation problem identified in the Day 1 audit.

## Decision
Move Google Search Console MCP connector to Phase 1. It will be configured alongside GA4 in Batch 4 of the Phase 1 roadmap.

The Organic & Merchandising Agent remains Phase 2 — but Search Console data will be available to the Marketing Ops Agent in Phase 1 for basic indexation and click monitoring.

## Consequences
- One additional service account credential required in Secrets Manager
- Search Console read-only connector added to Phase 1 integrations-matrix.json
- `indexed_pages_vs_catalog` metric moved from Phase 2 to Phase 1 (partial)
- No additional agent run cost in Phase 1 — data consumed by existing Marketing Ops Agent
