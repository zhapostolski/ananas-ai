import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatCard } from "@/components/dashboard/stat-card";
import { AgentStatus } from "@/components/dashboard/agent-status";
import { Badge } from "@/components/ui/badge";
import { getLatestOutput } from "@/lib/db";
import { formatDate, dbStr, stripMarkdown } from "@/lib/utils";

export const dynamic = "force-dynamic";
export const revalidate = 0;

const AGENTS = [
  { id: "performance-agent", label: "Performance & Paid Media" },
  { id: "crm-lifecycle-agent", label: "CRM & Lifecycle" },
  { id: "reputation-agent", label: "Reputation" },
  { id: "marketing-ops-agent", label: "Marketing Ops" },
  { id: "cross-channel-brief-agent", label: "Cross-Channel Brief" },
];

export default async function ExecutivePage() {
  const agentData = AGENTS.map((a) => {
    const latest = getLatestOutput(a.id);
    return {
      id: a.id,
      label: a.label,
      lastRun: latest?.run_at as string | undefined,
      status: (latest?.status as "ok" | "error" | "skipped") ?? "skipped",
      summary: latest?.summary_text as string | undefined,
    };
  });

  const briefOutput = getLatestOutput("cross-channel-brief-agent");
  const perfOutput = getLatestOutput("performance-agent");
  const perfJson = perfOutput?.output_json as Record<string, unknown> | null;
  const perfSummary = perfJson?.summary as Record<string, unknown> | null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Executive Overview</h1>
          <p className="text-sm text-muted-foreground">
            Cross-platform KPIs and platform health
          </p>
        </div>
        {!!briefOutput?.run_at && (
          <Badge variant="outline">
            Last updated: {formatDate(briefOutput.run_at as string)}
          </Badge>
        )}
      </div>

      {/* KPI row */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Revenue (today)"
          value={perfSummary?.ga4_revenue != null ? "€" + Number(perfSummary.ga4_revenue).toLocaleString("en-US", { maximumFractionDigits: 0 }) : "—"}
          description="GA4 total revenue"
        />
        <StatCard
          title="Sessions (today)"
          value={dbStr(perfSummary?.ga4_sessions)}
          description="GA4 sessions"
        />
        <StatCard
          title="Blended ROAS"
          value={perfSummary?.blended_roas != null ? Number(perfSummary.blended_roas).toFixed(1) + "x" : "—"}
          description="All paid channels"
        />
        <StatCard
          title="Paid Spend (today)"
          value={perfSummary?.total_paid_spend != null ? "€" + Number(perfSummary.total_paid_spend).toLocaleString("en-US", { maximumFractionDigits: 0 }) : "—"}
          description="Google + Meta"
        />
      </div>

      {/* Brief + Agent health */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Daily Brief Summary</CardTitle>
            </CardHeader>
            <CardContent>
              {briefOutput?.summary_text ? (
                <div className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">
                  {stripMarkdown(dbStr(briefOutput.summary_text))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground italic">
                  No brief available yet. Agents run at 06:00-07:30 AM.
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
