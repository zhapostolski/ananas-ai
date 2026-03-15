import { StatCard } from "@/components/dashboard/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getLatestOutput } from "@/lib/db";
import { formatDate, dbStr } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function ReputationPage() {
  const latest = getLatestOutput("reputation-agent");
  const json = latest?.output_json as Record<string, unknown> | null;
  const gb = json?.google_business as Record<string, unknown> | undefined;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Reputation</h1>
          <p className="text-sm text-muted-foreground">
            Google Business reviews, sentiment, and response tracking
          </p>
        </div>
        {!!latest?.run_at && (
          <Badge variant="outline">{formatDate(latest.run_at as string)}</Badge>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Google Rating"
          value={dbStr(gb?.average_rating)}
          description="Google Business Profile"
        />
        <StatCard
          title="Total Reviews"
          value={dbStr(gb?.total_reviews)}
          description="Google Business"
        />
        <StatCard
          title="Unanswered Reviews"
          value={dbStr(gb?.unanswered_reviews)}
          status={typeof gb?.unanswered_reviews === "number" && (gb.unanswered_reviews as number) > 5 ? "warning" : "ok"}
          description="Require response"
        />
        <StatCard
          title="Profile Status"
          value={dbStr(gb?.status, "Not configured")}
          status="warning"
          description="Google Business"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Reputation Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          {latest?.summary_text ? (
            <div className="whitespace-pre-wrap text-sm leading-relaxed text-gray-700">
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
