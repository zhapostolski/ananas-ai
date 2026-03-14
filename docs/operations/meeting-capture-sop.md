# Meeting Capture SOP

Phase 1 meetings are physical. This SOP covers how to record and process them into structured summaries via the AI platform. Full automation (meeting-intelligence-agent) is Phase 2 — this SOP covers the manual-assisted workflow available today.

## What you need

- A phone or laptop microphone to record the meeting
- Access to the `/context/ananas/raw/` folder in the repo (or an S3 drop folder once configured)
- The Ananas AI Platform running (EC2 or local)

## Step-by-step

### 1. Record the meeting
- Use your phone's voice memo app, or any recording tool available
- Record the full meeting or the key decision/discussion portion
- Save as `.mp3` or `.m4a` — keep file size under 25MB for API compatibility

### 2. Transcribe
- Upload the recording to a transcription tool:
  - **Free**: [OpenAI Whisper](https://whisper.openai.com) (web) or run `whisper audio.mp3` locally if installed
  - **Paid/built-in**: Microsoft Teams transcription (when Teams meetings are introduced)
- Save the transcript as a `.txt` file

### 3. Drop the transcript into the intake folder
```bash
cp meeting_transcript.txt /path/to/ananas-ai/context/ananas/raw/
```
The `watch_context.py` watcher will automatically pick it up, call Claude, and update `context/ananas/ananas-overview.md`.

### 4. Manual summary (until meeting-intelligence-agent is live)
Until Phase 2, use the CLI to generate a structured summary:
```bash
# Activate venv
source .venv/bin/activate

# Run the context watcher manually against the file
python scripts/watch_context.py --file context/ananas/raw/meeting_transcript.txt
```

### 5. Post to Teams
Once the summary is generated, post it to the relevant Teams channel manually or via:
```bash
python -m ananas_ai.cli run-agent marketing-ops-agent  # if ops-related
```

### 6. Archive
- Move the raw recording and transcript to a SharePoint folder: `Marketing / AI Platform / Meeting Archives / YYYY-MM/`
- Name files: `YYYYMMDD_meeting_topic.mp3` and `YYYYMMDD_meeting_topic.txt`

## Phase 2 plan (meeting-intelligence-agent)
When the meeting-intelligence-agent is built, this process will be fully automated:
- Drop `.mp3` or `.m4a` into S3 intake bucket
- Agent transcribes (Whisper API), extracts action items, updates Confluence, posts Teams summary, creates Jira tasks
- No manual steps required

## Tips
- Even 10-minute recordings of decision meetings are valuable — the agent extracts action items and decisions, not just summaries
- If you can't record, write bullet notes immediately after and drop those into the intake folder instead — the watcher handles `.txt` files too
