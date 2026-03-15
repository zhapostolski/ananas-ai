#!/bin/bash
# Ananas AI — EC2 bootstrap script
# Runs once on first boot via EC2 user data.
# Installs all dependencies, clones the repo, sets up SQLite, Node.js, cron, and PM2.

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
    git curl jq unzip \
    awscli nginx

# CloudWatch agent — not in standard Ubuntu repos, install from AWS S3
curl -sO https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i amazon-cloudwatch-agent.deb
rm -f amazon-cloudwatch-agent.deb

# SSM agent — enables GitHub Actions deploy without SSH port exposure
snap install amazon-ssm-agent --classic
systemctl enable snap.amazon-ssm-agent.amazon-ssm-agent.service
systemctl start snap.amazon-ssm-agent.amazon-ssm-agent.service

# ── Node.js (for Next.js portal) via fnm ─────────────────────────────────────
sudo -u ubuntu bash << 'BASH'
curl -fsSL https://fnm.vercel.app/install | bash
export PATH="$HOME/.local/share/fnm:$PATH"
eval "$(fnm env)"
fnm install 20
fnm use 20
fnm default 20
npm install -g pm2
echo "Node.js $(node -v) + PM2 ready"
BASH

# Symlink node/pm2 into system PATH for cron
NODE_BIN=$(sudo -u ubuntu bash -c 'export PATH="$HOME/.local/share/fnm:$PATH"; eval "$(fnm env)"; which node')
ln -sf "$NODE_BIN" /usr/local/bin/node
ln -sf "$(dirname $NODE_BIN)/npm" /usr/local/bin/npm
ln -sf "$(dirname $NODE_BIN)/pm2" /usr/local/bin/pm2

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
for name in ["anthropic", "openai", "google", "meta", "pinterest", "microsoft", "database", "ananas-internal"]:
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

# ── Build and start Next.js portal ───────────────────────────────────────────
sudo -u ubuntu bash << 'BASH'
export PATH="$HOME/.local/share/fnm:$PATH"
eval "$(fnm env)"
cd /home/ubuntu/ananas-ai/portal

# Write portal .env.local from /etc/ananas-ai/env
source /etc/ananas-ai/env 2>/dev/null || true
cat > .env.local << ENVLOCAL
AZURE_AD_CLIENT_ID=${AZURE_AD_CLIENT_ID}
AZURE_AD_CLIENT_SECRET=${AZURE_AD_CLIENT_SECRET}
AZURE_AD_TENANT_ID=${AZURE_AD_TENANT_ID}
AUTH_SECRET=${AUTH_SECRET:-$(openssl rand -hex 32)}
NEXTAUTH_URL=https://ai.ananas.mk
DB_PATH=/home/ubuntu/ananas-ai/ananas_ai.db
ENVLOCAL
chmod 600 .env.local

npm ci --silent
npm run build

# Start with PM2
pm2 start npm --name "ananas-portal" -- start
echo "Portal built and started on port 3000"
BASH

# ── Teams bot (Python aiohttp, port 3978) ────────────────────────────────────
sudo -u ubuntu bash << 'BASH'
cd /home/ubuntu/ananas-ai
source .venv/bin/activate
set -a && source /etc/ananas-ai/env && set +a
pm2 start "python -m ananas_ai.bot.app" --name "ananas-bot" --interpreter python
echo "Teams bot started on port 3978"
BASH

# Save PM2 list and enable startup
sudo -u ubuntu bash << 'BASH'
export PATH="$HOME/.local/share/fnm:$PATH"
eval "$(fnm env)"
pm2 save
pm2 startup systemd -u ubuntu --hp /home/ubuntu | tail -1 | bash || true
BASH

# ── nginx reverse proxy for portal ───────────────────────────────────────────
cat > /etc/nginx/sites-available/ananas-portal << 'NGINXEOF'
server {
    listen 80;
    server_name ai.ananas.mk;

    # Teams bot endpoint -- Bot Framework POSTs here
    location /api/messages {
        proxy_pass http://localhost:3978;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Bot health check
    location /bot/health {
        proxy_pass http://localhost:3978/health;
    }

    # Portal (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/ananas-portal /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl enable nginx && systemctl restart nginx
echo "nginx configured for ai.ananas.mk → localhost:3000"

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

# Refresh Meta long-lived token — 1st of each month at 03:00 UTC
0 3 1 * * ubuntu cd /home/ubuntu/ananas-ai && source .venv/bin/activate && set -a && source /etc/ananas-ai/env && set +a && python3 scripts/refresh_meta_token.py --env /etc/ananas-ai/env >> /var/log/ananas-agents.log 2>&1
CRONEOF

chmod 644 "$CRON_FILE"
echo "Cron jobs installed"

# ── Log rotation ──────────────────────────────────────────────────────────────
cat > /etc/logrotate.d/ananas-ai << 'LOGEOF'
/var/log/ananas-agents.log {
    weekly
    rotate 8
    compress
    missingok
    notifempty
    copytruncate
}
/var/log/ananas-backup.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
    copytruncate
}
LOGEOF
echo "Log rotation configured"

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
