"""Meeting transcription and summarisation pipeline.

Transcribes a meeting audio file via OpenAI speech-to-text, then generates a
structured summary via Claude (with GPT-4.1 fallback).

Supported transcription models (OpenAI):
  - gpt-4o-transcribe        (default - best accuracy, released March 2025)
  - gpt-4o-mini-transcribe   (cheaper, lower latency)
  - whisper-1                (original Whisper API model, still supported)

Supported audio formats: .mp3 .m4a .mp4 .wav .webm .ogg .oga .flac
Max file size: 25 MB (OpenAI API limit - use ffmpeg to split larger recordings)
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = ROOT / "context" / "ananas" / "raw"

SUPPORTED_FORMATS = {".mp3", ".m4a", ".mp4", ".wav", ".webm", ".ogg", ".oga", ".flac"}
MAX_FILE_SIZE_MB = 25
DEFAULT_TRANSCRIPTION_MODEL = "gpt-4o-transcribe"

SUMMARY_SYSTEM = """You are the Ananas AI meeting intelligence assistant. Ananas is North Macedonia's
largest e-commerce marketplace with an 8-person marketing team.

You receive a raw meeting transcript. Extract and structure the following:

1. **Meeting summary** (2-3 sentences, what was this meeting about)
2. **Key decisions** (bullet list - concrete decisions made)
3. **Action items** (bullet list - what needs to be done, by whom if mentioned, with deadline if mentioned)
4. **Topics discussed** (brief bullet list of main topics)
5. **Blockers / risks** (anything flagged as a problem or risk, if any)
6. **Next steps** (follow-ups or next meeting agenda items, if any)

Format clearly with markdown headers. Be concise - this summary goes to the marketing team in Teams.
If the transcript is unclear or incomplete, note that briefly.
Do NOT invent information not present in the transcript."""


def validate_file(path: Path) -> None:
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        print(
            f"Error: unsupported format '{path.suffix}'. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}",
            file=sys.stderr,
        )
        sys.exit(1)
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        print(
            f"Error: file is {size_mb:.1f}MB - OpenAI limit is {MAX_FILE_SIZE_MB}MB.\n"
            "Tip: split the recording with: ffmpeg -i input.mp3 -t 00:30:00 part1.mp3",
            file=sys.stderr,
        )
        sys.exit(1)


def transcribe(audio_path: Path, model: str = DEFAULT_TRANSCRIPTION_MODEL) -> str:
    """Transcribe audio via OpenAI speech-to-text API. Returns transcript text."""
    import openai  # type: ignore[import]

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set in environment.", file=sys.stderr)
        sys.exit(1)

    client = openai.OpenAI(api_key=api_key)
    size_kb = audio_path.stat().st_size / 1024
    print(f"Transcribing {audio_path.name} ({size_kb:.0f} KB) via {model}...")

    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model=model,
            file=f,
            response_format="text",
        )
    transcript = str(result)
    print(f"Transcription complete - {len(transcript):,} characters.")
    return transcript


def summarise(transcript: str, title: str, date_str: str) -> str:
    """Generate structured meeting summary via Claude (falls back to GPT-4.1)."""
    import anthropic  # type: ignore[import]

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _summarise_openai(transcript, title, date_str)

    client = anthropic.Anthropic(api_key=api_key)
    print("Generating structured summary via Claude...")

    user_content = (
        f"Meeting: {title}\nDate: {date_str}\n\n"
        f"Transcript:\n\n{transcript[:40_000]}\n\n"
        "Generate the structured meeting summary."
    )

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SUMMARY_SYSTEM,
        messages=[{"role": "user", "content": user_content}],
    )
    text_block = next((b for b in msg.content if b.type == "text"), None)
    summary = str(text_block.text) if text_block else ""  # type: ignore[union-attr]
    tokens_used = msg.usage.input_tokens + msg.usage.output_tokens
    print(f"Summary generated - {len(summary):,} characters, {tokens_used:,} tokens.")
    return summary


def _summarise_openai(transcript: str, title: str, date_str: str) -> str:
    """Fallback: generate summary via OpenAI GPT-4.1."""
    import openai  # type: ignore[import]

    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    print("Generating structured summary via GPT-4.1 (Claude fallback)...")

    resp = client.chat.completions.create(
        model="gpt-4.1",
        max_tokens=2048,
        messages=[
            {"role": "system", "content": SUMMARY_SYSTEM},
            {
                "role": "user",
                "content": (
                    f"Meeting: {title}\nDate: {date_str}\n\n"
                    f"Transcript:\n\n{transcript[:40_000]}\n\n"
                    "Generate the structured meeting summary."
                ),
            },
        ],
    )
    return str(resp.choices[0].message.content)


def save_transcript(transcript: str, audio_path: Path, date_str: str) -> Path:
    """Save raw transcript to context/ananas/raw/ for the context watcher."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    safe_stem = audio_path.stem.replace(" ", "_")
    out_path = RAW_DIR / f"{date_str}_{safe_stem}_transcript.txt"
    out_path.write_text(
        f"# Meeting Transcript: {audio_path.stem}\nDate: {date_str}\n\n{transcript}",
        encoding="utf-8",
    )
    print(f"Transcript saved: {out_path.relative_to(ROOT)}")
    return out_path


def post_to_teams(summary: str, title: str) -> None:
    """Post summary to Teams #marketing-summary channel."""
    from ananas_ai.teams import post_message

    result = post_message("#marketing-summary", f"Meeting Summary: {title}", summary)
    if result.get("status") == "ok":
        print("Posted to Teams #marketing-summary.")
    else:
        print(f"Teams post failed: {result.get('error', 'unknown error')}", file=sys.stderr)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Transcribe a meeting recording and generate a structured summary.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  ananas-ai-transcribe recording.mp3\n"
            "  ananas-ai-transcribe recording.m4a --title 'Weekly Marketing Sync' --post\n"
            "  ananas-ai-transcribe recording.mp3 --model gpt-4o-mini-transcribe\n"
        ),
    )
    parser.add_argument("audio_file", help="Path to audio file (.mp3, .m4a, .wav, etc.)")
    parser.add_argument(
        "--title", default="", help="Meeting title (default: derived from filename)"
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_TRANSCRIPTION_MODEL,
        choices=["gpt-4o-transcribe", "gpt-4o-mini-transcribe", "whisper-1"],
        help=f"OpenAI transcription model (default: {DEFAULT_TRANSCRIPTION_MODEL})",
    )
    parser.add_argument(
        "--post",
        action="store_true",
        help="Post summary to Teams #marketing-summary after generating",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save transcript to context/ananas/raw/",
    )
    args = parser.parse_args()

    audio_path = Path(args.audio_file).resolve()
    validate_file(audio_path)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    title = args.title or audio_path.stem.replace("_", " ").replace("-", " ").title()

    print(f"\n=== Meeting: {title} | {date_str} ===\n")

    transcript = transcribe(audio_path, model=args.model)

    if not args.no_save:
        save_transcript(transcript, audio_path, date_str)

    summary = summarise(transcript, title, date_str)

    print(f"\n{'=' * 60}")
    print(f"MEETING SUMMARY: {title}")
    print(f"{'=' * 60}\n")
    print(summary)
    print(f"\n{'=' * 60}\n")

    if args.post:
        post_to_teams(summary, title)


if __name__ == "__main__":
    main()
