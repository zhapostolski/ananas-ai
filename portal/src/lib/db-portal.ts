/**
 * Writable SQLite connection for portal-specific data.
 * Separate from db.ts (read-only agent outputs in ananas_ai.db).
 * File: portal.db
 */
import Database from "better-sqlite3";
import path from "path";
import fs from "fs";

const PORTAL_DB_PATH =
  process.env.PORTAL_DB_PATH ??
  path.resolve(process.cwd(), "../portal.db");

let _db: Database.Database | null = null;

export function getPortalDb(): Database.Database {
  if (!_db) {
    _db = new Database(PORTAL_DB_PATH);
    _db.pragma("journal_mode = WAL");
    bootstrapPortalSchema(_db);
  }
  return _db;
}

function bootstrapPortalSchema(db: Database.Database): void {
  const schemaPath = path.resolve(process.cwd(), "sql/portal-schema.sql");
  if (!fs.existsSync(schemaPath)) return;
  const sql = fs.readFileSync(schemaPath, "utf-8");
  db.exec(sql);
  // Migrations for columns added after initial schema
  runMigrations(db);
}

function runMigrations(db: Database.Database): void {
  const cols = db.pragma("table_info(portal_users)") as Array<{ name: string }>;
  const colNames = cols.map((c) => c.name);
  const addIfMissing = (col: string, def: string) => {
    if (!colNames.includes(col)) db.exec(`ALTER TABLE portal_users ADD COLUMN ${col} ${def}`);
  };
  addIfMissing("avatar_url", "TEXT");
  addIfMissing("azure_job_title", "TEXT");
  addIfMissing("azure_department", "TEXT");
  addIfMissing("azure_phone", "TEXT");
  addIfMissing("azure_office", "TEXT");
  addIfMissing("birth_date", "TEXT");
  addIfMissing("hire_date", "TEXT");
  addIfMissing("berry_employee_id", "TEXT");
}

export interface PortalUser {
  id: number;
  email: string;
  display_name: string | null;
  role: string;
  department: string | null;
  avatar_color: string;
  avatar_url: string | null;
  bio: string | null;
  azure_job_title: string | null;
  azure_department: string | null;
  azure_phone: string | null;
  azure_office: string | null;
  birth_date: string | null;
  hire_date: string | null;
  berry_employee_id: string | null;
  interests_json: string;
  preferences_json: string;
  favorite_agents_json: string;
  notifications_json: string;
  last_seen_at: string | null;
  created_at: string;
  updated_at: string;
}

export function getPortalUser(email: string): PortalUser | undefined {
  return getPortalDb()
    .prepare("SELECT * FROM portal_users WHERE email = ?")
    .get(email) as PortalUser | undefined;
}

export function getOrCreatePortalUser(
  email: string,
  displayName?: string | null
): PortalUser {
  const db = getPortalDb();
  const existing = db
    .prepare("SELECT * FROM portal_users WHERE email = ?")
    .get(email) as PortalUser | undefined;
  if (existing) return existing;

  db.prepare(
    "INSERT INTO portal_users (email, display_name) VALUES (?, ?)"
  ).run(email, displayName ?? null);

  return db
    .prepare("SELECT * FROM portal_users WHERE email = ?")
    .get(email) as PortalUser;
}

export function updatePortalUser(
  email: string,
  fields: Partial<
    Pick<
      PortalUser,
      | "display_name"
      | "role"
      | "department"
      | "avatar_color"
      | "avatar_url"
      | "bio"
      | "azure_job_title"
      | "azure_department"
      | "azure_phone"
      | "azure_office"
      | "birth_date"
      | "hire_date"
      | "berry_employee_id"
      | "interests_json"
      | "preferences_json"
      | "favorite_agents_json"
      | "notifications_json"
      | "last_seen_at"
    >
  >
): void {
  const keys = Object.keys(fields);
  if (keys.length === 0) return;
  const sets = keys.map((k) => `${k} = @${k}`).join(", ");
  getPortalDb()
    .prepare(
      `UPDATE portal_users SET ${sets}, updated_at = datetime('now') WHERE email = @email`
    )
    .run({ ...fields, email });
}

export function touchLastSeen(email: string): void {
  getPortalDb()
    .prepare(
      "UPDATE portal_users SET last_seen_at = datetime('now') WHERE email = ?"
    )
    .run(email);
}

export function trackPageView(
  email: string,
  page: string,
  title?: string,
  sessionId?: string
): void {
  getPortalDb()
    .prepare(
      "INSERT INTO portal_page_views (email, page, title, session_id) VALUES (?, ?, ?, ?)"
    )
    .run(email, page, title ?? null, sessionId ?? null);
}

export function getUserActivity(
  email: string,
  limit = 20
): Array<{ page: string; title: string | null; created_at: string }> {
  return getPortalDb()
    .prepare(
      "SELECT page, title, created_at FROM portal_page_views WHERE email = ? ORDER BY created_at DESC LIMIT ?"
    )
    .all(email, limit) as Array<{
    page: string;
    title: string | null;
    created_at: string;
  }>;
}

export function getUserMostVisitedPages(
  email: string,
  limit = 5
): Array<{ page: string; count: number }> {
  return getPortalDb()
    .prepare(
      "SELECT page, COUNT(*) as count FROM portal_page_views WHERE email = ? GROUP BY page ORDER BY count DESC LIMIT ?"
    )
    .all(email, limit) as Array<{ page: string; count: number }>;
}

export function getAllPortalUsers(): PortalUser[] {
  return getPortalDb()
    .prepare("SELECT * FROM portal_users ORDER BY last_seen_at DESC NULLS LAST")
    .all() as PortalUser[];
}

export function auditRoleChange(
  email: string,
  oldRole: string,
  newRole: string,
  changedBy: string,
  note?: string
): void {
  const db = getPortalDb();
  db.prepare(
    "INSERT INTO portal_role_audit (email, old_role, new_role, changed_by, note) VALUES (?, ?, ?, ?, ?)"
  ).run(email, oldRole, newRole, changedBy, note ?? null);
  db.prepare(
    "UPDATE portal_users SET role = ?, updated_at = datetime('now') WHERE email = ?"
  ).run(newRole, email);
}

export function createRoleInvite(
  email: string,
  role: string,
  invitedBy: string
): void {
  getPortalDb()
    .prepare(
      "INSERT INTO portal_role_invites (email, role, invited_by) VALUES (?, ?, ?)"
    )
    .run(email, role, invitedBy);
}

export function getPendingInvite(
  email: string
): { role: string } | undefined {
  return getPortalDb()
    .prepare(
      "SELECT role FROM portal_role_invites WHERE email = ? AND used_at IS NULL ORDER BY created_at DESC LIMIT 1"
    )
    .get(email) as { role: string } | undefined;
}

export function markInviteUsed(email: string): void {
  getPortalDb()
    .prepare(
      "UPDATE portal_role_invites SET used_at = datetime('now') WHERE email = ? AND used_at IS NULL"
    )
    .run(email);
}

// ── Notifications ─────────────────────────────────────────────────────────

export interface PortalNotification {
  id: number;
  recipient: string | null;
  sender: string;
  type: string;
  title: string;
  body: string | null;
  link: string | null;
  read_by_json: string;
  created_at: string;
}

export function createNotification(params: {
  recipient: string | null;
  sender: string;
  type?: string;
  title: string;
  body?: string;
  link?: string;
}): void {
  getPortalDb()
    .prepare(
      `INSERT INTO portal_notifications (recipient, sender, type, title, body, link)
       VALUES (?, ?, ?, ?, ?, ?)`
    )
    .run(
      params.recipient ?? null,
      params.sender,
      params.type ?? "admin_message",
      params.title,
      params.body ?? null,
      params.link ?? null
    );
}

export function getNotificationsForUser(
  email: string,
  limit = 30
): PortalNotification[] {
  return getPortalDb()
    .prepare(
      `SELECT * FROM portal_notifications
       WHERE recipient IS NULL OR recipient = ?
       ORDER BY created_at DESC LIMIT ?`
    )
    .all(email, limit) as PortalNotification[];
}

export function countUnreadForUser(email: string): number {
  const rows = getPortalDb()
    .prepare(
      `SELECT read_by_json FROM portal_notifications
       WHERE recipient IS NULL OR recipient = ?`
    )
    .all(email) as Array<{ read_by_json: string }>;
  return rows.filter((r) => {
    try {
      const map = JSON.parse(r.read_by_json) as Record<string, string>;
      return !map[email];
    } catch {
      return true;
    }
  }).length;
}

export function markNotificationRead(id: number, email: string): void {
  const row = getPortalDb()
    .prepare("SELECT read_by_json FROM portal_notifications WHERE id = ?")
    .get(id) as { read_by_json: string } | undefined;
  if (!row) return;
  let map: Record<string, string> = {};
  try {
    map = JSON.parse(row.read_by_json);
  } catch {
    /* empty */
  }
  map[email] = new Date().toISOString();
  getPortalDb()
    .prepare("UPDATE portal_notifications SET read_by_json = ? WHERE id = ?")
    .run(JSON.stringify(map), id);
}

export function markAllReadForUser(email: string): void {
  const rows = getPortalDb()
    .prepare(
      `SELECT id, read_by_json FROM portal_notifications
       WHERE recipient IS NULL OR recipient = ?`
    )
    .all(email) as Array<{ id: number; read_by_json: string }>;
  const now = new Date().toISOString();
  const stmt = getPortalDb().prepare(
    "UPDATE portal_notifications SET read_by_json = ? WHERE id = ?"
  );
  for (const row of rows) {
    let map: Record<string, string> = {};
    try {
      map = JSON.parse(row.read_by_json);
    } catch {
      /* empty */
    }
    if (!map[email]) {
      map[email] = now;
      stmt.run(JSON.stringify(map), row.id);
    }
  }
}
