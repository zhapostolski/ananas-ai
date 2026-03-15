import { StatCard } from "@/components/dashboard/stat-card";
import { AgentStatus } from "@/components/dashboard/agent-status";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getLatestOutput } from "@/lib/db";
import { formatDate, dbStr } from "@/lib/utils";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function PerformancePage() {
  const latest = getLatestOutput("performance-agent");
  const json = latest?.output_json as Record<string, unknown> | null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Performance & Paid Media</h1>
          <p className="text-sm text-muted-foreground">
            Paid channel performance — Google, Meta, and more
          </p>
        </div>
        {!!latest?.run_at && (
          <Badge variant="outline">
            {formatDate(latest.run_at as string)}
          </Badge>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Spend (7d)" value={(json?.total_spend as string) ?? "--"} />
        <StatCard title="Blended ROAS" value={(json?.blended_roas as string) ?? "--"} />
        <StatCard title="CAC" value={(json?.cac as string) ?? "--"} description="Cost per acquisition" />
        <StatCard
          title="Google Shopping"
          value="No campaigns"
          status="critical"
          description="Zero campaigns on 250k+ products"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Agent Output</CardTitle>
        </CardHeader>
        <CardContent>
          {latest?.summary_text ? (
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {latest.summary_text as string}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">No data yet.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
