"""Tests for Teams delivery -- verifies output without real webhook."""

from __future__ import annotations

from unittest.mock import patch

from ananas_ai.teams import post_message


def test_post_message_returns_ok():
    result = post_message("#marketing-performance", "Test Title", "Test body")
    assert result["status"] == "ok"
    assert result["channel"] == "#marketing-performance"


def test_post_message_no_webhook_writes_file():
    with patch.dict("os.environ", {"TEAMS_WEBHOOK_URL": ""}, clear=False):
        result = post_message("#marketing-crm", "CRM Title", "CRM body")
    assert result["status"] == "ok"
    assert "path" in result
