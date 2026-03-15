import { StatCard } from "@/components/dashboard/stat-card";
import { AgentStatus } from "@/components/dashboard/agent-status";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getLatestOutput } from "@/lib/db";
import { formatDate, dbStr, stripMarkdown } from "@/lib/utils";
import { auth } from "@/lib/auth";
import { getPortalUser } from "@/lib/db-portal";
import { RevenueAreaChart, SessionsLineChart } from "@/components/dashboard/overview-charts";
import type { Role } from "@/types";

export const dynamic = "force-dynamic";
export const revalidate = 0;

const AGENTS = [
  { id: "performance-agent", label: "Performance" },
  { id: "crm-lifecycle-agent", label: "CRM & Lifecycle" },
  { id: "reputation-agent", label: "Reputation" },
  { id: "marketing-ops-agent", label: "Marketing Ops" },
  { id: "cross-channel-brief-agent", label: "Overview" },
];

/** Build fake 7-day chart data from brief JSON or return empty */
function buildChartData(
  briefJson: Record<string, unknown> | null,
  key: string
): Array<{ label: string; value: number }> {
  const trend = briefJson?.[key];
  if (!Array.isArray(trend) || trend.length === 0) return [];

  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  return trend.slice(0, 7).map((v: unknown, i: number) => ({
    label: days[i] ?? `D${i + 1}`,
    value: typeof v === "number" ? v : 0,
  }));
}

export default async function OverviewPage() {
  const session = await auth();
  const email = (session?.user as { email?: string } | undefined)?.email;

  const portalUser = email ? getPortalUser(email) : undefined;
  const interests: string[] = portalUser
    ? JSON.parse(portalUser.interests_json)
    : [];

  const agentData = AGENTS.map((a) => {
    const latest = getLatestOutput(a.id);
    return {
      id: a.id,
      label: a.label,
      lastRun: latest?.run_at as string | undefined,
      status: (latest?.status as "ok" | "error" | "skipped") ?? "skipped",
      summary:
        typeof latest?.summary_text === "string"
          ? latest.summary_text.slice(0, 120)
          : undefined,
    };
  });

  const briefOutput = getLatestOutput("cross-channel-brief-agent");
  const briefJson = briefOutput?.output_json as Record<string, unknown> | null;

  const summaryText =
    typeof briefOutput?.summary_text === "string"
      ? stripMarkdown(briefOutput.summary_text)
      : null;

  const revenueData = buildChartData(briefJson, "revenue_trend");
  const sessionsData = buildChartData(briefJson, "sessions_trend");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Overview</h1>
          <p className="text-sm text-muted-foreground">
            Daily cross-channel intelligence summary
          </p>
        </div>
        {!!briefOutput?.run_at && (
          <Badge variant="outline">
            Last updated: {formatDate(briefOutput.run_at as string)}
          </Badge>
        )}
      </div>

      {/* KPI stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Sessions (7d)"
          value={dbStr(briefJson?.sessions_7d)}
          delta={
            typeof briefJson?.sessions_delta === "number"
              ? (briefJson.sessions_delta as number)
              : undefined
          }
          deltaLabel="WoW"
        />
        <StatCard
          title="Revenue (7d)"
          value={dbStr(briefJson?.gmv_7d)}
          delta={
            typeof briefJson?.gmv_delta === "number"
              ? (briefJson.gmv_delta as number)
              : undefined
          }
          deltaLabel="WoW"
        />
        <StatCard
          title="Blended ROAS"
          value={dbStr(briefJson?.roas)}
          description="All paid channels"
        />
        <StatCard
          title="Google Business"
          value={dbStr(briefJson?.google_rating, "Not set up")}
          description="Review rating"
        />
      </div>

      {/* Charts row — only shown when data available */}
      {(revenueData.length > 0 || sessionsData.length > 0) && (
        <div className="grid gap-6 lg:grid-cols-2">
          {revenueData.length > 0 && <RevenueAreaChart data={revenueData} />}
          {sessionsData.length > 0 && <SessionsLineChart data={sessionsData} />}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Daily Summary</CardTitle>
            </CardHeader>
            <CardContent>
              {summaryText ? (
                <div className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">
                  {summaryText}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground italic">
                  No summary available yet. Agents run at 06:00 to 07:30.
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        <div>
          <AgentStatus agents={agentData} />
        </div>
      </div>
    </div>
  );
}
