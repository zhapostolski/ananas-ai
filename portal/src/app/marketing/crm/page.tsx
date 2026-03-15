import { StatCard } from "@/components/dashboard/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getLatestOutput } from "@/lib/db";
import { formatDate, dbStr } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function CrmPage() {
  const latest = getLatestOutput("crm-lifecycle-agent");
  const json = latest?.output_json as Record<string, unknown> | null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">CRM & Lifecycle</h1>
          <p className="text-sm text-muted-foreground">
            Retention, email revenue, cart recovery, and churn signals
          </p>
        </div>
        {!!latest?.run_at && (
          <Badge variant="outline">{formatDate(latest.run_at as string)}</Badge>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Repeat Purchase Rate" value={(json?.repeat_rate as string) ?? "--"} />
        <StatCard title="Cart Recovery Rate" value={(json?.cart_recovery_rate as string) ?? "--"} />
        <StatCard
          title="Email Automations"
          value="None live"
          status="warning"
          description="Cart recovery, churn flows not active"
        />
        <StatCard title="Churn Risk Users" value={(json?.churn_risk_count as string) ?? "--"} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">CRM Analysis</CardTitle>
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
