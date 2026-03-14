# Operating Rhythm

## Daily — automated (EC2 cron)

| Time | Job | Teams channel |
|---|---|---|
| 06:00 | performance-agent | #marketing-performance |
| 06:30 | crm-lifecycle-agent | #marketing-crm |
| 07:00 | reputation-agent | #marketing-reputation |
| 07:15 | marketing-ops-agent | #marketing-ops |
| 07:30 | cross-channel-brief-agent | #marketing-summary + #executive-summary |
| 03:00 | DB backup to S3 | — |

## Daily — human review (5 min)

1. Check Teams channels — scan the brief in #executive-summary
2. Check GitHub Actions — confirm last Release run is green
3. If any agent shows WARNING/CRITICAL — investigate before standup

## Weekly — platform health (30 min, Mondays)

- Review agent run logs: `psql` → `SELECT * FROM agent_logs ORDER BY run_at DESC LIMIT 50;`
- Check token usage vs caps (200k/day per agent)
- Review any new credential blockers (see `docs/operations/access-requirements.md`)
- Check for pending integrations that unblocked since last week
- If any config changed — run `make validate` and review CHANGELOG

## Release procedure

1. Work on `main` for normal changes
2. Before every release: `make release VERSION=vX.Y.Z`
3. Monitor GitHub Actions → Release workflow (all 4 QA jobs must pass before deploy)
4. After successful deploy: verify on EC2 with a manual `run-brief` if the change was significant

## Incident response

**Agent producing no output:**
```bash
# Check logs on EC2 via SSM
aws ssm start-session --target <INSTANCE_ID> --region eu-central-1
cd /opt/ananas-ai && source .venv/bin/activate
python -m ananas_ai.cli list-latest
```

**Deploy failed on GitHub Actions:**
- Check the Release workflow logs in GitHub → Actions tab
- Fix the issue, commit, run `make release VERSION=vX.Y.Z-hotfix`
- Never push a tag manually to bypass QA

**EC2 instance unreachable:**
```bash
# Check instance state
aws ec2 describe-instances --instance-ids <INSTANCE_ID> --region eu-central-1
# Restart if stopped
aws ec2 start-instances --instance-ids <INSTANCE_ID> --region eu-central-1
```

**Anthropic API unavailable:**
- Automatic: agents fall back to OpenAI GPT-4o via `model_client.py`
- Check fallback in logs: `fallback: true` in agent output
- If both APIs fail: agents write `model unavailable` to DB and continue

## Adding a new integration (checklist)

- [ ] Add credentials to AWS Secrets Manager: `aws secretsmanager create-secret ...`
- [ ] Add credentials to GitHub Actions secrets (for CI test runs if needed)
- [ ] Add to `.env.example`
- [ ] Update `config/integrations-matrix.json`
- [ ] Implement `is_configured()` and `safe_fetch()` in the integration class
- [ ] Run `make release VERSION=vX.Y.Z`
