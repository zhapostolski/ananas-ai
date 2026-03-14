#!/usr/bin/env python3
"""Transcribe a meeting recording — thin shim over ananas_ai.transcribe_meeting.

Usage:
    python scripts/transcribe_meeting.py recording.mp3
    python scripts/transcribe_meeting.py recording.m4a --title "Weekly Marketing Sync" --post
    ananas-ai-transcribe recording.mp3 --post  # preferred CLI form once installed

Supported transcription models (--model flag):
    gpt-4o-transcribe        (default, best accuracy)
    gpt-4o-mini-transcribe   (cheaper, faster)
    whisper-1                (original Whisper model)

Supported audio formats: .mp3 .m4a .mp4 .wav .webm .ogg .oga .flac
Max file size: 25 MB (OpenAI API limit)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the package is importable when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ananas_ai.transcribe_meeting import main

if __name__ == "__main__":
    main()
