import { StatCard } from "@/components/dashboard/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getLatestOutput } from "@/lib/db";
import { formatDate, dbStr } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function ReputationPage() {
  const latest = getLatestOutput("reputation-agent");
  const json = latest?.output_json as Record<string, unknown> | null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Reputation</h1>
          <p className="text-sm text-muted-foreground">
            Trustpilot, Google reviews, sentiment tracking
          </p>
        </div>
        {!!latest?.run_at && (
          <Badge variant="outline">{formatDate(latest.run_at as string)}</Badge>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Trustpilot Score"
          value={(json?.trustpilot_score as string) ?? "2.0"}
          status="critical"
          description="Profile not yet claimed — CRITICAL"
        />
        <StatCard
          title="Google Reviews"
          value={(json?.google_rating as string) ?? "--"}
        />
        <StatCard
          title="Response Rate"
          value={(json?.response_rate as string) ?? "--"}
          description="Reviews responded to"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Reputation Analysis</CardTitle>
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
