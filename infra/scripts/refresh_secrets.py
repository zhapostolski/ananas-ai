#!/usr/bin/env python3
"""Refresh secrets from AWS Secrets Manager into /etc/ananas-ai/env.

Runs daily at 01:00 UTC via cron (as root). Replaces the env file in-place
so the next cron agent run picks up rotated credentials.

Also writes the Google service account JSON file to disk if the
ananas-ai/google-sa-json secret exists.
"""

import json
import os
import subprocess
import sys

SECRETS = ["anthropic", "openai", "google", "meta", "pinterest", "microsoft", "database"]
ENV_FILE = "/etc/ananas-ai/env"
REGION = os.environ.get("AWS_REGION", "eu-central-1")
GA4_CREDENTIALS_PATH = "/home/ubuntu/ananas-ai/secrets/google-sa.json"


def fetch_secret_raw(name: str) -> str:
    """Fetch raw secret string (not parsed as JSON)."""
    result = subprocess.run(
        [
            "aws",
            "secretsmanager",
            "get-secret-value",
            "--secret-id",
            f"ananas-ai/{name}",
            "--region",
            REGION,
            "--query",
            "SecretString",
            "--output",
            "text",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def fetch_secret(name: str) -> dict:
    raw = fetch_secret_raw(name)
    if not raw:
        print(f"Warning: could not fetch secret ananas-ai/{name}", file=sys.stderr)
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"Warning: invalid JSON in secret ananas-ai/{name}", file=sys.stderr)
        return {}


def deploy_google_credentials() -> None:
    """Write the Google service account JSON file to disk."""
    raw = fetch_secret_raw("google-sa-json")
    if not raw:
        print(
            "Warning: ananas-ai/google-sa-json not found, skipping credentials file",
            file=sys.stderr,
        )
        return
    os.makedirs(os.path.dirname(GA4_CREDENTIALS_PATH), exist_ok=True)
    with open(GA4_CREDENTIALS_PATH, "w") as f:
        f.write(raw)
    os.chmod(GA4_CREDENTIALS_PATH, 0o600)
    print(f"Wrote Google credentials to {GA4_CREDENTIALS_PATH}")


def main() -> None:
    all_vars: dict = {}
    for name in SECRETS:
        all_vars.update(fetch_secret(name))

    lines = []
    for k, v in all_vars.items():
        if v and v != "REPLACE_ME":
            lines.append(f'{k}="{v}"\n')

    with open(ENV_FILE, "w") as f:
        f.writelines(lines)

    os.chmod(ENV_FILE, 0o600)
    print(f"Refreshed {len(lines)} secrets into {ENV_FILE}")

    deploy_google_credentials()


if __name__ == "__main__":
    main()
