# ADR-004 PostgreSQL on Runtime Host in Phase 1

## Status
Accepted — implemented March 2026

## Context
The platform needs persistent storage for agent outputs, run logs, token usage, system health, and delivery logs (6 tables, ~schema.sql). Storage options evaluated:

- **AWS RDS PostgreSQL (~$25–50/month)**: managed, automatic backups, multi-AZ possible — but doubles the infrastructure cost in Phase 1 for a low-write workload (~5 writes/day)
- **SQLite on EC2**: simplest, zero cost, but no concurrent writes and not suitable for Phase 2 multi-process access
- **PostgreSQL on the same EC2 host**: chosen — full SQL, concurrent write support, zero extra cost, acceptable risk for Phase 1 volume

Local dev uses SQLite via `ANANAS_DB_PATH=:memory:` or a tmp file. Production EC2 uses PostgreSQL. The `persistence.py` layer is DB-agnostic (uses standard SQL, no PostgreSQL-specific syntax except `ON CONFLICT DO UPDATE` which SQLite 3.24+ also supports).

## Decision
PostgreSQL installed on the EC2 runtime host. Password stored in AWS Secrets Manager. Nightly `pg_dump` → S3 via `infra/scripts/backup_db.sh` cron job (03:00 UTC).

## Consequences
- **+** Zero added cost vs. RDS (~$300–600/year saved)
- **+** Full SQL support; SQLite-compatible query layer for local dev
- **+** Simple operations: one host, one backup target
- **−** DB and app share host resources — a runaway agent could starve the DB
- **−** No automatic failover; host failure = full outage until EC2 restart
- **−** Manual backup discipline required (automated but must be monitored)
- **Review trigger:** Phase 2 multi-agent concurrency, or data retention > 90 days → migrate to RDS t3.micro
