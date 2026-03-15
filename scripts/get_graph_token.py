#!/usr/bin/env python3
"""One-time script to get a Graph API refresh token via device code flow.

Uses MSAL (already installed). Run on EC2, open the URL in a browser,
sign in as zharko.apostolski@ananas.mk, accept the permissions.
The refresh token is written to /tmp/graph_token.txt when done.

Usage:
    cd /home/ubuntu/ananas-ai
    source .venv/bin/activate
    python3 scripts/get_graph_token.py
"""

import sys

CLIENT_ID = "3d0a6854-b742-461d-b98a-420efd6fd8dd"
TENANT_ID = "c764ab62-ad43-4930-aa38-c9e23a990cb0"
SCOPES = [
    "https://graph.microsoft.com/Mail.Send",
    "https://graph.microsoft.com/Mail.Send.Shared",
]


def main() -> None:
    import msal  # noqa: PLC0415

    app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    )

    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        print(f"Failed to start device flow: {flow}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(flow["message"])
    print("=" * 60)
    print("\nWaiting for sign-in...", flush=True)

    result = app.acquire_token_by_device_flow(flow)

    if "error" in result:
        print(f"\nError: {result['error']}: {result.get('error_description', '')}")
        sys.exit(1)

    refresh_token = result.get("refresh_token", "")
    if not refresh_token:
        print("No refresh token returned. Make sure offline_access scope is included.")
        sys.exit(1)

    out = f"GRAPH_REFRESH_TOKEN={refresh_token}\n"
    with open("/tmp/graph_token.txt", "w") as f:
        f.write(out)

    print("\nSuccess! Add this to your .env on EC2:\n")
    print(out)


if __name__ == "__main__":
    main()
