# ADR-001 Runtime on AWS EC2

## Status
Accepted — implemented March 2026

## Context
The platform needs a production runtime for 5 specialist agents on daily cron schedules. Constraints: single operator, personal AWS account in Phase 1, Ananas already uses AWS so IT governance is simpler than onboarding a new vendor.

Alternatives considered:
- **Hetzner VPS (~€6/month)**: cheapest, but external vendor adds friction with IT governance and breaks the future AWS integration path
- **AWS Lambda**: no idle cost, but 5-minute agent runs are near the 15-minute limit and cold starts interfere with cron reliability
- **AWS ECS/Fargate**: more scalable but unnecessary orchestration complexity for a single-operator Phase 1
- **AWS EC2 t3.small (~$25/month total)**: chosen — persistent, always-on, cron-native, SSM-accessible, no open ports

## Decision
Single AWS EC2 t3.small in eu-central-1 (Frankfurt) with: Elastic IP, PostgreSQL on the same host (see ADR-004), SSM for remote access (SSH port closed), Secrets Manager for all credentials, S3 for DB backups, CloudWatch for monitoring.

## Consequences
- **+** Aligns with Ananas AWS infrastructure — no new vendor relationship
- **+** SSM is more secure than SSH (port 22 closed, no key management)
- **+** IAM role grants Secrets Manager access without hardcoded credentials
- **+** Clear upgrade path: t3.small → t3.medium → ECS when needed
- **−** ~$25/month vs ~$6/month for Hetzner (~$230/year extra)
- **−** Single-host PostgreSQL requires disciplined nightly S3 backups
- **Review trigger:** Cost exceeds $100/month or team grows beyond 2 operators → evaluate ECS migration
