/**
 * Lightweight SQLite reader for portal API routes.
 * Uses better-sqlite3 (sync) for simplicity in Next.js Route Handlers.
 *
 * Schema tables: agent_outputs, agent_logs, metrics_history, system_health,
 *                delivery_log, bot_interactions
 */
import Database from "better-sqlite3";
import path from "path";

const DB_PATH =
  process.env.DB_PATH ??
  path.resolve(process.cwd(), "../ananas_ai.db");

let _db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!_db) {
    _db = new Database(DB_PATH, { readonly: true });
  }
  return _db;
}

/**
 * Returns the latest successful output for an agent.
 * Columns aliased for portal compatibility:
 *   data_json  → output_json
 *   created_at → run_at
 *   summary    from data_json → summary_text (if present)
 */
export function getLatestOutput(agentName: string) {
  const db = getDb();
  const row = db
    .prepare(
      `SELECT id, agent_name, output_type, data_json, model_used, created_at
       FROM agent_outputs
       WHERE agent_name = ?
       ORDER BY created_at DESC
       LIMIT 1`
    )
    .get(agentName) as Record<string, unknown> | undefined;

  if (!row) return undefined;

  // Parse data_json and surface summary_text for template compatibility
  let parsed: Record<string, unknown> = {};
  try {
    parsed = JSON.parse(row.data_json as string);
  } catch {
    // leave empty
  }

  // Extract text summary — only accept string values, never objects.
  // Agent schema: performance/crm/reputation/ops use `headline`, brief uses `analysis`.
  const candidates = [parsed.summary_text, parsed.analysis, parsed.brief_text, parsed.headline];
  const summary_text = candidates.find((v) => typeof v === "string") ?? null;

  return {
    ...row,
    output_json: parsed,
    run_at: row.created_at,
    summary_text,
    status: "ok",
  };
}

export function getOutputHistory(agentName: string, days = 7) {
  const db = getDb();
  return db
    .prepare(
      `SELECT id, agent_name, output_type, model_used, created_at AS run_at,
              'ok' AS status
       FROM agent_outputs
       WHERE agent_name = ? AND created_at >= datetime('now', ?)
       ORDER BY created_at DESC`
    )
    .all(agentName, `-${days} days`) as Record<string, unknown>[];
}
