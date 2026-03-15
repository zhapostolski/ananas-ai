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
  bio                   TEXT,
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
