"""Tests for email delivery via AWS SES."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch


def _configured_env() -> dict:
    return {
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

    mock_ses = MagicMock()
    mock_ses.send_email.return_value = {"MessageId": "test-msg-id-123"}

    mock_boto3 = MagicMock()
    mock_boto3.client.return_value = mock_ses

    with (
        patch.dict("os.environ", _configured_env(), clear=False),
        patch.dict("sys.modules", {"boto3": mock_boto3}),
    ):
        result = email_delivery.send_brief("Daily Marketing Brief", "body", today=date(2026, 3, 14))

    assert result["status"] == "ok"
    assert result["message_id"] == "test-msg-id-123"
    assert result["recipients"] == ["zharko.apostolski@ananas.mk"]
    mock_ses.send_email.assert_called_once()


def test_send_brief_returns_error_on_ses_failure():
    from ananas_ai import email_delivery

    mock_boto3 = MagicMock()
    mock_boto3.client.side_effect = Exception("SES not available")

    with (
        patch.dict("os.environ", _configured_env(), clear=False),
        patch.dict("sys.modules", {"boto3": mock_boto3}),
        patch.object(
            email_delivery, "_write_local", return_value={"status": "ok", "path": "/tmp/x.txt"}
        ),
    ):
        result = email_delivery.send_brief("Daily Marketing Brief", "body", today=date(2026, 3, 14))

    assert result["status"] == "error"
    assert "SES not available" in result["error"]


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

    mock_ses = MagicMock()
    mock_ses.send_email.return_value = {"MessageId": "abc"}
    mock_boto3 = MagicMock()
    mock_boto3.client.return_value = mock_ses

    with (
        patch.dict("os.environ", _configured_env(), clear=False),
        patch.dict("sys.modules", {"boto3": mock_boto3}),
    ):
        email_delivery.send_brief("Daily Marketing Brief", "body", today=date(2026, 3, 14))

    call_kwargs = mock_ses.send_email.call_args[1]
    assert call_kwargs["Message"]["Subject"]["Data"] == "Daily Marketing Brief -- 2026-03-14"
    assert call_kwargs["Destination"]["ToAddresses"] == ["zharko.apostolski@ananas.mk"]
    assert call_kwargs["Source"] == "zharko.apostolski@ananas.mk"


def test_send_brief_multiple_recipients():
    from ananas_ai import email_delivery

    env = {
        "EMAIL_FROM_ADDRESS": "zharko.apostolski@ananas.mk",
        "EMAIL_TO_ADDRESS": "zharko.apostolski@ananas.mk,denis@ananas.mk",
    }
    mock_ses = MagicMock()
    mock_ses.send_email.return_value = {"MessageId": "abc"}
    mock_boto3 = MagicMock()
    mock_boto3.client.return_value = mock_ses

    with (
        patch.dict("os.environ", env, clear=False),
        patch.dict("sys.modules", {"boto3": mock_boto3}),
    ):
        result = email_delivery.send_brief("Brief", "body", today=date(2026, 3, 14))

    assert result["recipients"] == ["zharko.apostolski@ananas.mk", "denis@ananas.mk"]
