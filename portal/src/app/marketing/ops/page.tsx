import { StatCard } from "@/components/dashboard/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getLatestOutput } from "@/lib/db";
import { formatDate, dbStr } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function OpsPage() {
  const latest = getLatestOutput("marketing-ops-agent");
  const json = latest?.output_json as Record<string, unknown> | null;
  const tracking = json?.tracking_health as Record<string, unknown> | undefined;
  const sc = json?.search_console as Record<string, unknown> | undefined;
  const alerts = Array.isArray(json?.alerts) ? (json.alerts as string[]) : [];
  const notes = Array.isArray(json?.notes) ? (json.notes as string[]) : [];

  const trackingStatus = dbStr(tracking?.status, "Unknown");
  const isTrackingBad = trackingStatus.toLowerCase().includes("warn") || trackingStatus.toLowerCase().includes("error");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Marketing Ops</h1>
          <p className="text-sm text-muted-foreground">
            Tracking health, KPI integrity, and campaign quality
          </p>
        </div>
        {!!latest?.run_at && (
          <Badge variant="outline">{formatDate(latest.run_at as string)}</Badge>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Tracking Status"
          value={isTrackingBad ? "Warning" : trackingStatus === "Unknown" ? "--" : "OK"}
          status={isTrackingBad ? "warning" : "ok"}
          description="GA4 data pipeline"
        />
        <StatCard
          title="GA4 Sessions (today)"
          value={dbStr(tracking?.ga4_sessions)}
          description="Live tracking signal"
        />
        <StatCard
          title="Search Console Clicks"
          value={dbStr(sc?.total_clicks)}
          description="Last 7 days"
        />
        <StatCard
          title="Search Impressions"
          value={dbStr(sc?.total_impressions)}
          description="Last 7 days"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {alerts.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1.5">
                {alerts.map((alert, i) => (
                  <li key={i} className="text-sm text-red-600 flex items-start gap-2">
                    <span className="mt-0.5 h-1.5 w-1.5 rounded-full bg-red-500 shrink-0" />
                    {alert}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {notes.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Ops Notes</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1.5">
                {notes.map((note, i) => (
                  <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="mt-0.5 h-1.5 w-1.5 rounded-full bg-gray-400 shrink-0" />
                    {note}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        <Card className={alerts.length > 0 && notes.length > 0 ? "lg:col-span-2" : ""}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Full Report</CardTitle>
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
    </div>
  );
}
