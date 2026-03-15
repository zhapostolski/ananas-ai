"""Tests for email delivery via Microsoft Graph API."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch


def _configured_env() -> dict:
    return {
        "GRAPH_TENANT_ID": "test-tenant-id",
        "GRAPH_CLIENT_ID": "test-client-id",
        "GRAPH_REFRESH_TOKEN": "test-refresh-token",
        "EMAIL_FROM_ADDRESS": "zharko.apostolski@ananas.mk",
        "EMAIL_TO_ADDRESS": "zharko.apostolski@ananas.mk",
    }


def test_is_configured_false_when_missing_vars():
    from ananas_ai.email_delivery import is_configured

    with patch.dict("os.environ", {}, clear=True):
        assert not is_configured()


def test_is_configured_true_when_vars_set():
    from ananas_ai.email_delivery import is_configured

    with patch.dict("os.environ", _configured_env(), clear=False):
        assert is_configured()


def test_send_brief_writes_file_when_not_configured():
    from ananas_ai import email_delivery

    with (
        patch.dict("os.environ", {}, clear=True),
        patch.object(
            email_delivery,
            "_write_local",
            return_value={"status": "ok", "path": "/tmp/x.txt"},
        ) as mock_write,
    ):
        result = email_delivery.send_brief("Daily Marketing Brief", "body", today=date(2026, 3, 14))

    mock_write.assert_called_once()
    assert result["status"] == "ok"


def test_send_brief_calls_ses():
    from ananas_ai import email_delivery

    with (
        patch.dict("os.environ", _configured_env(), clear=False),
        patch.object(
            email_delivery,
            "_send_graph",
            return_value={
                "status": "ok",
                "recipients": ["zharko.apostolski@ananas.mk"],
                "provider": "graph",
            },
        ) as mock_send,
    ):
        result = email_delivery.send_brief("Daily Marketing Brief", "body", today=date(2026, 3, 14))

    assert result["status"] == "ok"
    assert result["recipients"] == ["zharko.apostolski@ananas.mk"]
    mock_send.assert_called_once()


def test_send_brief_returns_error_on_ses_failure():
    from ananas_ai import email_delivery

    with (
        patch.dict("os.environ", _configured_env(), clear=False),
        patch.object(email_delivery, "_send_graph", side_effect=Exception("Graph not available")),
        patch.object(
            email_delivery, "_write_local", return_value={"status": "ok", "path": "/tmp/x.txt"}
        ),
    ):
        result = email_delivery.send_brief("Daily Marketing Brief", "body", today=date(2026, 3, 14))

    assert result["status"] == "error"
    assert "Graph not available" in result["error"]


def test_send_brief_subject_includes_date():
    from ananas_ai import email_delivery

    captured = {}

    def fake_write(subject: str, body: str) -> dict:
        captured["subject"] = subject
        return {"status": "ok", "path": "/tmp/x.txt"}

    with (
        patch.dict("os.environ", {}, clear=True),
        patch.object(email_delivery, "_write_local", side_effect=fake_write),
    ):
        email_delivery.send_brief("Daily Marketing Brief", "body", today=date(2026, 3, 14))

    assert "2026-03-14" in captured["subject"]
    assert "Daily Marketing Brief" in captured["subject"]


def test_send_brief_ses_subject_passed_correctly():
    from ananas_ai import email_delivery

    captured = {}

    def fake_send_graph(subject: str, body: str, from_addr: str, to_addrs: list) -> dict:
        captured["subject"] = subject
        captured["from_addr"] = from_addr
        captured["to_addrs"] = to_addrs
        return {"status": "ok", "recipients": to_addrs, "provider": "graph"}

    with (
        patch.dict("os.environ", _configured_env(), clear=False),
        patch.object(email_delivery, "_send_graph", side_effect=fake_send_graph),
    ):
        email_delivery.send_brief("Daily Marketing Brief", "body", today=date(2026, 3, 14))

    assert captured["subject"] == "Daily Marketing Brief -- 2026-03-14"
    assert captured["to_addrs"] == ["zharko.apostolski@ananas.mk"]
    assert captured["from_addr"] == "zharko.apostolski@ananas.mk"


def test_send_brief_multiple_recipients():
    from ananas_ai import email_delivery

    env = {
        **_configured_env(),
        "EMAIL_TO_ADDRESS": "zharko.apostolski@ananas.mk,denis@ananas.mk",
    }

    captured = {}

    def fake_send_graph(subject: str, body: str, from_addr: str, to_addrs: list) -> dict:
        captured["to_addrs"] = to_addrs
        return {"status": "ok", "recipients": to_addrs, "provider": "graph"}

    with (
        patch.dict("os.environ", env, clear=False),
        patch.object(email_delivery, "_send_graph", side_effect=fake_send_graph),
    ):
        result = email_delivery.send_brief("Brief", "body", today=date(2026, 3, 14))

    assert result["recipients"] == ["zharko.apostolski@ananas.mk", "denis@ananas.mk"]
