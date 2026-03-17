"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { DateRangeFilter, type DateRange } from "@/components/dashboard/date-range-filter";
import { RevenueAreaChart, SessionsLineChart } from "@/components/dashboard/overview-charts";
import { useT } from "@/lib/i18n";
import { useTranslateContent } from "@/lib/i18n/use-translate-content";

interface PerfData {
  run_at: string | null;
  summary_text: string | null;
  kpis: {
    total_paid_spend?: number;
    blended_roas?: number;
    ga4_revenue?: number;
    ga4_sessions?: number;
    ga4_conversion_rate_pct?: number;
    ga4_users?: number;
  };
  history: Array<{ date: string; sessions: number; revenue: number; paid_spend: number; blended_roas: number }>;
}

interface Ga4Channel {
  channel: string;
  sessions: number;
  revenue: number;
  users: number;
}

interface Ga4Data {
  sessions: number;
  users: number;
  revenue: number;
  conversionRate: number;
  channels: Ga4Channel[];
  startDate: string;
  endDate: string;
  error?: string;
}

function fmtEur(val: number | undefined | null): string {
  if (val == null) return "--";
  return "€" + val.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}
function fmtX(val: number | undefined | null): string {
  if (val == null) return "--";
  return val.toFixed(2) + "x";
}
function fmtPct(val: number | undefined | null): string {
  if (val == null) return "--";
  return val.toFixed(2) + "%";
}
function fmtNum(val: number | undefined | null): string {
  if (val == null) return "--";
  return val.toLocaleString("en-US");
}

function channelIcon(channel: string): string {
  const c = channel.toLowerCase();
  if (c.includes("organic search")) return "🔍";
  if (c.includes("paid search")) return "🎯";
  if (c.includes("paid social")) return "📘";
  if (c.includes("direct")) return "🔗";
  if (c.includes("email")) return "✉️";
  if (c.includes("referral")) return "🔄";
  if (c.includes("display")) return "🖼️";
  if (c.includes("affiliates")) return "🤝";
  return "📊";
}

export default function PerformancePage() {
  const t = useT();
  const [dateRange, setDateRange] = useState<DateRange>({ preset: "last_7d" });
  const [data, setData] = useState<PerfData | null>(null);
  const [ga4, setGa4] = useState<Ga4Data | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const rangeParam = dateRange.preset === "custom" && dateRange.from && dateRange.to
      ? `${dateRange.from},${dateRange.to}`
      : dateRange.preset;

    Promise.all([
      fetch("/api/marketing/performance?range=" + rangeParam).then((r) => r.json()),
      fetch("/api/marketing/ga4?range=" + rangeParam).then((r) => r.json()),
    ]).then(([perf, ga4data]) => {
      setData(perf);
      setGa4(ga4data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [dateRange]);

  const kpis = data?.kpis ?? {};
  const history = data?.history ?? [];

  // Prefer live GA4 data over agent-output KPIs
  const sessions = ga4?.sessions ?? kpis.ga4_sessions;
  const users = ga4?.users ?? kpis.ga4_users;
  const revenue = ga4?.revenue ?? kpis.ga4_revenue;
  const convRate = ga4?.conversionRate ?? kpis.ga4_conversion_rate_pct;

  const roasStatus =
    !kpis.blended_roas ? "neutral"
    : kpis.blended_roas >= 5 ? "green"
    : kpis.blended_roas >= 3 ? "yellow"
    : "red";

  const cvrStatus =
    !convRate ? "neutral"
    : convRate > 2.5 ? "green"
    : convRate > 1.5 ? "yellow"
    : "red";

  const revenueData = history.map((d) => ({ label: d.date.slice(5), value: d.revenue }));
  const sessionsData = history.map((d) => ({ label: d.date.slice(5), value: d.sessions }));

  const channels = ga4?.channels ?? [];
  const { translated: translatedSummary, translating } = useTranslateContent(data?.summary_text);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold">{t.page_performance}</h1>
          <p className="text-sm text-muted-foreground">{t.performance_subtitle}</p>
        </div>
        <div className="flex items-center gap-3">
          {data?.run_at && (
            <Badge variant="outline" className="text-xs">
              Last run: {new Date(data.run_at).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
            </Badge>
          )}
          <DateRangeFilter value={dateRange} onChange={setDateRange} />
        </div>
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">{t.performance_ga4_section}</p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard title={t.performance_revenue} value={fmtEur(revenue)} status="neutral" description={t.performance_all_channels} />
          <KpiCard title={t.performance_sessions} value={fmtNum(sessions)} status="neutral" />
          <KpiCard title={t.performance_users} value={fmtNum(users)} status="neutral" />
          <KpiCard title={t.performance_conversion_rate} value={fmtPct(convRate)} status={cvrStatus}
            badge={cvrStatus === "green" ? t.good : cvrStatus === "red" ? t.below_target : undefined}
            description={t.target + ": >2.5%"} />
        </div>
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">{t.performance_paid_section}</p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard title={t.performance_total_spend} value={fmtEur(kpis.total_paid_spend)} status="neutral" description={t.performance_all_paid} />
          <KpiCard title={t.performance_blended_roas} value={fmtX(kpis.blended_roas)} status={roasStatus}
            badge={roasStatus === "green" ? t.on_target : roasStatus === "red" ? t.below_target : undefined}
            description={t.target + ": >5.0x"} />
          <KpiCard title={t.performance_poas} value="--" status="neutral" description={t.performance_poas_desc} badge={t.phase_2} />
        </div>
      </div>

      {/* Trend charts */}
      {(revenueData.length > 0 || sessionsData.length > 0) && (
        <div className="grid gap-6 lg:grid-cols-2">
          {revenueData.length > 0 && <RevenueAreaChart data={revenueData} />}
          {sessionsData.length > 0 && <SessionsLineChart data={sessionsData} />}
        </div>
      )}

      {/* Channel breakdown - live from GA4 */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-medium">{t.channel_breakdown}</CardTitle>
          {ga4 && !ga4.error && (
            <span className="text-xs text-muted-foreground">
              {ga4.startDate} to {ga4.endDate} - {t.live_ga4}
            </span>
          )}
        </CardHeader>
        <CardContent>
          {ga4?.error ? (
            <p className="text-sm text-muted-foreground italic">{ga4.error}</p>
          ) : channels.length > 0 ? (
            <div className="divide-y text-sm">
              {channels.map((ch) => {
                const sharePct = sessions ? ((ch.sessions / sessions) * 100).toFixed(1) : "0";
                return (
                  <div key={ch.channel} className="flex items-center justify-between py-2.5 gap-4">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="text-base leading-none">{channelIcon(ch.channel)}</span>
                      <span className="font-medium truncate">{ch.channel}</span>
                    </div>
                    <div className="flex items-center gap-6 shrink-0 text-xs text-muted-foreground">
                      <span className="w-24 text-right">{fmtNum(ch.sessions)} {t.performance_sessions.toLowerCase()}</span>
                      <span className="w-20 text-right">{fmtEur(ch.revenue)}</span>
                      <span className="w-12 text-right text-foreground font-medium">{sharePct}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : loading ? (
            <p className="text-sm text-muted-foreground italic">{t.performance_loading_channels}</p>
          ) : (
            <p className="text-sm text-muted-foreground italic">{t.performance_no_channel_data}</p>
          )}
        </CardContent>
      </Card>

      {data?.summary_text && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">{t.agent_analysis}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {translating ? <span className="text-muted-foreground italic">{t.translating}</span> : translatedSummary}
            </div>
          </CardContent>
        </Card>
      )}

      {loading && (
        <p className="text-sm text-muted-foreground italic">{t.loading}</p>
      )}
    </div>
  );
}
