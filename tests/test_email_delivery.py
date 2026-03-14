"""Tests for email delivery -- verifies Graph API calls and fallback behaviour."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch


def _configured_env() -> dict:
    return {
        "TEAMS_CLIENT_ID": "test-client-id",
        "TEAMS_CLIENT_SECRET": "test-secret",
        "TEAMS_TENANT_ID": "test-tenant",
        "OUTLOOK_FROM_ADDRESS": "noreply@ananas.mk",
        "OUTLOOK_TO_ADDRESS": "zharko.apostolski@ananas.mk",
    }


def test_is_configured_false_when_missing_vars():
    from ananas_ai.email_delivery import is_configured

    with patch.dict("os.environ", {}, clear=True):
        assert not is_configured()


def test_is_configured_true_when_all_vars_set():
    from ananas_ai.email_delivery import is_configured

    with patch.dict("os.environ", _configured_env(), clear=False):
        assert is_configured()


def test_send_brief_writes_file_when_not_configured(tmp_path):
    from ananas_ai import email_delivery

    with (
        patch.dict("os.environ", {}, clear=True),
        patch.object(email_delivery, "_write_local", return_value={"status": "ok", "path": str(tmp_path / "x.txt")}) as mock_write,
    ):
        result = email_delivery.send_brief("Daily Marketing Brief", "body text", today=date(2026, 3, 14))

    mock_write.assert_called_once()
    assert result["status"] == "ok"


def test_send_brief_posts_to_graph_api():
    from ananas_ai import email_delivery

    mock_token_resp = MagicMock()
    mock_token_resp.json.return_value = {"access_token": "test-token"}
    mock_token_resp.raise_for_status = MagicMock()

    mock_send_resp = MagicMock()
    mock_send_resp.status_code = 202
    mock_send_resp.raise_for_status = MagicMock()

    mock_requests = MagicMock()
    mock_requests.post.side_effect = [mock_token_resp, mock_send_resp]

    with (
        patch.dict("os.environ", _configured_env(), clear=False),
        patch.dict("sys.modules", {"requests": mock_requests}),
    ):
        result = email_delivery.send_brief("Daily Marketing Brief", "body text", today=date(2026, 3, 14))

    assert result["status"] == "ok"
    assert result["http_status"] == 202
    assert result["recipients"] == ["zharko.apostolski@ananas.mk"]


def test_send_brief_returns_error_on_api_failure():
    from ananas_ai import email_delivery

    mock_requests = MagicMock()
    mock_requests.post.side_effect = Exception("connection refused")

    with (
        patch.dict("os.environ", _configured_env(), clear=False),
        patch.dict("sys.modules", {"requests": mock_requests}),
        patch.object(email_delivery, "_write_local", return_value={"status": "ok", "path": "/tmp/x.txt"}),
    ):
        result = email_delivery.send_brief("Daily Marketing Brief", "body text", today=date(2026, 3, 14))

    assert result["status"] == "error"
    assert "connection refused" in result["error"]


def test_send_brief_subject_includes_date():
    from ananas_ai import email_delivery

    captured = {}

    def fake_write_local(subject: str, body: str) -> dict:
        captured["subject"] = subject
        return {"status": "ok", "path": "/tmp/x.txt"}

    with (
        patch.dict("os.environ", {}, clear=True),
        patch.object(email_delivery, "_write_local", side_effect=fake_write_local),
    ):
        email_delivery.send_brief("Daily Marketing Brief", "body", today=date(2026, 3, 14))

    assert "2026-03-14" in captured["subject"]
    assert "Daily Marketing Brief" in captured["subject"]


def test_send_brief_multiple_recipients_split_correctly():
    from ananas_ai import email_delivery

    recipients_used = []

    def fake_build_payload(subject, body, to_addresses):
        recipients_used.extend(to_addresses)
        return {"message": {}}

    mock_token_resp = MagicMock()
    mock_token_resp.json.return_value = {"access_token": "tok"}
    mock_token_resp.raise_for_status = MagicMock()

    mock_send_resp = MagicMock()
    mock_send_resp.status_code = 202
    mock_send_resp.raise_for_status = MagicMock()

    mock_requests = MagicMock()
    mock_requests.post.side_effect = [mock_token_resp, mock_send_resp]

    with (
        patch.dict("os.environ", _configured_env(), clear=False),
        patch.dict("sys.modules", {"requests": mock_requests}),
        patch.object(email_delivery, "_build_payload", side_effect=fake_build_payload),
    ):
        email_delivery.send_brief("Brief", "body", today=date(2026, 3, 14))

    assert recipients_used == ["zharko.apostolski@ananas.mk"]
