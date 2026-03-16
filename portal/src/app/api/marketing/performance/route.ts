import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getLatestOutput, getPerformanceHistory } from "@/lib/db";

function daysForPreset(preset: string | null): number {
  if (!preset) return 7;

  // Custom range: "YYYY-MM-DD,YYYY-MM-DD"
  if (preset.includes(",")) {
    const [from, to] = preset.split(",");
    const fromDate = new Date(from);
    const toDate = new Date(to);
    if (!isNaN(fromDate.getTime()) && !isNaN(toDate.getTime())) {
      return Math.max(1, Math.ceil((toDate.getTime() - fromDate.getTime()) / 86400000) + 1);
    }
    return 7;
  }

  switch (preset) {
    case "today":
    case "yesterday":
      return 1;
    case "last_7d":
      return 7;
    case "last_week":
      return 14;
    case "last_30d":
      return 30;
    case "mtd": {
      const now = new Date();
      return now.getDate();
    }
    case "last_month":
      return 30;
    case "qtd": {
      const now = new Date();
      const q = Math.floor(now.getMonth() / 3);
      const startOfQ = new Date(now.getFullYear(), q * 3, 1);
      return Math.ceil((now.getTime() - startOfQ.getTime()) / 86400000) + 1;
    }
    case "ytd": {
      const now = new Date();
      const startOfYear = new Date(now.getFullYear(), 0, 1);
      return Math.ceil((now.getTime() - startOfYear.getTime()) / 86400000) + 1;
    }
    default:
      return 7;
  }
}

export async function GET(request: Request) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const preset = searchParams.get("range");
  const days = daysForPreset(preset);

  const latest = getLatestOutput("performance-agent");
  const kpisRaw = (latest?.output_json as Record<string, unknown> | null)?.summary as Record<string, unknown> | undefined;

  const history = getPerformanceHistory(days);

  return NextResponse.json({
    run_at: latest?.run_at ?? null,
    summary_text: latest?.summary_text ?? null,
    kpis: {
      total_paid_spend: kpisRaw?.total_paid_spend ?? null,
      blended_roas: kpisRaw?.blended_roas ?? null,
      ga4_revenue: kpisRaw?.ga4_revenue ?? null,
      ga4_sessions: kpisRaw?.ga4_sessions ?? null,
      ga4_conversion_rate_pct: kpisRaw?.ga4_conversion_rate_pct ?? null,
      ga4_users: null, // extracted from history's latest day
    },
    history: history.map((d) => ({
      date: d.date,
      sessions: d.sessions,
      revenue: d.revenue,
      paid_spend: d.paid_spend,
      blended_roas: d.blended_roas,
    })),
  });
}
