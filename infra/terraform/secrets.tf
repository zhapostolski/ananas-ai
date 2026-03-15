# ── Secrets Manager — structure only ─────────────────────────────────────────
# These create the secret containers. Fill in the actual values via:
#   aws secretsmanager put-secret-value --secret-id ananas-ai/... --secret-string '{"key":"value"}'
# Or use the AWS Console.

resource "aws_secretsmanager_secret" "anthropic" {
  name                    = "ananas-ai/anthropic"
  description             = "Anthropic API credentials"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret" "openai" {
  name                    = "ananas-ai/openai"
  description             = "OpenAI API credentials (GPT-4o-mini router)"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret" "google" {
  name                    = "ananas-ai/google"
  description             = "Google credentials - GA4, Ads, Search Console service account"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret" "google_sa_json" {
  name                    = "ananas-ai/google-sa-json"
  description             = "Google service account JSON key file (full JSON, not base64)"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret" "meta" {
  name                    = "ananas-ai/meta"
  description             = "Meta Ads API credentials"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret" "pinterest" {
  name                    = "ananas-ai/pinterest"
  description             = "Pinterest Ads API credentials"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret" "microsoft" {
  name                    = "ananas-ai/microsoft"
  description             = "Microsoft Graph API credentials (Teams + Outlook)"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret" "database" {
  name                    = "ananas-ai/database"
  description             = "PostgreSQL connection credentials"
  recovery_window_in_days = 7
}

# ── Secret value templates (initial placeholder — update after Terraform apply) ─

resource "aws_secretsmanager_secret_version" "anthropic" {
  secret_id     = aws_secretsmanager_secret.anthropic.id
  secret_string = jsonencode({ ANTHROPIC_API_KEY = "REPLACE_ME" })

  lifecycle { ignore_changes = [secret_string] }
}

resource "aws_secretsmanager_secret_version" "openai" {
  secret_id     = aws_secretsmanager_secret.openai.id
  secret_string = jsonencode({ OPENAI_API_KEY = "REPLACE_ME" })

  lifecycle { ignore_changes = [secret_string] }
}

resource "aws_secretsmanager_secret_version" "google" {
  secret_id     = aws_secretsmanager_secret.google.id
  secret_string = jsonencode({
    GA4_PROPERTY_ID                  = "REPLACE_ME",
    GA4_CREDENTIALS                  = "/home/ubuntu/ananas-ai/secrets/google-sa.json",
    GOOGLE_ADS_DEVELOPER_TOKEN       = "REPLACE_ME",
    GOOGLE_ADS_SERVICE_ACCOUNT_FILE  = "/home/ubuntu/ananas-ai/secrets/google-sa.json",
    GOOGLE_ADS_LOGIN_CUSTOMER_ID     = "REPLACE_ME",
    GOOGLE_ADS_CUSTOMER_IDS          = "REPLACE_ME",
    SEARCH_CONSOLE_SITE_URL          = "https://ananas.mk/",
  })

  lifecycle { ignore_changes = [secret_string] }
}

resource "aws_secretsmanager_secret_version" "google_sa_json" {
  secret_id     = aws_secretsmanager_secret.google_sa_json.id
  secret_string = "REPLACE_ME"

  lifecycle { ignore_changes = [secret_string] }
}

resource "aws_secretsmanager_secret_version" "meta" {
  secret_id     = aws_secretsmanager_secret.meta.id
  secret_string = jsonencode({
    META_ACCESS_TOKEN  = "REPLACE_ME",
    META_AD_ACCOUNT_ID = "REPLACE_ME",
  })

  lifecycle { ignore_changes = [secret_string] }
}

resource "aws_secretsmanager_secret_version" "pinterest" {
  secret_id     = aws_secretsmanager_secret.pinterest.id
  secret_string = jsonencode({
    PINTEREST_ACCESS_TOKEN  = "REPLACE_ME",
    PINTEREST_AD_ACCOUNT_ID = "REPLACE_ME",
  })

  lifecycle { ignore_changes = [secret_string] }
}

resource "aws_secretsmanager_secret_version" "microsoft" {
  secret_id     = aws_secretsmanager_secret.microsoft.id
  secret_string = jsonencode({
    TEAMS_TENANT_ID      = "REPLACE_ME",
    TEAMS_CLIENT_ID      = "REPLACE_ME",
    TEAMS_CLIENT_SECRET  = "REPLACE_ME",
    AZURE_AD_CLIENT_ID   = "REPLACE_ME",
    AZURE_AD_CLIENT_SECRET = "REPLACE_ME",
    AZURE_AD_TENANT_ID   = "REPLACE_ME",
    AUTH_SECRET          = "REPLACE_ME",
  })

  lifecycle { ignore_changes = [secret_string] }
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id     = aws_secretsmanager_secret.database.id
  secret_string = jsonencode({
    ANANAS_DB_PATH = "/home/ubuntu/ananas-ai/ananas_ai.db",
    DATABASE_URL   = "postgresql://ananas_ai:REPLACE_ME@localhost/ananas_ai",
  })

  lifecycle { ignore_changes = [secret_string] }
}
