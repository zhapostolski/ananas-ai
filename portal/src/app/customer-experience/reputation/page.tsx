import { AgentStatus } from "@/components/dashboard/agent-status";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatCard } from "@/components/dashboard/stat-card";
import { getLatestOutput } from "@/lib/db";
import { dbStr, stripMarkdown } from "@/lib/utils";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function CXReputationPage() {
  const latest = getLatestOutput("reputation-agent");
  const data = latest?.output_json as Record<string, unknown> | null;
  const gbp = data?.google_business as Record<string, unknown> | null;

  const agents = [
    {
      id: "reputation-agent",
      label: "Reputation Agent",
      lastRun: latest?.run_at as string | undefined,
      status: (latest?.status as "ok" | "error" | "skipped") ?? "skipped",
      summary: latest?.summary_text as string | undefined,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Reputation & Reviews</h1>
        <p className="text-sm text-muted-foreground">
          Google Business Profile rating, review themes, response rate
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          title="Google Rating"
          value={dbStr(gbp?.average_rating, "N/A")}
          description="Google Business Profile"
        />
        <StatCard
          title="Total Reviews"
          value={dbStr(gbp?.total_reviews, "N/A")}
        />
        <StatCard
          title="Unanswered"
          value={dbStr(gbp?.unanswered_reviews, "N/A")}
          status={gbp?.unanswered_reviews ? "warning" : undefined}
          description="Needs response"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Daily Reputation Brief</CardTitle>
            </CardHeader>
            <CardContent>
              {latest?.summary_text ? (
                <div className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">
                  {stripMarkdown(dbStr(latest.summary_text))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground italic">
                  No data yet. Configure Google Business Profile credentials to enable live monitoring.
                </p>
              )}
            </CardContent>
          </Card>
        </div>
        <div>
          <AgentStatus agents={agents} />
        </div>
      </div>
    </div>
  );
}
