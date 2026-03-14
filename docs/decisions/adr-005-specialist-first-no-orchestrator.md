# ADR-005 Specialist-First Design Without Permanent Orchestrator

## Status
Accepted

## Context
A permanent orchestrator agent would add latency, cost, and runtime complexity in normal flows.

## Decision
Use specialist agents directly and keep cross-channel synthesis as a scheduled summary layer rather than a permanent orchestration layer.

## Consequences
- Lower cost and lower runtime complexity
- Clearer ownership per agent
- Some complex cross-domain cases require explicit synthesis workflows later
