-- Portal-specific database schema
-- Separate from ananas_ai.db (agent outputs, read-only)
-- File: portal.db (writable)

CREATE TABLE IF NOT EXISTS portal_users (
  id                    INTEGER PRIMARY KEY AUTOINCREMENT,
  email                 TEXT    NOT NULL UNIQUE,
  display_name          TEXT,
  role                  TEXT    NOT NULL DEFAULT 'performance_marketer',
  department            TEXT,
  avatar_color          TEXT    NOT NULL DEFAULT '#FE5000',
  avatar_url            TEXT,
  bio                   TEXT,
  -- Azure AD / Microsoft Graph fields (synced on login)
  azure_job_title       TEXT,
  azure_department      TEXT,
  azure_phone           TEXT,
  azure_office          TEXT,
  -- HR fields
  birth_date            TEXT,
  hire_date             TEXT,
  berry_employee_id     TEXT,
  interests_json        TEXT    NOT NULL DEFAULT '[]',
  preferences_json      TEXT    NOT NULL DEFAULT '{"theme":"system","density":"default"}',
  favorite_agents_json  TEXT    NOT NULL DEFAULT '[]',
  notifications_json    TEXT    NOT NULL DEFAULT '{}',
  last_seen_at          TEXT,
  created_at            TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at            TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS portal_role_invites (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  email       TEXT NOT NULL,
  role        TEXT NOT NULL,
  invited_by  TEXT NOT NULL,
  used_at     TEXT,
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS portal_page_views (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  email       TEXT NOT NULL,
  page        TEXT NOT NULL,
  title       TEXT,
  session_id  TEXT,
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_page_views_email ON portal_page_views(email);
CREATE INDEX IF NOT EXISTS idx_page_views_created ON portal_page_views(created_at);

CREATE TABLE IF NOT EXISTS portal_role_audit (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  email       TEXT NOT NULL,
  old_role    TEXT NOT NULL,
  new_role    TEXT NOT NULL,
  changed_by  TEXT NOT NULL,
  note        TEXT,
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS portal_notifications (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  recipient     TEXT,         -- NULL = broadcast to all users
  sender        TEXT NOT NULL,
  type          TEXT NOT NULL DEFAULT 'admin_message',
  -- types: admin_message | token_cap | agent_failure | system | invite
  title         TEXT NOT NULL,
  body          TEXT,
  link          TEXT,         -- optional action URL
  read_by_json  TEXT NOT NULL DEFAULT '{}',  -- JSON: {email: iso_timestamp}
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_notifications_created ON portal_notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON portal_notifications(recipient);

-- ── Chat ──────────────────────────────────────────────────────────────────
-- One session = one conversation thread per user
CREATE TABLE IF NOT EXISTS chat_sessions (
  id          TEXT    PRIMARY KEY,  -- UUID
  email       TEXT    NOT NULL,
  title       TEXT,                 -- auto-generated from first message
  model       TEXT    NOT NULL DEFAULT 'claude-sonnet-4-6',
  created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_email ON chat_sessions(email);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated ON chat_sessions(updated_at);

CREATE TABLE IF NOT EXISTS chat_messages (
  id          TEXT    PRIMARY KEY,  -- UUID
  session_id  TEXT    NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
  role        TEXT    NOT NULL,     -- 'user' | 'assistant'
  content     TEXT    NOT NULL,
  tokens_in   INTEGER,
  tokens_out  INTEGER,
  cost_usd    REAL,
  created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created ON chat_messages(created_at);
