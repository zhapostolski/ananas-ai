import { StatCard } from "@/components/dashboard/stat-card";
import { AgentStatus } from "@/components/dashboard/agent-status";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getLatestOutput } from "@/lib/db";
import { formatDate, dbStr, stripMarkdown } from "@/lib/utils";

export const dynamic = "force-dynamic";
export const revalidate = 0;

const AGENTS = [
  { id: "performance-agent", label: "Performance" },
  { id: "crm-lifecycle-agent", label: "CRM & Lifecycle" },
  { id: "reputation-agent", label: "Reputation" },
  { id: "marketing-ops-agent", label: "Marketing Ops" },
  { id: "cross-channel-brief-agent", label: "Overview" },
];

export default async function OverviewPage() {
  const agentData = AGENTS.map((a) => {
    const latest = getLatestOutput(a.id);
    return {
      id: a.id,
      label: a.label,
      lastRun: latest?.run_at as string | undefined,
      status: (latest?.status as "ok" | "error" | "skipped") ?? "skipped",
      summary: typeof latest?.summary_text === "string" ? latest.summary_text.slice(0, 120) : undefined,
    };
  });

  const briefOutput = getLatestOutput("cross-channel-brief-agent");
  const briefJson = briefOutput?.output_json as Record<string, unknown> | null;

  const summaryText =
    typeof briefOutput?.summary_text === "string"
      ? stripMarkdown(briefOutput.summary_text)
      : null;

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

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Sessions (7d)"
          value={dbStr(briefJson?.sessions_7d)}
          delta={typeof briefJson?.sessions_delta === "number" ? briefJson.sessions_delta as number : undefined}
          deltaLabel="WoW"
        />
        <StatCard
          title="Revenue (7d)"
          value={dbStr(briefJson?.gmv_7d)}
          delta={typeof briefJson?.gmv_delta === "number" ? briefJson.gmv_delta as number : undefined}
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

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Daily Summary</CardTitle>
            </CardHeader>
            <CardContent>
              {summaryText ? (
                <div className="whitespace-pre-wrap text-sm leading-relaxed text-gray-700">
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
