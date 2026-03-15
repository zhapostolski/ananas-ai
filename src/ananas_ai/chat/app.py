"""
Ananas AI Chat - FastAPI app with Entra ID auth and streaming Claude responses.
Stores all conversations in PostgreSQL for analytics and audit.
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone

import anthropic
import httpx
import msal
from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from itsdangerous import BadSignature, URLSafeTimedSerializer
from pydantic import BaseModel

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
AZURE_CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
AZURE_CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]
AZURE_TENANT_ID = os.environ["AZURE_TENANT_ID"]
AZURE_REDIRECT_URI = os.environ["AZURE_REDIRECT_URI"]
SESSION_SECRET = os.environ["SESSION_SECRET"]
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
DB_PATH = os.environ.get(
    "ANANAS_DB_PATH",
    str(__import__("pathlib").Path(__file__).resolve().parents[4] / "ananas_ai.db"),
)

AUTHORITY = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}"
SCOPES = ["User.Read"]

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------
app = FastAPI(title="Ananas AI Chat")
signer = URLSafeTimedSerializer(SESSION_SECRET)
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ---------------------------------------------------------------------------
# MSAL helper
# ---------------------------------------------------------------------------
def _msal_app() -> msal.ConfidentialClientApplication:
    return msal.ConfidentialClientApplication(
        AZURE_CLIENT_ID,
        authority=AUTHORITY,
        client_credential=AZURE_CLIENT_SECRET,
    )


# ---------------------------------------------------------------------------
# Session helpers (signed cookie, no server state)
# ---------------------------------------------------------------------------
def _set_session(response, data: dict) -> None:
    token = signer.dumps(data)
    response.set_cookie("session", token, httponly=True, samesite="lax", max_age=86400 * 7)


def _get_session(session: str | None) -> dict[str, str] | None:
    if not session:
        return None
    try:
        data = signer.loads(session, max_age=86400 * 7)
        return dict(data) if isinstance(data, dict) else None
    except BadSignature:
        return None


# ---------------------------------------------------------------------------
# Database (SQLite - same DB as agents)
# ---------------------------------------------------------------------------
def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_tables():
    with _db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS chat_conversations (
                id          TEXT PRIMARY KEY,
                session_id  TEXT NOT NULL,
                user_id     TEXT NOT NULL,
                user_name   TEXT NOT NULL,
                user_email  TEXT NOT NULL,
                role        TEXT NOT NULL,
                content     TEXT NOT NULL,
                created_at  TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_chat_session
                ON chat_conversations(session_id, created_at);
            CREATE INDEX IF NOT EXISTS idx_chat_user
                ON chat_conversations(user_id, created_at);
        """)


def _save_message(session_id: str, user: dict, role: str, content: str):
    with _db() as conn:
        conn.execute(
            """
            INSERT INTO chat_conversations
                (id, session_id, user_id, user_name, user_email, role, content, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                str(uuid.uuid4()),
                session_id,
                user["id"],
                user["name"],
                user["email"],
                role,
                content,
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def _load_history(session_id: str) -> list[dict]:
    with _db() as conn:
        rows = conn.execute(
            """
            SELECT role, content FROM chat_conversations
            WHERE session_id = ?
            ORDER BY created_at ASC
        """,
            (session_id,),
        ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are the Ananas AI assistant - an internal intelligence tool for the Ananas marketing team.

You have deep knowledge of the Ananas platform:
- Ananas is a marketplace in North Macedonia with 250k+ products
- The team is 8 people: 2 designers, 3 performance marketers, 1 content/social, 1 CRM, 1 TBD
- Critical issues: Trustpilot rating 2.0 (unclaimed), zero Google Shopping campaigns, heavy coupon dependency
- Active AI agents: performance, crm-lifecycle, reputation, marketing-ops, cross-channel-brief (run daily)
- Phase 2 agents planned: product-feed, promo-simulator, customer-segmentation, category-growth, competitor-intelligence, and more
- Infrastructure: AWS EC2, PostgreSQL, Teams for comms, Claude Sonnet as default model
- Key metrics: POAS >3.0, contribution margin >18%, cart abandonment <65%, Trustpilot response rate 100%
- GA4 live: 464k sessions, 215k users, €13.4M revenue (as of 2026-03-13)

You help the team with:
- Understanding agent outputs and KPIs
- Marketing strategy and campaign analysis
- Platform decisions and architecture questions
- Interpreting data and identifying opportunities
- Anything else the team needs

Be concise, direct, and business-focused. You know this team and their context well."""


# ---------------------------------------------------------------------------
# Routes - Auth
# ---------------------------------------------------------------------------
@app.get("/auth/login")
async def login(request: Request, session: str | None = Cookie(default=None)):
    if _get_session(session):
        return RedirectResponse("/")
    flow = _msal_app().initiate_auth_code_flow(SCOPES, redirect_uri=AZURE_REDIRECT_URI)
    response = RedirectResponse(flow["auth_uri"])
    response.set_cookie("auth_flow", signer.dumps(flow), httponly=True, samesite="lax", max_age=600)
    return response


@app.get("/auth/callback")
async def auth_callback(request: Request, auth_flow: str | None = Cookie(default=None)):
    if not auth_flow:
        raise HTTPException(400, "Missing auth flow cookie")
    try:
        flow = signer.loads(auth_flow, max_age=600)
    except BadSignature as exc:
        raise HTTPException(400, "Invalid auth flow") from exc

    result = _msal_app().acquire_token_by_auth_code_flow(flow, dict(request.query_params))
    if "error" in result:
        raise HTTPException(401, f"Auth failed: {result.get('error_description', result['error'])}")

    # Fetch user profile from Microsoft Graph
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {result['access_token']}"},
        )
        profile = resp.json()

    user = {
        "id": profile.get("id"),
        "name": profile.get("displayName"),
        "email": profile.get("mail") or profile.get("userPrincipalName"),
    }

    response = RedirectResponse("/")
    _set_session(response, user)
    response.delete_cookie("auth_flow")
    return response


@app.get("/auth/logout")
async def logout():
    response = RedirectResponse("/")
    response.delete_cookie("session")
    return response


# ---------------------------------------------------------------------------
# Routes - Chat
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index(session: str | None = Cookie(default=None)):
    user = _get_session(session)
    if not user:
        return RedirectResponse("/auth/login")
    return HTMLResponse(_render_ui(user))


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


@app.post("/chat")
async def chat(req: ChatRequest, session: str | None = Cookie(default=None)):
    user = _get_session(session)
    if not user:
        raise HTTPException(401, "Not authenticated")

    session_id = req.session_id or str(uuid.uuid4())
    history = _load_history(session_id)

    # Save user message
    _save_message(session_id, user, "user", req.message)

    # Build messages for Claude
    messages = history + [{"role": "user", "content": req.message}]

    async def stream():
        yield json.dumps({"session_id": session_id}) + "\n"
        full_response = []
        try:
            with claude.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    full_response.append(text)
                    yield json.dumps({"text": text}) + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"
            return

        # Save assistant response
        _save_message(session_id, user, "assistant", "".join(full_response))
        yield json.dumps({"done": True}) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")


@app.get("/chat/history")
async def history(session_id: str, session: str | None = Cookie(default=None)):
    user = _get_session(session)
    if not user:
        raise HTTPException(401, "Not authenticated")
    return {"messages": _load_history(session_id)}


@app.get("/me")
async def me(session: str | None = Cookie(default=None)):
    user = _get_session(session)
    if not user:
        raise HTTPException(401, "Not authenticated")
    return user


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
ANANAS_LOGO_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="39" viewBox="0 0 124 48" fill="none"><path d="M8.402 32.394c-2.414 0-3.67-.872-3.67-2.617 0-2.035 1.449-2.908 4.539-2.908h3.477c.193 0 .29.097.29.291v1.648c0 2.423-1.642 3.586-4.636 3.586zm8.885 3.586c.29 0 .483-.194.483-.485v-13.86c0-5.234-2.414-7.463-8.885-7.463-3.477 0-5.794.872-7.533 2.035-.193.097-.193.388-.097.582l1.642 2.908c.097.194.386.291.579.097.966-.775 2.511-1.454 4.829-1.454 3.573 0 4.732 1.066 4.732 3.489v.969c0 .194-.097.291-.29.291H8.498C3.283 23.09 0 25.222 0 29.874c0 4.459 3.283 6.494 7.146 6.494 2.994 0 5.022-.969 5.988-2.52v1.551c0 .291.193.485.483.485h3.67v.097zm22.017.001c.29 0 .483-.194.483-.485V22.12c0-4.555-2.801-7.948-7.34-7.948-2.801 0-4.636 1.163-5.601 2.52v-1.551c0-.291-.193-.485-.483-.485H22.21c-.29 0-.483.194-.483.485v20.451c0 .291.193.485.483.485h4.056c.29 0 .483-.194.483-.485V23.283c0-2.714 1.449-4.652 4.056-4.652s3.959 1.939 3.959 4.653v12.31c0 .291.193.485.483.485h4.056v-.097zm11.783-3.587c-2.414 0-3.67-.872-3.67-2.617 0-2.035 1.449-2.908 4.539-2.908h3.477c.193 0 .29.097.29.291v1.648c.097 2.423-1.545 3.586-4.635 3.586zm8.981 3.586c.29 0 .483-.194.483-.485v-13.86c0-5.234-2.414-7.463-8.885-7.463-3.477 0-5.794.872-7.533 2.035-.193.097-.193.388-.096.582l1.642 2.908c.097.194.386.291.58.097.966-.775 2.511-1.454 4.829-1.454 3.573 0 4.732 1.066 4.732 3.489v.969c0 .194-.097.291-.29.291h-4.346c-5.215 0-8.498 2.132-8.498 6.785 0 4.459 3.284 6.494 7.147 6.494 2.994 0 5.022-.969 5.987-2.52v1.551c0 .291.193.485.483.485h3.766v.097zm21.923.001c.29 0 .483-.194.483-.485V22.12c0-4.555-2.801-7.948-7.34-7.948-2.801 0-4.635 1.163-5.601 2.52v-1.551c0-.291-.193-.485-.483-.485h-4.056c-.29 0-.483.194-.483.485v20.451c0 .291.193.485.483.485h4.056c.29 0 .483-.194.483-.485V23.283c0-2.714 1.449-4.652 4.056-4.652s3.96 1.939 3.96 4.653v12.31c0 .291.193.485.483.485h3.959v-.097zm11.879-3.587c-2.414 0-3.67-.872-3.67-2.617 0-2.035 1.449-2.908 4.539-2.908h3.477c.193 0 .29.097.29.291v1.648c0 2.423-1.642 3.586-4.635 3.586zm8.885 3.586c.29 0 .483-.194.483-.485v-13.86c0-5.234-2.414-7.463-8.885-7.463-3.477 0-5.794.872-7.533 2.035-.193.097-.193.388-.097.582l1.642 2.908c.096.194.386.291.579.097.966-.775 2.511-1.454 4.829-1.454 3.573 0 4.732 1.066 4.732 3.489v.969c0 .194-.096.291-.29.291H93.87c-5.215 0-8.498 2.132-8.498 6.785 0 4.459 3.284 6.494 7.146 6.494 2.994 0 5.022-.969 5.987-2.52v1.551c0 .291.193.485.483.485h3.766v.097zm12.36.485c5.794 0 8.885-3.005 8.885-7.172 0-3.489-2.125-5.816-6.567-6.203l-2.318-.194c-2.704-.291-3.477-.969-3.477-2.229s1.063-2.229 3.187-2.229 4.249.872 5.505 1.745c.193.097.483.097.579-.097l2.125-2.617c.097-.194.097-.485-.097-.582-1.931-1.551-4.635-2.617-8.015-2.617-5.312 0-8.209 2.617-8.209 6.688 0 3.586 2.221 5.816 6.471 6.3l2.317.194c2.801.291 3.477 1.066 3.477 2.326 0 1.454-1.352 2.52-3.96 2.52-2.221 0-4.635-.969-6.18-2.423-.193-.194-.483-.194-.58 0l-2.511 2.617c-.193.194-.193.485 0 .581 2.028 1.648 5.022 3.392 9.368 3.392z" fill="#fe502a"/><path d="M1.642 11.362h15.741c.29 0 .483-.194.483-.485V7.485c0-.291-.193-.485-.483-.485H1.642c-.29 0-.483.194-.483.485v3.489c0 .194.193.388.483.388z" fill="#84bd00"/></svg>'


def _render_ui(user: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ananas AI</title>
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Open Sans', -apple-system, sans-serif; background: #f6f8f9; height: 100vh; display: flex; flex-direction: column; }}

  /* Header */
  header {{
    background: #fff;
    border-bottom: 1px solid #ebebeb;
    padding: 0 24px;
    height: 56px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
  }}
  .header-left {{ display: flex; align-items: center; gap: 12px; }}
  .header-left svg {{ display: block; }}
  .ai-badge {{
    background: #fe502a;
    color: #fff;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 2px 7px;
    border-radius: 4px;
    text-transform: uppercase;
  }}
  .header-right {{ display: flex; align-items: center; gap: 16px; }}
  .user-name {{ font-size: 13px; color: #2D2926; font-weight: 500; }}
  .btn-new {{ background: none; border: 1.5px solid #fe502a; color: #fe502a; border-radius: 6px; padding: 5px 12px; font-size: 12px; font-weight: 600; cursor: pointer; font-family: inherit; }}
  .btn-new:hover {{ background: #fff4f1; }}
  .btn-logout {{ font-size: 12px; color: #999; text-decoration: none; }}
  .btn-logout:hover {{ color: #2D2926; }}

  /* Chat area */
  #chat {{
    flex: 1;
    overflow-y: auto;
    padding: 24px 20px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }}

  /* Welcome state */
  .welcome {{
    margin: auto;
    text-align: center;
    padding: 40px 20px;
  }}
  .welcome svg {{ margin: 0 auto 16px; display: block; }}
  .welcome h2 {{ font-size: 20px; font-weight: 600; color: #2D2926; margin-bottom: 8px; }}
  .welcome p {{ font-size: 14px; color: #888; max-width: 360px; margin: 0 auto 24px; line-height: 1.6; }}
  .suggestions {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; max-width: 540px; margin: 0 auto; }}
  .suggestion {{
    background: #fff;
    border: 1.5px solid #ebebeb;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
    color: #2D2926;
    cursor: pointer;
    font-family: inherit;
    text-align: left;
    transition: border-color 0.15s;
  }}
  .suggestion:hover {{ border-color: #fe502a; color: #fe502a; }}

  /* Messages */
  .msg {{ max-width: 760px; width: 100%; display: flex; flex-direction: column; }}
  .msg.user {{ align-self: flex-end; align-items: flex-end; }}
  .msg.assistant {{ align-self: flex-start; align-items: flex-start; }}
  .msg-inner {{ display: flex; align-items: flex-end; gap: 8px; }}
  .msg.user .msg-inner {{ flex-direction: row-reverse; }}
  .avatar {{
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 600; flex-shrink: 0;
  }}
  .assistant .avatar {{ background: #fe502a; color: #fff; }}
  .user .avatar {{ background: #2D2926; color: #fff; }}
  .bubble {{
    padding: 12px 16px;
    border-radius: 14px;
    line-height: 1.6;
    font-size: 14px;
    white-space: pre-wrap;
    word-break: break-word;
    max-width: calc(100% - 40px);
  }}
  .user .bubble {{
    background: #fe502a;
    color: #fff;
    border-bottom-right-radius: 4px;
  }}
  .assistant .bubble {{
    background: #fff;
    color: #2D2926;
    border: 1px solid #ebebeb;
    border-bottom-left-radius: 4px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }}
  .meta {{ font-size: 11px; color: #bbb; margin-top: 4px; padding: 0 36px; }}
  .user .meta {{ text-align: right; }}
  .cursor {{ display: inline-block; width: 2px; height: 14px; background: #fe502a; margin-left: 2px; vertical-align: middle; animation: blink 0.8s infinite; }}
  @keyframes blink {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0; }} }}

  /* Footer */
  footer {{
    background: #fff;
    border-top: 1px solid #ebebeb;
    padding: 14px 20px;
    flex-shrink: 0;
  }}
  #form {{ display: flex; gap: 10px; max-width: 800px; margin: 0 auto; align-items: flex-end; }}
  #input {{
    flex: 1;
    padding: 10px 14px;
    border: 1.5px solid #ebebeb;
    border-radius: 10px;
    font-size: 14px;
    resize: none;
    height: 44px;
    max-height: 120px;
    line-height: 1.5;
    font-family: inherit;
    color: #2D2926;
    background: #f6f8f9;
    transition: border-color 0.15s;
  }}
  #input:focus {{ outline: none; border-color: #fe502a; background: #fff; }}
  #input::placeholder {{ color: #bbb; }}
  #send {{
    padding: 0 20px;
    height: 44px;
    background: #fe502a;
    color: #fff;
    border: none;
    border-radius: 10px;
    font-size: 14px;
    cursor: pointer;
    font-weight: 600;
    font-family: inherit;
    white-space: nowrap;
    transition: background 0.15s;
    flex-shrink: 0;
  }}
  #send:hover {{ background: #e0431f; }}
  #send:disabled {{ background: #f9b89f; cursor: not-allowed; }}
  .footer-hint {{ text-align: center; font-size: 11px; color: #ccc; margin-top: 8px; }}
</style>
</head>
<body>
<header>
  <div class="header-left">
    {ANANAS_LOGO_SVG}
    <span class="ai-badge">AI</span>
  </div>
  <div class="header-right">
    <button class="btn-new" onclick="newChat()">+ New chat</button>
    <span class="user-name">{user["name"]}</span>
    <a href="/auth/logout" class="btn-logout">Sign out</a>
  </div>
</header>

<div id="chat">
  <div class="welcome" id="welcome">
    {ANANAS_LOGO_SVG.replace('width="100"', 'width="72"')}
    <h2>Ananas AI</h2>
    <p>Ask me anything about the platform - campaigns, KPIs, agent outputs, strategy, or how the system works.</p>
    <div class="suggestions">
      <button class="suggestion" onclick="suggest(this)">What did performance-agent find today?</button>
      <button class="suggestion" onclick="suggest(this)">What's our coupon dependency ratio?</button>
      <button class="suggestion" onclick="suggest(this)">Explain our Trustpilot situation</button>
      <button class="suggestion" onclick="suggest(this)">Which agents are running in Phase 2?</button>
      <button class="suggestion" onclick="suggest(this)">What's our POAS target and current status?</button>
      <button class="suggestion" onclick="suggest(this)">Why do we have zero Google Shopping campaigns?</button>
    </div>
  </div>
</div>

<footer>
  <form id="form">
    <textarea id="input" placeholder="Ask anything..." rows="1"></textarea>
    <button id="send" type="submit">Send</button>
  </form>
  <div class="footer-hint">Shift+Enter for new line &nbsp;·&nbsp; Enter to send</div>
</footer>

<script>
let sessionId = localStorage.getItem('chatSession') || null;

function newChat() {{
  sessionId = null;
  localStorage.removeItem('chatSession');
  const chat = document.getElementById('chat');
  chat.innerHTML = '';
  chat.appendChild(buildWelcome());
}}

function buildWelcome() {{
  const d = document.createElement('div');
  d.className = 'welcome';
  d.id = 'welcome';
  d.innerHTML = document.querySelector('.welcome').innerHTML;
  return d;
}}

function suggest(btn) {{
  document.getElementById('input').value = btn.textContent;
  document.getElementById('form').dispatchEvent(new Event('submit'));
}}

function initials(name) {{
  return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
}}

function addMsg(role, text, streaming=false) {{
  const welcome = document.getElementById('welcome');
  if (welcome) welcome.remove();

  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  const now = new Date().toLocaleTimeString([], {{hour:'2-digit', minute:'2-digit'}});
  const avatarText = role === 'user' ? initials('{user["name"]}') : 'AI';
  const cursor = streaming && role === 'assistant' ? '<span class="cursor" id="cursor"></span>' : '';

  div.innerHTML = `
    <div class="msg-inner">
      <div class="avatar">${{avatarText}}</div>
      <div class="bubble" id="bubble-${{Date.now()}}">${{text}}${{cursor}}</div>
    </div>
    <div class="meta">${{role === 'user' ? 'You' : 'Ananas AI'}} · ${{now}}</div>`;

  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div.querySelector('.bubble');
}}

document.getElementById('form').addEventListener('submit', async (e) => {{
  e.preventDefault();
  const input = document.getElementById('input');
  const msg = input.value.trim();
  if (!msg) return;

  input.value = '';
  input.style.height = '44px';
  document.getElementById('send').disabled = true;

  addMsg('user', msg);
  const bubble = addMsg('assistant', '', true);

  try {{
    const resp = await fetch('/chat', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{message: msg, session_id: sessionId}}),
    }});

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let text = '';

    while (true) {{
      const {{done, value}} = await reader.read();
      if (done) break;
      const lines = decoder.decode(value).split('\\n').filter(Boolean);
      for (const line of lines) {{
        const data = JSON.parse(line);
        if (data.session_id) {{
          sessionId = data.session_id;
          localStorage.setItem('chatSession', sessionId);
        }}
        if (data.text) {{
          text += data.text;
          const cursor = bubble.querySelector('#cursor');
          bubble.textContent = text;
          if (cursor) bubble.appendChild(cursor);
          document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
        }}
        if (data.error) {{
          bubble.textContent = 'Error: ' + data.error;
        }}
        if (data.done) {{
          const cursor = document.getElementById('cursor');
          if (cursor) cursor.remove();
        }}
      }}
    }}
  }} catch (err) {{
    bubble.textContent = 'Connection error. Please try again.';
    const cursor = document.getElementById('cursor');
    if (cursor) cursor.remove();
  }}

  document.getElementById('send').disabled = false;
  input.focus();
}});

document.getElementById('input').addEventListener('input', function() {{
  this.style.height = '44px';
  this.style.height = Math.min(this.scrollHeight, 120) + 'px';
}});

document.getElementById('input').addEventListener('keydown', function(e) {{
  if (e.key === 'Enter' && !e.shiftKey) {{
    e.preventDefault();
    document.getElementById('form').dispatchEvent(new Event('submit'));
  }}
}});
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    _ensure_tables()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
