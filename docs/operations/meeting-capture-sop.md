# Meeting Capture SOP

Phase 1 meetings are physical. This SOP covers how to record and process them into structured summaries via the AI platform. Full automation (meeting-intelligence-agent) is Phase 2 — this SOP covers the script-assisted workflow available today.

## What you need

- A phone or laptop to record the meeting
- The Ananas AI Platform installed (`pip install -e .` in the repo)
- `OPENAI_API_KEY` and (optional) `ANTHROPIC_API_KEY` set in your `.env`

## Step-by-step

### 1. Record the meeting
- Use your phone's voice memo app, or any recording tool available
- Record the full meeting or the key decision/discussion portion
- Save as `.mp3` or `.m4a` — keep file size under 25 MB for API compatibility
- Tip: even a 10-minute recording of a decision meeting is valuable

### 2. Run the transcribe command
```bash
# Activate venv
source .venv/bin/activate

# Transcribe + generate structured summary (default: gpt-4o-transcribe model)
ananas-ai-transcribe recording.mp3

# With custom title and auto-post to Teams #marketing-summary
ananas-ai-transcribe recording.m4a --title "Weekly Marketing Sync" --post

# Faster / cheaper model (lower accuracy)
ananas-ai-transcribe recording.mp3 --model gpt-4o-mini-transcribe

# Don't save transcript to context/ folder
ananas-ai-transcribe recording.mp3 --no-save
```

**What happens automatically:**
1. Audio is transcribed via OpenAI `gpt-4o-transcribe` (best accuracy) or your chosen `--model`
2. Structured summary (decisions, actions, blockers, next steps) is generated via Claude Sonnet
3. Raw transcript is saved to `context/ananas/raw/` — the context watcher picks it up
4. Summary is printed to the terminal
5. With `--post`: summary is posted to Teams `#marketing-summary`

### Transcription model options

| Model | Quality | Cost | Use when |
|---|---|---|---|
| `gpt-4o-transcribe` | Best | ~$0.006/min | Standard (default) |
| `gpt-4o-mini-transcribe` | Good | ~$0.003/min | Quick notes, budget-sensitive |
| `whisper-1` | Good | ~$0.006/min | Fallback if newer models unavailable |

### 3. Review the summary
The structured summary is printed with:
- Meeting summary (2–3 sentences)
- Key decisions
- Action items (with owner + deadline if mentioned)
- Topics discussed
- Blockers / risks
- Next steps

### 4. Post to Teams (if not using --post)
If you didn't use `--post`, copy the summary to the relevant Teams channel manually, or run:
```bash
ananas-ai run-agent marketing-ops-agent  # for ops-related meetings
```

### 5. Archive
- Move the raw recording to SharePoint: `Marketing / AI Platform / Meeting Archives / YYYY-MM/`
- Naming: `YYYYMMDD_meeting_topic.mp3`
- The transcript is auto-saved to `context/ananas/raw/` — no manual step needed

## Splitting large recordings

If your file is over 25 MB, split it with ffmpeg:
```bash
# Split into 30-minute chunks
ffmpeg -i full_meeting.mp3 -t 00:30:00 part1.mp3
ffmpeg -i full_meeting.mp3 -ss 00:30:00 part2.mp3

# Then transcribe each part
ananas-ai-transcribe part1.mp3 --no-save
ananas-ai-transcribe part2.mp3 --post
```

## Phase 2 plan (meeting-intelligence-agent)

When the meeting-intelligence-agent is built, this process will be fully automated:
- Drop `.mp3` or `.m4a` into S3 intake bucket
- Agent transcribes (Whisper API), extracts action items, updates Confluence, posts Teams summary, creates Jira tasks
- No manual steps required

## Tips
- If you can't record, write bullet notes immediately after and drop those into `context/ananas/raw/` as a `.txt` file — the watcher handles those too
- Transcription is charged per minute of audio — a 1-hour meeting costs ~$0.36 with `gpt-4o-transcribe`
- The `--no-save` flag is useful when testing or when the meeting content is sensitive
