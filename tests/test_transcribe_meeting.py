"""Tests for ananas_ai.transcribe_meeting."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ananas_ai import transcribe_meeting as tm


def _mock_openai_module(transcription_result: str = "Hello transcript") -> MagicMock:
    """Return a fake openai module with a pre-configured transcription response."""
    mock_client = MagicMock()
    mock_client.audio.transcriptions.create.return_value = transcription_result
    mock_openai = MagicMock()
    mock_openai.OpenAI.return_value = mock_client
    return mock_openai


def _mock_anthropic_module(summary_text: str = "## Summary\nDecisions made.") -> MagicMock:
    """Return a fake anthropic module with a pre-configured message response."""
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = summary_text

    mock_msg = MagicMock()
    mock_msg.content = [mock_block]
    mock_msg.usage.input_tokens = 100
    mock_msg.usage.output_tokens = 50

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_msg

    mock_anthropic = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client
    return mock_anthropic


# ── validate_file ─────────────────────────────────────────────────────────────


def test_validate_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        tm.validate_file(tmp_path / "missing.mp3")


def test_validate_file_unsupported_format(tmp_path: Path) -> None:
    f = tmp_path / "audio.avi"
    f.write_bytes(b"x")
    with pytest.raises(SystemExit):
        tm.validate_file(f)


def test_validate_file_too_large(tmp_path: Path) -> None:
    f = tmp_path / "big.mp3"
    f.write_bytes(b"0" * (26 * 1024 * 1024))
    with pytest.raises(SystemExit):
        tm.validate_file(f)


def test_validate_file_ok(tmp_path: Path) -> None:
    f = tmp_path / "meeting.mp3"
    f.write_bytes(b"audio_data")
    tm.validate_file(f)  # should not raise


def test_validate_file_m4a_ok(tmp_path: Path) -> None:
    f = tmp_path / "recording.m4a"
    f.write_bytes(b"audio_data")
    tm.validate_file(f)  # should not raise


# ── transcribe ────────────────────────────────────────────────────────────────


def test_transcribe_calls_api_with_model(tmp_path: Path) -> None:
    audio = tmp_path / "meeting.mp3"
    audio.write_bytes(b"fake audio")

    mock_openai = _mock_openai_module("Hello world transcript")
    mock_client = mock_openai.OpenAI.return_value

    with (
        patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}),
        patch.dict("sys.modules", {"openai": mock_openai}),
    ):
        result = tm.transcribe(audio, model="gpt-4o-transcribe")

    assert result == "Hello world transcript"
    mock_client.audio.transcriptions.create.assert_called_once()
    call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
    assert call_kwargs["model"] == "gpt-4o-transcribe"
    assert call_kwargs["response_format"] == "text"


def test_transcribe_uses_default_model(tmp_path: Path) -> None:
    audio = tmp_path / "meeting.mp3"
    audio.write_bytes(b"fake audio")

    mock_openai = _mock_openai_module()
    mock_client = mock_openai.OpenAI.return_value

    with (
        patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}),
        patch.dict("sys.modules", {"openai": mock_openai}),
    ):
        tm.transcribe(audio)

    call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
    assert call_kwargs["model"] == tm.DEFAULT_TRANSCRIPTION_MODEL


def test_transcribe_exits_without_api_key(tmp_path: Path) -> None:
    audio = tmp_path / "meeting.mp3"
    audio.write_bytes(b"fake audio")

    with (
        patch.dict("os.environ", {}, clear=True),
        patch.dict("sys.modules", {"openai": _mock_openai_module()}),
        pytest.raises(SystemExit),
    ):
        tm.transcribe(audio)


def test_transcribe_mini_model(tmp_path: Path) -> None:
    audio = tmp_path / "meeting.mp3"
    audio.write_bytes(b"fake audio")

    mock_openai = _mock_openai_module("transcript via mini")
    mock_client = mock_openai.OpenAI.return_value

    with (
        patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}),
        patch.dict("sys.modules", {"openai": mock_openai}),
    ):
        result = tm.transcribe(audio, model="gpt-4o-mini-transcribe")

    assert result == "transcript via mini"
    call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
    assert call_kwargs["model"] == "gpt-4o-mini-transcribe"


# ── summarise ─────────────────────────────────────────────────────────────────


def test_summarise_uses_claude_when_key_present() -> None:
    mock_anthropic = _mock_anthropic_module("## Summary\nDecisions made.")
    mock_client = mock_anthropic.Anthropic.return_value

    with (
        patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test"}),
        patch.dict("sys.modules", {"anthropic": mock_anthropic}),
    ):
        result = tm.summarise("Transcript text", "Weekly Sync", "2026-03-14")

    assert "Summary" in result
    mock_client.messages.create.assert_called_once()


def test_summarise_falls_back_to_openai_when_no_anthropic_key() -> None:
    mock_choice = MagicMock()
    mock_choice.message.content = "GPT summary"
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_resp

    mock_openai = MagicMock()
    mock_openai.OpenAI.return_value = mock_client

    with (
        patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}, clear=True),
        patch.dict("sys.modules", {"openai": mock_openai}),
    ):
        result = tm.summarise("Transcript text", "Weekly Sync", "2026-03-14")

    assert result == "GPT summary"
    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args[1]
    assert call_args["model"] == "gpt-4.1"


def test_summarise_truncates_long_transcript() -> None:
    long_transcript = "word " * 10_000  # ~50k chars

    mock_anthropic = _mock_anthropic_module("Summary")
    mock_client = mock_anthropic.Anthropic.return_value

    with (
        patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test"}),
        patch.dict("sys.modules", {"anthropic": mock_anthropic}),
    ):
        tm.summarise(long_transcript, "Long Meeting", "2026-03-14")

    call_kwargs = mock_client.messages.create.call_args[1]
    user_content = call_kwargs["messages"][0]["content"]
    # The truncated transcript (40k) + header text must be shorter than raw transcript
    assert len(user_content) < len(long_transcript)


# ── save_transcript ───────────────────────────────────────────────────────────


def test_save_transcript_creates_file(tmp_path: Path) -> None:
    audio = tmp_path / "my_meeting.mp3"
    audio.write_bytes(b"data")

    with patch.object(tm, "RAW_DIR", tmp_path / "raw"), patch.object(tm, "ROOT", tmp_path):
        out = tm.save_transcript("Hello transcript", audio, "2026-03-14")

    assert out.exists()
    content = out.read_text()
    assert "Hello transcript" in content
    assert "2026-03-14" in content
    assert "my_meeting" in out.name


def test_save_transcript_replaces_spaces_in_stem(tmp_path: Path) -> None:
    audio = tmp_path / "my meeting file.mp3"
    audio.write_bytes(b"data")

    with patch.object(tm, "RAW_DIR", tmp_path / "raw"), patch.object(tm, "ROOT", tmp_path):
        out = tm.save_transcript("transcript", audio, "2026-03-14")

    assert " " not in out.name


def test_save_transcript_header_format(tmp_path: Path) -> None:
    audio = tmp_path / "weekly_sync.mp3"
    audio.write_bytes(b"data")

    with patch.object(tm, "RAW_DIR", tmp_path / "raw"), patch.object(tm, "ROOT", tmp_path):
        out = tm.save_transcript("Actual transcript text", audio, "2026-03-14")

    content = out.read_text()
    assert content.startswith("# Meeting Transcript:")
    assert "Actual transcript text" in content


# ── DEFAULT_TRANSCRIPTION_MODEL ───────────────────────────────────────────────


def test_default_model_is_gpt4o_transcribe() -> None:
    assert tm.DEFAULT_TRANSCRIPTION_MODEL == "gpt-4o-transcribe"
