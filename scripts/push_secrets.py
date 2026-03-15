#!/usr/bin/env python3
"""
Push all confirmed credentials to AWS Secrets Manager.

Run this once from your dev machine (with AWS credentials that have
secretsmanager:PutSecretValue on ananas-ai/*).

Usage:
    # Dry run -- prints what would be pushed
    python scripts/push_secrets.py --dry-run

    # Push everything
    python scripts/push_secrets.py

    # Push specific secret group
    python scripts/push_secrets.py --only google meta

Secrets are structured to match what refresh_secrets.py expects.
The service account JSON is pushed separately as a raw file (not JSON-encoded).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# ── Fill in values before running ────────────────────────────────────────────
# Values with REPLACE_ME are not yet known. Do not run until all are filled.

SECRETS: dict[str, dict | str] = {
    "anthropic": {
        "ANTHROPIC_API_KEY": "REPLACE_ME",
    },
    "openai": {
        "OPENAI_API_KEY": "REPLACE_ME",
    },
    "google": {
        "GA4_PROPERTY_ID": "374249510",
        "GA4_CREDENTIALS": "/home/ubuntu/ananas-ai/secrets/google-sa.json",
        "GOOGLE_ADS_DEVELOPER_TOKEN": "eXEYMMzTsTSxcJZUrXIiUA",
        "GOOGLE_ADS_SERVICE_ACCOUNT_FILE": "/home/ubuntu/ananas-ai/secrets/google-sa.json",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "2135950127",
        # Search MK, Display MK, Display MK alt, YouTube MK
        "GOOGLE_ADS_CUSTOMER_IDS": "5832113533,9993867198,8508967046,4783821547",
        "SEARCH_CONSOLE_SITE_URL": "https://ananas.mk/",
    },
    # google-sa-json: set via --sa-json flag pointing to the key file
    "meta": {
        "META_ACCESS_TOKEN": "REPLACE_ME",  # long-lived token from token exchange
        "META_AD_ACCOUNT_ID": "act_174735152216843",
        "META_APP_SECRET": "fca40d216af2067c34f8829aedb884b0",
    },
    "microsoft": {
        "TEAMS_TENANT_ID": "c764ab62-ad43-4930-aa38-c9e23a990cb0",
        "TEAMS_CLIENT_ID": "3d0a6854-b742-461d-b98a-420efd6fd8dd",
        "TEAMS_CLIENT_SECRET": "REPLACE_ME",
        "AZURE_AD_CLIENT_ID": "3d0a6854-b742-461d-b98a-420efd6fd8dd",
        "AZURE_AD_CLIENT_SECRET": "REPLACE_ME",
        "AZURE_AD_TENANT_ID": "c764ab62-ad43-4930-aa38-c9e23a990cb0",
    },
    "database": {
        "ANANAS_DB_PATH": "/home/ubuntu/ananas-ai/ananas_ai.db",
    },
}

REGION = os.environ.get("AWS_REGION", "eu-central-1")


def _put(client, secret_id: str, value: str, dry_run: bool) -> None:
    print(f"  → {secret_id}")
    if dry_run:
        preview = value[:80] + "..." if len(value) > 80 else value
        print(f"    (dry run) value: {preview}")
        return
    client.put_secret_value(SecretId=secret_id, SecretString=value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", nargs="+", metavar="GROUP", help="Only push these groups")
    parser.add_argument(
        "--sa-json",
        metavar="FILE",
        help="Path to Google service account JSON file to push as google-sa-json",
    )
    args = parser.parse_args()

    # Validate no REPLACE_ME in pushed groups
    groups_to_push = args.only or list(SECRETS.keys())
    for group in groups_to_push:
        if group not in SECRETS:
            sys.exit(f"Unknown group: {group}. Valid: {list(SECRETS.keys())}")
        val = SECRETS[group]
        if isinstance(val, dict):
            placeholders = [k for k, v in val.items() if v == "REPLACE_ME"]
            if placeholders and not args.dry_run:
                print(f"WARNING: {group} has unfilled values: {placeholders}")
                resp = input("Push anyway? [y/N] ")
                if resp.lower() != "y":
                    sys.exit("Aborted.")

    import boto3  # noqa: PLC0415

    client = boto3.client("secretsmanager", region_name=REGION)

    print(f"Pushing to AWS Secrets Manager ({REGION})...")

    for group in groups_to_push:
        val = SECRETS[group]
        secret_string = json.dumps(val) if isinstance(val, dict) else val
        _put(client, f"ananas-ai/{group}", secret_string, args.dry_run)

    if args.sa_json or (not args.only):
        sa_path = args.sa_json
        if sa_path and os.path.exists(sa_path):
            with open(sa_path) as f:
                sa_content = f.read()
            _put(client, "ananas-ai/google-sa-json", sa_content, args.dry_run)
        elif not args.only:
            print("  → ananas-ai/google-sa-json (SKIPPED -- use --sa-json /path/to/key.json)")

    print("Done.")


if __name__ == "__main__":
    main()
