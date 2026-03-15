/**
 * Returns the latest agent output for a given agent within a date range.
 * Used by CRM, Reputation, Ops pages with the date filter.
 *
 * Query params:
 *   agent  - agent name (e.g. crm-lifecycle-agent)
 *   from   - ISO date string (optional, defaults to 30 days ago)
 *   to     - ISO date string (optional, defaults to now)
 */
import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getDb } from "@/lib/db";

export async function GET(request: Request) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const agent = searchParams.get("agent");
  const from = searchParams.get("from");
  const to = searchParams.get("to");

  if (!agent) {
    return NextResponse.json({ error: "Missing agent param" }, { status: 400 });
  }

  const db = getDb();

  // Get all runs within the date range, most recent first
  const rows = db
    .prepare(
      `SELECT id, agent_name, data_json, model_used, created_at
       FROM agent_outputs
       WHERE agent_name = ?
         AND (? IS NULL OR date(created_at) >= ?)
         AND (? IS NULL OR date(created_at) <= ?)
       ORDER BY created_at DESC
       LIMIT 30`
    )
    .all(agent, from, from, to, to) as Array<{
      id: number;
      agent_name: string;
      data_json: string;
      model_used: string;
      created_at: string;
    }>;

  const runs = rows.map((row) => {
    let parsed: Record<string, unknown> = {};
    try {
      parsed = JSON.parse(row.data_json);
    } catch { /* empty */ }

    const candidates = [parsed.summary_text, parsed.analysis, parsed.brief_text, parsed.headline];
    const summary_text = candidates.find((v) => typeof v === "string") ?? null;

    return {
      id: row.id,
      run_at: row.created_at,
      model_used: row.model_used,
      output_json: parsed,
      summary_text,
    };
  });

  // Return the latest run and all runs in range
  return NextResponse.json({
    latest: runs[0] ?? null,
    runs,
    total: runs.length,
  });
}
