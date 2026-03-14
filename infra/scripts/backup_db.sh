#!/bin/bash
# Ananas AI — nightly PostgreSQL backup to S3
# Runs at 02:00 UTC via cron. Dumps the DB and uploads to S3 with date stamp.

set -euo pipefail

APP_DIR="/home/ubuntu/ananas-ai"
DB_NAME="ananas_ai"
BACKUP_DIR="/tmp/ananas-backups"
DATE=$(date +%Y-%m-%d)
BACKUP_FILE="$BACKUP_DIR/ananas_ai_$DATE.sql.gz"

# Load env for S3 bucket name
set -a && source /etc/ananas-ai/env && set +a

S3_BUCKET="${S3_BACKUP_BUCKET:-ananas-ai-backups-production}"
AWS_REGION="${AWS_REGION:-eu-central-1}"

mkdir -p "$BACKUP_DIR"

echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') [backup] Starting PostgreSQL backup for $DB_NAME"

# Dump and compress
sudo -u postgres pg_dump "$DB_NAME" | gzip > "$BACKUP_FILE"

echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') [backup] Dump complete: $(du -h "$BACKUP_FILE" | cut -f1)"

# Upload to S3
aws s3 cp "$BACKUP_FILE" "s3://$S3_BUCKET/postgres/$DATE/ananas_ai_$DATE.sql.gz" \
    --region "$AWS_REGION" \
    --storage-class STANDARD_IA

echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') [backup] Uploaded to s3://$S3_BUCKET/postgres/$DATE/"

# Clean up local file
rm -f "$BACKUP_FILE"

echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') [backup] Done"
