# Quick Start — Ananas AI Platform

## Dev environment (local WSL2)

```bash
# SSH to GitHub with work account
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_work" git clone git@github-work:zhapostolski/ananas-ai.git

# Enter project
cd ananas-ai

# Activate venv
source .venv/bin/activate

# Load env (local dev)
cp .env.example .env
# Edit .env: set GA4_PROPERTY_ID=374249510 and local DB path

# Authenticate GA4 (local dev only)
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/analytics.readonly

# Run health check
python -m ananas_ai.cli doctor

# Bootstrap database
python -m ananas_ai.cli bootstrap-db

# Run a single agent
python -m ananas_ai.cli run-agent performance

# Run full morning brief
python -m ananas_ai.cli run-brief

# List latest outputs
python -m ananas_ai.cli list-latest
```

## Production (AWS EC2)

EC2 access is via AWS SSM only (SSH port is closed). Requires AWS CLI configured.

```bash
# Open interactive session on EC2
aws ssm start-session --target <INSTANCE_ID> --region eu-central-1

# Check cron status

# Check last brief
cd /opt/ananas-ai && source .venv/bin/activate
python -m ananas_ai.cli list-latest

# View agent logs
psql -U ananas_ai -d ananas_ai -c "SELECT agent_name, run_at, status, model_used FROM agent_logs ORDER BY run_at DESC LIMIT 20;"

# Manual brief trigger
python -m ananas_ai.cli run-brief

# Check system health
python -m ananas_ai.cli doctor
```

## Secrets (production)

All secrets in AWS Secrets Manager — never in .env on EC2.

```bash
# List secrets
aws secretsmanager list-secrets --filter Key=name,Values=ananas-ai

# Retrieve (for debugging)
aws secretsmanager get-secret-value --secret-id ananas-ai/ga4-service-account
```

## Teams channels

| Channel | Agent | Time |
|---|---|---|
| #marketing-performance | Performance Agent | 06:00 |
| #marketing-crm | CRM & Lifecycle Agent | 06:30 |
| #marketing-reputation | Reputation Agent | 07:00 |
| #marketing-ops | Marketing Ops Agent | 07:15 |
| #marketing-summary | Cross-Channel Brief | 07:30 |
| #executive-summary | Cross-Channel Brief | 07:30 |

Denis also receives the executive brief by email at ~07:35.

## Backup and restore

```bash
# Manual DB backup
pg_dump -U ananas_ai ananas_ai | gzip > backup_$(date +%Y%m%d).sql.gz
aws s3 cp backup_$(date +%Y%m%d).sql.gz s3://ananas-ai-backups/manual/

# Restore from backup
aws s3 cp s3://ananas-ai-backups/daily/backup_YYYYMMDD.sql.gz .
gunzip backup_YYYYMMDD.sql.gz
psql -U ananas_ai ananas_ai < backup_YYYYMMDD.sql
```

## Cron schedule

```cron
00 6 * * * cd /opt/ananas-ai && .venv/bin/python -m ananas_ai.cli run-agent performance
30 6 * * * cd /opt/ananas-ai && .venv/bin/python -m ananas_ai.cli run-agent crm-lifecycle
00 7 * * * cd /opt/ananas-ai && .venv/bin/python -m ananas_ai.cli run-agent reputation
15 7 * * * cd /opt/ananas-ai && .venv/bin/python -m ananas_ai.cli run-agent marketing-ops
30 7 * * * cd /opt/ananas-ai && .venv/bin/python -m ananas_ai.cli run-brief
00 3 * * * cd /opt/ananas-ai && .venv/bin/python -m ananas_ai.cli db-backup
*/15 * * * * cd /opt/ananas-ai && .venv/bin/python -m ananas_ai.cli health-check
```
