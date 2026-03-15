import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getLatestOutput } from "@/lib/db";
import { formatDate, dbStr } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function InfluencersPage() {
  const latest = getLatestOutput("influencer-partnership-agent");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Influencers & Partnerships</h1>
          <p className="text-sm text-muted-foreground">
            Campaign ROI, creator scoring, affiliate performance
          </p>
        </div>
        {!!latest?.run_at && (
          <Badge variant="outline">{formatDate(latest.run_at as string)}</Badge>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Influencer Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          {latest?.summary_text ? (
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {latest.summary_text as string}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">
              No data yet. This is a Phase 2 agent.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
