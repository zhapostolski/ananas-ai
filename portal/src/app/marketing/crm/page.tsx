import { KpiCard, KpiAlertBanner } from "@/components/dashboard/kpi-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getLatestOutput } from "@/lib/db";
import { formatDate } from "@/lib/utils";

export const dynamic = "force-dynamic";

function pctStatus(val: number | null | undefined, green: number, yellow: number, higherIsBetter = true) {
  if (val == null) return "neutral" as const;
  if (higherIsBetter) {
    return val >= green ? "green" : val >= yellow ? "yellow" : "red";
  } else {
    return val <= green ? "green" : val <= yellow ? "yellow" : "red";
  }
}

export default async function CrmPage() {
  const latest = getLatestOutput("crm-lifecycle-agent");
  const json = latest?.output_json as Record<string, unknown> | null;
  const email = json?.email as Record<string, unknown> | undefined;
  const lifecycle = json?.lifecycle as Record<string, unknown> | undefined;

  const cartAbandonmentRate = email?.cart_abandonment_rate as number | undefined;
  const cartRecoveryRate = email?.cart_recovery_rate as number | undefined;
  const repeatPurchaseRate = lifecycle?.repeat_purchase_rate as number | undefined;
  const activeSubscribers = email?.active_subscribers as number | undefined;
  const emailOpenRate = email?.open_rate as number | undefined;
  const emailRevPerSend = email?.revenue_per_send as number | undefined;
  const churnRate30d = lifecycle?.churn_rate_30d as number | undefined;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
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

      {/* Critical gaps */}
      <KpiAlertBanner
        title="No email lifecycle automations active"
        message="Cart recovery, win-back, churn prevention, and post-purchase flows are not live. Average cart recovery rate with automation: 15-20%. Every day without automation is revenue left on the table."
        status="critical"
      />

      {/* Cart & Acquisition */}
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
          Cart Performance
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <KpiCard
            title="Cart Abandonment Rate"
            value={cartAbandonmentRate != null ? cartAbandonmentRate.toFixed(1) + "%" : "--"}
            status={cartAbandonmentRate != null ? pctStatus(cartAbandonmentRate, 65, 75, false) : "neutral"}
            description="Target: <65% | Industry avg: 70-75%"
          />
          <KpiCard
            title="Cart Recovery Rate"
            value={cartRecoveryRate != null ? cartRecoveryRate.toFixed(1) + "%" : "0%"}
            status={cartRecoveryRate == null || cartRecoveryRate === 0 ? "critical" : pctStatus(cartRecoveryRate, 20, 10)}
            description={cartRecoveryRate === 0 || cartRecoveryRate == null ? "No recovery automation — target 15%+" : "Target: >20%"}
            badge={cartRecoveryRate === 0 || cartRecoveryRate == null ? "0% — Not live" : undefined}
          />
          <KpiCard
            title="Avg Order Value"
            value={lifecycle?.aov != null ? "€" + (lifecycle.aov as number).toFixed(2) : "--"}
            status={lifecycle?.aov != null ? pctStatus(lifecycle.aov as number, 45, 30) : "neutral"}
            description="Target: >€45"
          />
        </div>
      </div>

      {/* Email Performance */}
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
          Email Performance
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title="Email Open Rate"
            value={emailOpenRate != null ? emailOpenRate.toFixed(1) + "%" : "--"}
            status={pctStatus(emailOpenRate, 22, 15)}
            description="Benchmark: 18-25%"
          />
          <KpiCard
            title="Revenue per Send"
            value={emailRevPerSend != null ? "€" + emailRevPerSend.toFixed(3) : "--"}
            status={pctStatus(emailRevPerSend, 0.40, 0.20)}
            description="Target: >€0.40/send"
          />
          <KpiCard
            title="Active Subscribers (90d)"
            value={activeSubscribers != null ? activeSubscribers.toLocaleString() : "--"}
            status="neutral"
            description="Opened or clicked in last 90d"
          />
          <KpiCard
            title="Churn Rate (30d)"
            value={churnRate30d != null ? churnRate30d.toFixed(1) + "%" : "--"}
            status={churnRate30d != null ? pctStatus(churnRate30d, 15, 25, false) : "neutral"}
            description="Target: <15%"
          />
        </div>
      </div>

      {/* Retention */}
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
          Retention
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <KpiCard
            title="Repeat Purchase Rate"
            value={repeatPurchaseRate != null ? repeatPurchaseRate.toFixed(1) + "%" : "--"}
            status={pctStatus(repeatPurchaseRate, 35, 20)}
            description="Target: >35% | Benchmark: 30-40%"
          />
          <KpiCard
            title="LTV:CAC Ratio"
            value={lifecycle?.ltv_cac_ratio != null ? (lifecycle.ltv_cac_ratio as number).toFixed(1) + ":1" : "--"}
            status={lifecycle?.ltv_cac_ratio != null ? pctStatus(lifecycle.ltv_cac_ratio as number, 3.0, 2.0) : "neutral"}
            description="Target: ≥3.0:1"
          />
          <KpiCard
            title="New vs Returning Split"
            value={lifecycle?.returning_pct != null ? (lifecycle.returning_pct as number).toFixed(0) + "% returning" : "--"}
            status={pctStatus(lifecycle?.returning_pct as number | undefined, 40, 25)}
            description="Target: >40% returning"
          />
        </div>
      </div>

      {/* Agent analysis */}
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
            <p className="text-sm text-muted-foreground italic">
              No data yet. CRM agent runs at 06:30 daily.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
