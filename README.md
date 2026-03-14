# Ananas AI Platform Repository

This pack is a populated project knowledge base for the Ananas AI Platform.

It is designed for two audiences:
- Humans: architecture, budget, roadmap, decisions, and operating rules
- Claude Code: persistent project memory, scoped rules, subagents, schedules, metrics, and integration maps

## Repository intent
This is the marketing-first implementation of the broader Ananas AI Platform.
Phase 1 covers:
- AWS runtime (EC2 + PostgreSQL)
- Teams channel posting
- five specialist agents (daily cron)
- multi-model routing
- GitHub-governed prompts, metrics, schemas, and schedules

Phase 2 adds:
- ai.ananas.mk portal
- Teams bot engagement
- 11 additional specialist agents

## Most important files
- `CLAUDE.md` — project-wide operating context for Claude Code
- `.claude/rules/` — modular project rules
- `.claude/agents/` — project subagents
- `docs/architecture/architecture-v1.md` — business-facing architecture narrative
- `docs/budget/budget.md` — detailed budget scenarios
- `docs/roadmap/phase-1-roadmap.md` — implementation plan
- `config/` — live architecture-driving config files
- `scripts/validate_pack.py` — repository sanity checks
