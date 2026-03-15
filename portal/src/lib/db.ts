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

/**
 * Returns the latest N outputs for an agent, each with its full parsed JSON.
 * Used to build time-series charts on portal pages.
 */
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

interface DailyMetric {
  date: string;
  sessions: number;
  revenue: number;
  users: number;
  conversion_rate: number;
  paid_spend: number;
  blended_roas: number;
}

/**
 * Builds a time-series of daily GA4 + paid metrics from the last N agent_outputs
 * rows for the performance agent. Returns one entry per unique date, most recent last.
 */
export function getPerformanceHistory(days = 7): DailyMetric[] {
  const db = getDb();
  const rows = db
    .prepare(
      `SELECT data_json, date(created_at) as day
       FROM agent_outputs
       WHERE agent_name = 'performance-agent'
         AND created_at >= datetime('now', ?)
       ORDER BY created_at DESC`
    )
    .all(`-${days} days`) as Array<{ data_json: string; day: string }>;

  // De-duplicate by day, keep latest per day
  const seen = new Set<string>();
  const daily: DailyMetric[] = [];
  for (const row of rows) {
    if (seen.has(row.day)) continue;
    seen.add(row.day);
    let parsed: Record<string, unknown> = {};
    try {
      parsed = JSON.parse(row.data_json);
    } catch { /* empty */ }
    const ga4 = (parsed.ga4 ?? {}) as Record<string, unknown>;
    const summary = (parsed.summary ?? {}) as Record<string, unknown>;
    daily.push({
      date: row.day,
      sessions: (ga4.sessions ?? summary.ga4_sessions ?? 0) as number,
      revenue: (ga4.revenue ?? summary.ga4_revenue ?? 0) as number,
      users: (ga4.users ?? 0) as number,
      conversion_rate: (ga4.conversion_rate_pct ?? summary.ga4_conversion_rate_pct ?? 0) as number,
      paid_spend: (summary.total_paid_spend ?? 0) as number,
      blended_roas: (summary.blended_roas ?? 0) as number,
    });
  }
  // Return chronological order (oldest first for charts)
  return daily.reverse();
}
