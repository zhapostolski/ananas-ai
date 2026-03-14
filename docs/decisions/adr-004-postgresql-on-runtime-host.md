# ADR-004 PostgreSQL on Runtime Host in Phase 1

## Status
Accepted

## Context
Phase 1 needs a simple and affordable operational footprint.

## Decision
Run PostgreSQL on the same EC2 host as the runtime in Phase 1.

## Consequences
- Simpler early deployment
- Lower cost
- Requires disciplined off-instance backups and a later path to service separation
