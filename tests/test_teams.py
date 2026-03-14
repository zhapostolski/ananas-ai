"""Tests for Teams delivery stub — verifies output without real Graph API."""

from __future__ import annotations

from ananas_ai.teams import post_message


def test_post_message_returns_ok():
    result = post_message("#marketing-performance", "Test Title", "Test body")
    assert result["status"] == "ok"
    assert result["channel"] == "#marketing-performance"


def test_post_message_crm_channel():
    result = post_message("#marketing-crm", "CRM Title", "CRM body")
    assert result["status"] == "ok"
    assert "path" in result
