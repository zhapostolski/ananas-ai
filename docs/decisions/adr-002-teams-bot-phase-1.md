# ADR-002 Teams as Primary Output Channel in Phase 1

## Status
Accepted — Phase 1 delivery only (no bot listener yet)

## Context
The 8-person marketing team lives in Microsoft Teams. The platform must deliver daily briefs where the team already works, not require them to visit a separate portal. The portal (ai.ananas.mk) is planned for Phase 2 as the deep-analysis interface.

Two Teams integration modes were considered:
- **Webhook posting only**: platform pushes formatted cards to channels; no bot listener; zero Teams app registration required
- **Full Teams bot**: two-way interaction, slash commands, bot listener; requires Azure Bot Service registration and IT approval

Phase 1 constraint: IT access requests are pending and a full bot registration would block launch.

## Decision
Phase 1 uses **outbound webhook posting only** (Adaptive Card JSON via incoming webhook URL). Teams channels receive daily briefs at scheduled times. No bot listener in Phase 1 — the portal handles interactive queries in Phase 2.

Scope limits (intentional):
- No `@bot` mentions or slash commands in Phase 1
- No message threading or reply handling
- Bot interaction table exists in schema for Phase 2 readiness

## Consequences
- **+** No IT/Azure registration required — just a webhook URL from Teams channel settings
- **+** Zero latency risk from bot listener infra
- **+** Adaptive Card format renders well on mobile and desktop Teams
- **−** One-way only — users cannot ask questions via Teams in Phase 1
- **−** Webhook URL is a secret that must be rotated if compromised
- **Review trigger:** Portal (Phase 2) is built → revisit full bot with Azure Bot Service registration
