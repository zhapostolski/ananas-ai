import { StatCard } from "@/components/dashboard/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getLatestOutput } from "@/lib/db";
import { formatDate, dbStr } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function InfluencersPage() {
  const latest = getLatestOutput("influencer-partnership-agent");
  const json = latest?.output_json as Record<string, unknown> | null;
  const campaigns = Array.isArray(json?.influencer_campaigns)
    ? (json.influencer_campaigns as Record<string, unknown>[])
    : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Influencers & Partnerships</h1>
          <p className="text-sm text-muted-foreground">
            Campaign ROI, creator performance, and affiliate revenue
          </p>
        </div>
        {!!latest?.run_at ? (
          <Badge variant="outline">{formatDate(latest.run_at as string)}</Badge>
        ) : (
          <Badge variant="outline" className="text-yellow-600 border-yellow-300">
            Phase 2 agent
          </Badge>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Active Campaigns"
          value={dbStr(json?.active_campaigns_count)}
          description="Live influencer campaigns"
        />
        <StatCard
          title="Top Creator ROI"
          value={dbStr(json?.top_creator_roi)}
          description="Best performing creator"
        />
        <StatCard
          title="Affiliate Revenue (30d)"
          value={dbStr(json?.affiliate_revenue_30d)}
          description="Total affiliate-driven revenue"
        />
        <StatCard
          title="Avg Engagement Rate"
          value={dbStr(json?.avg_engagement_rate)}
          description="Across active campaigns"
        />
      </div>

      {campaigns.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Active Campaigns</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-xs text-muted-foreground">
                    <th className="pb-2 pr-4 font-medium">Creator</th>
                    <th className="pb-2 pr-4 font-medium">Platform</th>
                    <th className="pb-2 pr-4 font-medium">Status</th>
                    <th className="pb-2 pr-4 font-medium">ROI</th>
                    <th className="pb-2 font-medium">Revenue</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {campaigns.map((c, i) => (
                    <tr key={i}>
                      <td className="py-2 pr-4 font-medium">{dbStr(c.creator_name)}</td>
                      <td className="py-2 pr-4 text-muted-foreground">{dbStr(c.platform)}</td>
                      <td className="py-2 pr-4">
                        <Badge
                          variant="outline"
                          className={
                            c.status === "active"
                              ? "border-green-300 text-green-700"
                              : "text-muted-foreground"
                          }
                        >
                          {dbStr(c.status)}
                        </Badge>
                      </td>
                      <td className="py-2 pr-4">{dbStr(c.roi)}</td>
                      <td className="py-2">{dbStr(c.revenue_attributed)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Campaign Data</CardTitle>
          </CardHeader>
          <CardContent>
            {latest?.summary_text ? (
              <div className="whitespace-pre-wrap text-sm leading-relaxed text-gray-700">
                {latest.summary_text as string}
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  No campaign data yet. The influencer agent will begin tracking once configured.
                </p>
                <div className="rounded-lg border border-dashed p-4">
                  <p className="text-xs text-muted-foreground font-medium mb-2">This module will track:</p>
                  <ul className="text-xs text-muted-foreground space-y-1">
                    <li>Creator campaign ROI and attributed revenue</li>
                    <li>Affiliate link performance and conversion rates</li>
                    <li>Engagement rates by creator and platform</li>
                    <li>Co-marketing opportunity detection</li>
                  </ul>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
