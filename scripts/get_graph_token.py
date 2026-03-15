#!/usr/bin/env python3
"""One-time script to get a Graph API refresh token via device code flow.

Run this once locally or on EC2. It will print a URL and code - open the URL
in a browser, enter the code, and sign in as zharko.apostolski@ananas.mk.

The script prints GRAPH_REFRESH_TOKEN=<value> to add to your .env file.

Usage:
    python scripts/get_graph_token.py
"""

import json
import os
import sys
import urllib.parse
import urllib.request

CLIENT_ID = os.environ.get("GRAPH_CLIENT_ID", "3d0a6854-b742-461d-b98a-420efd6fd8dd")
TENANT_ID = os.environ.get("GRAPH_TENANT_ID", "c764ab62-ad43-4930-aa38-c9e23a990cb0")
SCOPES = "https://graph.microsoft.com/Mail.Send offline_access"


def main() -> None:
    # Step 1: start device code flow
    device_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode"
    data = urllib.parse.urlencode({"client_id": CLIENT_ID, "scope": SCOPES}).encode()
    req = urllib.request.Request(device_url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=15) as resp:
        flow = json.loads(resp.read())

    print("\n" + "=" * 60)
    print(flow["message"])
    print("=" * 60 + "\n")

    # Step 2: poll for token
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    import time

    while True:
        time.sleep(flow.get("interval", 5))
        poll_data = urllib.parse.urlencode(
            {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": CLIENT_ID,
                "device_code": flow["device_code"],
            }
        ).encode()
        req2 = urllib.request.Request(token_url, data=poll_data, method="POST")
        req2.add_header("Content-Type", "application/x-www-form-urlencoded")
        try:
            with urllib.request.urlopen(req2, timeout=15) as resp2:
                token = json.loads(resp2.read())
        except urllib.error.HTTPError as e:
            body = json.loads(e.read())
            err = body.get("error", "")
            if err == "authorization_pending":
                print("Waiting for sign-in...", end="\r", flush=True)
                continue
            if err == "authorization_declined":
                print("\nSign-in was declined.")
                sys.exit(1)
            if err == "expired_token":
                print("\nCode expired - re-run the script.")
                sys.exit(1)
            print(f"\nUnexpected error: {body}")
            sys.exit(1)
        else:
            break

    refresh_token = token.get("refresh_token", "")
    if not refresh_token:
        print("No refresh token returned - make sure offline_access scope is added.")
        sys.exit(1)

    print("\n\nSuccess! Add this line to your .env file on EC2:\n")
    print(f"GRAPH_REFRESH_TOKEN={refresh_token}")
    print()


if __name__ == "__main__":
    import urllib.error

    main()
