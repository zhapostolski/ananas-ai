#!/usr/bin/env python3
"""
Refresh the Meta long-lived access token stored in .env.

Meta long-lived tokens last ~60 days. Each call to this script
exchanges the current token for a new 60-day token and writes it
back to the .env file in the project root.

Usage:
    python scripts/refresh_meta_token.py [--env /path/to/.env]

Run monthly via cron to keep it fresh.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

import requests

GRAPH_BASE = "https://graph.facebook.com/v19.0"
APP_ID = "925959596694676"


def refresh_token(current_token: str, app_secret: str) -> str:
    resp = requests.get(
        f"{GRAPH_BASE}/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": APP_ID,
            "client_secret": app_secret,
            "fb_exchange_token": current_token,
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if "access_token" not in data:
        print(f"Error: {data}", file=sys.stderr)
        sys.exit(1)
    return data["access_token"]


def update_env_file(env_path: str, new_token: str) -> None:
    with open(env_path) as f:
        content = f.read()
    updated = re.sub(
        r"^(META_ACCESS_TOKEN=).*$",
        rf"\g<1>{new_token}",
        content,
        flags=re.MULTILINE,
    )
    with open(env_path, "w") as f:
        f.write(updated)
    print(f"Updated META_ACCESS_TOKEN in {env_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh Meta long-lived access token")
    parser.add_argument("--env", default=".env", help="Path to .env file")
    args = parser.parse_args()

    current_token = os.environ.get("META_ACCESS_TOKEN")
    app_secret = os.environ.get("META_APP_SECRET")

    if not current_token:
        sys.exit("META_ACCESS_TOKEN not set in environment")
    if not app_secret:
        sys.exit("META_APP_SECRET not set in environment")

    print("Exchanging token...")
    new_token = refresh_token(current_token, app_secret)
    print(f"New token: {new_token[:20]}...")

    env_path = args.env
    if os.path.exists(env_path):
        update_env_file(env_path, new_token)
    else:
        print(f"\nNew META_ACCESS_TOKEN:\n{new_token}")
        print(f"\n(File {env_path} not found — copy the token above manually)")


if __name__ == "__main__":
    main()
