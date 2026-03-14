#!/bin/bash
# Ananas AI — EC2 bootstrap script
# Runs once on first boot via EC2 user data.
# Installs all dependencies, clones the repo, sets up PostgreSQL, cron, and systemd services.

set -euo pipefail
exec > >(tee /var/log/ananas-bootstrap.log | logger -t ananas-bootstrap) 2>&1

echo "=== Ananas AI bootstrap starting ==="
GITHUB_REPO="${github_repo}"
DB_NAME="${db_name}"
DB_USER="${db_user}"
APP_DIR="/home/ubuntu/ananas-ai"
PYTHON_VERSION="3.12"

# ── System packages ───────────────────────────────────────────────────────────
apt-get update -y
apt-get install -y software-properties-common

# Python 3.12 requires deadsnakes PPA on Ubuntu 22.04
add-apt-repository ppa:deadsnakes/ppa -y
apt-get update -y
apt-get install -y \
    python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python3-pip \
    postgresql postgresql-contrib \
    git curl jq unzip \
    awscli

# CloudWatch agent — not in standard Ubuntu repos, install from AWS S3
curl -sO https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i amazon-cloudwatch-agent.deb
rm -f amazon-cloudwatch-agent.deb

# SSM agent — enables GitHub Actions deploy without SSH port exposure
snap install amazon-ssm-agent --classic
systemctl enable snap.amazon-ssm-agent.amazon-ssm-agent.service
systemctl start snap.amazon-ssm-agent.amazon-ssm-agent.service

# ── PostgreSQL ────────────────────────────────────────────────────────────────
systemctl enable postgresql
systemctl start postgresql

sudo -u postgres psql << SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${db_user}') THEN
    CREATE ROLE ${db_user} WITH LOGIN PASSWORD '$(openssl rand -base64 32)';
  END IF;
END
\$\$;
CREATE DATABASE IF NOT EXISTS ${db_name} OWNER ${db_user};
SQL

echo "PostgreSQL ready: ${db_name}@localhost"

# ── Clone repo ────────────────────────────────────────────────────────────────
if [ ! -d "$APP_DIR" ]; then
    git clone "https://github.com/${github_repo}.git" "$APP_DIR"
    chown -R ubuntu:ubuntu "$APP_DIR"
fi

# ── Python venv + dependencies ────────────────────────────────────────────────
sudo -u ubuntu bash << 'BASH'
cd /home/ubuntu/ananas-ai
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -e . --quiet
echo "Python environment ready"
BASH

# ── Load secrets from AWS Secrets Manager → /etc/ananas-ai/env ───────────────
mkdir -p /etc/ananas-ai
chmod 700 /etc/ananas-ai

load_secret() {
    local secret_name="$1"
    aws secretsmanager get-secret-value \
        --secret-id "ananas-ai/$secret_name" \
        --region "${aws_region}" \
        --query SecretString \
        --output text 2>/dev/null || echo "{}"
}

# Write all secrets as env vars
python3 << PYEOF
import json, os

secrets = {}
for name in ["anthropic", "openai", "google", "meta", "pinterest", "microsoft", "database"]:
    try:
        import subprocess
        result = subprocess.run(
            ["aws", "secretsmanager", "get-secret-value",
             "--secret-id", f"ananas-ai/{name}",
             "--region", "${aws_region}",
             "--query", "SecretString", "--output", "text"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            secrets.update(json.loads(result.stdout))
    except Exception as e:
        print(f"Warning: could not load secret {name}: {e}")

with open("/etc/ananas-ai/env", "w") as f:
    for k, v in secrets.items():
        if v and v != "REPLACE_ME":
            f.write(f'{k}="{v}"\n')

os.chmod("/etc/ananas-ai/env", 0o600)
print(f"Wrote {len(secrets)} environment variables to /etc/ananas-ai/env")
PYEOF

# ── Bootstrap database schema ─────────────────────────────────────────────────
sudo -u ubuntu bash << 'BASH'
cd /home/ubuntu/ananas-ai
source .venv/bin/activate
set -a && source /etc/ananas-ai/env && set +a
python -m ananas_ai.cli bootstrap-db
echo "Database schema applied"
BASH

# ── Cron jobs ─────────────────────────────────────────────────────────────────
# Runs agents on the Phase 1 schedule (times are UTC = MKD - 1h in summer)
CRON_FILE="/etc/cron.d/ananas-ai"
cat > "$CRON_FILE" << 'CRONEOF'
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
ANANAS_ROOT=/home/ubuntu/ananas-ai

# Ananas AI Phase 1 -- single daily brief (UTC)
# MKD is UTC+1 (winter) / UTC+2 (summer) -- adjust seasonally
# run-brief runs all 5 agents internally then posts one card to #ai-marketing

# Daily brief -- 07:30 MKD -> 06:30 UTC
30 6 * * * ubuntu cd /home/ubuntu/ananas-ai && source .venv/bin/activate && set -a && source /etc/ananas-ai/env && set +a && python3 -m ananas_ai.cli run-brief >> /var/log/ananas-agents.log 2>&1

# Nightly DB backup to S3 — 02:00 UTC
0 2 * * * ubuntu /home/ubuntu/ananas-ai/infra/scripts/backup_db.sh >> /var/log/ananas-backup.log 2>&1

# Refresh secrets from Secrets Manager — daily at 01:00 UTC
0 1 * * * root python3 /home/ubuntu/ananas-ai/infra/scripts/refresh_secrets.py
CRONEOF

chmod 644 "$CRON_FILE"
echo "Cron jobs installed"

# ── CloudWatch agent config ───────────────────────────────────────────────────
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'CWJSON'
{
  "agent": { "run_as_user": "root" },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/ananas-agents.log",
            "log_group_name": "/ananas-ai/agents",
            "log_stream_name": "{instance_id}",
            "timezone": "UTC"
          },
          {
            "file_path": "/var/log/ananas-bootstrap.log",
            "log_group_name": "/ananas-ai/system",
            "log_stream_name": "{instance_id}-bootstrap"
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "CWAgent",
    "metrics_collected": {
      "cpu": { "measurement": ["cpu_usage_active"], "metrics_collection_interval": 60 },
      "mem": { "measurement": ["mem_used_percent"], "metrics_collection_interval": 60 },
      "disk": {
        "measurement": ["disk_used_percent"],
        "metrics_collection_interval": 60,
        "resources": ["/"]
      }
    }
  }
}
CWJSON

/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
    -s

echo "=== Ananas AI bootstrap complete ==="
echo "Run 'ananas-ai doctor' to verify platform health"
