#!/usr/bin/env python3
"""Refresh secrets from AWS Secrets Manager into /etc/ananas-ai/env.

Runs daily at 01:00 UTC via cron (as root). Replaces the env file in-place
so the next cron agent run picks up rotated credentials.
"""

import json
import os
import subprocess
import sys

SECRETS = ["anthropic", "openai", "google", "meta", "pinterest", "microsoft", "database"]
ENV_FILE = "/etc/ananas-ai/env"
REGION = os.environ.get("AWS_REGION", "eu-central-1")


def fetch_secret(name: str) -> dict:
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
        print(f"Warning: could not fetch secret ananas-ai/{name}", file=sys.stderr)
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Warning: invalid JSON in secret ananas-ai/{name}", file=sys.stderr)
        return {}


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


if __name__ == "__main__":
    main()
