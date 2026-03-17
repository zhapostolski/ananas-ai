"use client";

import { useState, useEffect } from "react";
import { KpiCard, KpiAlertBanner } from "@/components/dashboard/kpi-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DateRangeFilter, type DateRange, resolveDateRange } from "@/components/dashboard/date-range-filter";
import { formatDate } from "@/lib/utils";
import { useT } from "@/lib/i18n";
import { useTranslateContent } from "@/lib/i18n/use-translate-content";

function pctStatus(val: number | null | undefined, green: number, yellow: number, higherIsBetter = true) {
  if (val == null) return "neutral" as const;
  if (higherIsBetter) {
    return val >= green ? "green" : val >= yellow ? "yellow" : "red";
  } else {
    return val <= green ? "green" : val <= yellow ? "yellow" : "red";
  }
}

interface AgentOutput {
  run_at: string;
  output_json: Record<string, unknown>;
  summary_text: string | null;
}

export default function CrmPage() {
  const t = useT();
  const [dateRange, setDateRange] = useState<DateRange>({ preset: "last_7d" });
  const [latest, setLatest] = useState<AgentOutput | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const { from, to } = resolveDateRange(dateRange);
    const fmt = (d: Date) => d.toISOString().slice(0, 10);
    const params = new URLSearchParams({ agent: "crm-lifecycle-agent" });
    params.set("from", fmt(from));
    params.set("to", fmt(to));

    fetch("/api/marketing/agent-output?" + params)
      .then((r) => r.json())
      .then((d) => { setLatest(d.latest ?? null); setLoading(false); })
      .catch(() => setLoading(false));
  }, [dateRange]);

  const json = latest?.output_json as Record<string, unknown> | null ?? null;
  const email = json?.email as Record<string, unknown> | undefined;
  const lifecycle = json?.lifecycle as Record<string, unknown> | undefined;

  const cartAbandonmentRate = email?.cart_abandonment_rate as number | undefined;
  const cartRecoveryRate = email?.cart_recovery_rate as number | undefined;
  const repeatPurchaseRate = lifecycle?.repeat_purchase_rate as number | undefined;
  const activeSubscribers = email?.active_subscribers as number | undefined;
  const emailOpenRate = email?.open_rate as number | undefined;
  const emailRevPerSend = email?.revenue_per_send as number | undefined;
  const churnRate30d = lifecycle?.churn_rate_30d as number | undefined;
  const { translated: translatedSummary, translating } = useTranslateContent(latest?.summary_text);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold">{t.page_crm}</h1>
          <p className="text-sm text-muted-foreground">{t.crm_subtitle}</p>
        </div>
        <div className="flex items-center gap-3">
          {!!latest?.run_at && (
            <Badge variant="outline">{formatDate(latest.run_at)}</Badge>
          )}
          <DateRangeFilter value={dateRange} onChange={setDateRange} />
        </div>
      </div>

      <KpiAlertBanner
        title={t.crm_alert_no_automations}
        message={t.crm_alert_no_automations_detail}
        status="critical"
      />

      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">{t.crm_cart_section}</p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <KpiCard title={t.crm_cart_abandonment}
            value={cartAbandonmentRate != null ? cartAbandonmentRate.toFixed(1) + "%" : "--"}
            status={cartAbandonmentRate != null ? pctStatus(cartAbandonmentRate, 65, 75, false) : "neutral"}
            description={t.crm_target_35} />
          <KpiCard title={t.crm_cart_recovery}
            value={cartRecoveryRate != null ? cartRecoveryRate.toFixed(1) + "%" : "0%"}
            status={cartRecoveryRate == null || cartRecoveryRate === 0 ? "critical" : pctStatus(cartRecoveryRate, 20, 10)}
            description={cartRecoveryRate === 0 || cartRecoveryRate == null ? t.crm_no_recovery : t.crm_target_15}
            badge={cartRecoveryRate === 0 || cartRecoveryRate == null ? t.crm_no_automation_badge : undefined} />
          <KpiCard title={t.crm_aov}
            value={lifecycle?.aov != null ? "€" + (lifecycle.aov as number).toFixed(2) : "--"}
            status={lifecycle?.aov != null ? pctStatus(lifecycle.aov as number, 45, 30) : "neutral"}
            description={t.target + ": >€45"} />
        </div>
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">{t.crm_email_section}</p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard title={t.crm_email_open_rate}
            value={emailOpenRate != null ? emailOpenRate.toFixed(1) + "%" : "--"}
            status={pctStatus(emailOpenRate, 22, 15)} />
          <KpiCard title={t.crm_revenue_per_send}
            value={emailRevPerSend != null ? "€" + emailRevPerSend.toFixed(3) : "--"}
            status={pctStatus(emailRevPerSend, 0.40, 0.20)} />
          <KpiCard title={t.crm_active_subscribers}
            value={activeSubscribers != null ? activeSubscribers.toLocaleString() : "--"}
            status="neutral" description={t.crm_subscribers_desc} />
          <KpiCard title={t.crm_churn_rate}
            value={churnRate30d != null ? churnRate30d.toFixed(1) + "%" : "--"}
            status={churnRate30d != null ? pctStatus(churnRate30d, 15, 25, false) : "neutral"}
            description={t.crm_retention_target} />
        </div>
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">{t.crm_retention_section}</p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <KpiCard title={t.crm_repeat_purchase}
            value={repeatPurchaseRate != null ? repeatPurchaseRate.toFixed(1) + "%" : "--"}
            status={pctStatus(repeatPurchaseRate, 35, 20)} description={t.crm_repeat_target} />
          <KpiCard title={t.crm_ltv_cac}
            value={lifecycle?.ltv_cac_ratio != null ? (lifecycle.ltv_cac_ratio as number).toFixed(1) + ":1" : "--"}
            status={lifecycle?.ltv_cac_ratio != null ? pctStatus(lifecycle.ltv_cac_ratio as number, 3.0, 2.0) : "neutral"}
            description={t.target + ": 3.0:1"} />
          <KpiCard title={t.crm_new_vs_returning}
            value={lifecycle?.returning_pct != null ? (lifecycle.returning_pct as number).toFixed(0) + "% returning" : "--"}
            status={pctStatus(lifecycle?.returning_pct as number | undefined, 40, 25)} />
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-sm font-medium">{t.agent_analysis}</CardTitle></CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground italic">{t.loading}</p>
          ) : latest?.summary_text ? (
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {translating ? <span className="text-muted-foreground italic">{t.translating}</span> : translatedSummary}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">{t.no_data}</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
