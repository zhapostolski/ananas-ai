/**
 * Lightweight SQLite reader for portal API routes.
 * Uses better-sqlite3 (sync) for simplicity in Next.js Route Handlers.
 *
 * Install: npm install better-sqlite3 @types/better-sqlite3
 */
import Database from "better-sqlite3";
import path from "path";

const DB_PATH =
  process.env.DB_PATH ??
  path.resolve(process.cwd(), "../ananas_ai_dev.db");

let _db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!_db) {
    _db = new Database(DB_PATH, { readonly: true });
  }
  return _db;
}

export function getLatestOutput(agentId: string) {
  const db = getDb();
  return db
    .prepare(
      `SELECT * FROM agent_runs
       WHERE agent_id = ? AND status = 'ok'
       ORDER BY run_at DESC
       LIMIT 1`
    )
    .get(agentId) as Record<string, unknown> | undefined;
}

export function getOutputHistory(agentId: string, days = 7) {
  const db = getDb();
  return db
    .prepare(
      `SELECT id, agent_id, run_at, status, summary_text, model_used,
              tokens_in, tokens_out, estimated_cost, duration_ms
       FROM agent_runs
       WHERE agent_id = ? AND run_at >= datetime('now', ?)
       ORDER BY run_at DESC`
    )
    .all(agentId, `-${days} days`) as Record<string, unknown>[];
}
