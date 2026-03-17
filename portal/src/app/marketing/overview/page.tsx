import { getLatestOutput, getPerformanceHistory } from "@/lib/db";
import { stripMarkdown } from "@/lib/utils";
import { auth } from "@/lib/auth";
import { OverviewClient } from "./overview-client";

export const dynamic = "force-dynamic";
export const revalidate = 0;

const AGENTS = [
  { id: "performance-agent", labelKey: "agent_performance" },
  { id: "crm-lifecycle-agent", labelKey: "agent_crm" },
  { id: "reputation-agent", labelKey: "agent_reputation" },
  { id: "marketing-ops-agent", labelKey: "agent_ops" },
  { id: "cross-channel-brief-agent", labelKey: "agent_brief" },
];

function shortDay(dateStr: string): string {
  try {
    const d = new Date(dateStr + "T00:00:00");
    return d.toLocaleDateString("en-US", { weekday: "short" });
  } catch {
    return dateStr.slice(5);
  }
}

export default async function OverviewPage() {
  await auth();

  const agentData = AGENTS.map((a) => {
    const latest = getLatestOutput(a.id);
    return {
      id: a.id,
      labelKey: a.labelKey,
      lastRun: latest?.run_at as string | undefined,
      status: (latest?.status as "ok" | "error" | "skipped") ?? "skipped",
      summary:
        typeof latest?.summary_text === "string"
          ? latest.summary_text.slice(0, 120)
          : undefined,
    };
  });

  const briefOutput = getLatestOutput("cross-channel-brief-agent");
  const briefJson = (briefOutput?.output_json as Record<string, unknown> | null) ?? {};

  const summaryText =
    typeof briefOutput?.summary_text === "string"
      ? stripMarkdown(briefOutput.summary_text)
      : null;

  const perfHistory = getPerformanceHistory(7);
  const revenueData = perfHistory.map((d) => ({ label: shortDay(d.date), value: d.revenue }));
  const sessionsData = perfHistory.map((d) => ({ label: shortDay(d.date), value: d.sessions }));

  return (
    <OverviewClient
      agentData={agentData}
      summaryText={summaryText}
      revenueData={revenueData}
      sessionsData={sessionsData}
      briefRunAt={(briefOutput?.run_at as string | null) ?? null}
      briefJson={{
        sessions_7d: briefJson.sessions_7d,
        gmv_7d: briefJson.gmv_7d,
        roas: briefJson.roas,
        google_rating: briefJson.google_rating,
        sessions_delta: typeof briefJson.sessions_delta === "number" ? briefJson.sessions_delta : undefined,
        gmv_delta: typeof briefJson.gmv_delta === "number" ? briefJson.gmv_delta : undefined,
      }}
    />
  );
}
