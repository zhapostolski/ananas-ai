# ADR-003 Multi-Model Routing Policy

## Status
Accepted

## Context
Model usage is the largest variable cost driver.

## Decision
Use a low-cost routing model for lightweight routing/classification, Claude Sonnet as the default execution model, and Claude Opus only for explicit escalation.

## Consequences
- Better cost control
- More explicit runtime behavior
- Slightly more configuration complexity
