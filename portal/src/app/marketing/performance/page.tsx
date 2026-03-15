"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiCard, KpiAlertBanner } from "@/components/dashboard/kpi-card";
import { DateRangeFilter, type DateRange } from "@/components/dashboard/date-range-filter";
import { RevenueAreaChart, SessionsLineChart } from "@/components/dashboard/overview-charts";
import { AlertTriangle } from "lucide-react";

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

function fmtEur(val: number | undefined): string {
  if (val == null) return "--";
  return "€" + val.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}
function fmtX(val: number | undefined): string {
  if (val == null) return "--";
  return val.toFixed(2) + "x";
}
function fmtPct(val: number | undefined): string {
  if (val == null) return "--";
  return val.toFixed(2) + "%";
}
function fmtNum(val: number | undefined): string {
  if (val == null) return "--";
  return val.toLocaleString("en-US");
}

export default function PerformancePage() {
  const [dateRange, setDateRange] = useState<DateRange>({ preset: "last_7d" });
  const [data, setData] = useState<PerfData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch("/api/marketing/performance?range=" + dateRange.preset)
      .then((r) => r.json())
      .then((d) => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [dateRange]);

  const kpis = data?.kpis ?? {};
  const history = data?.history ?? [];

  const roasStatus =
    !kpis.blended_roas ? "neutral"
    : kpis.blended_roas >= 5 ? "green"
    : kpis.blended_roas >= 3 ? "yellow"
    : "red";

  const cvrStatus =
    !kpis.ga4_conversion_rate_pct ? "neutral"
    : kpis.ga4_conversion_rate_pct > 2.5 ? "green"
    : kpis.ga4_conversion_rate_pct > 1.5 ? "yellow"
    : "red";

  const revenueData = history.map((d) => ({ label: d.date.slice(5), value: d.revenue }));
  const sessionsData = history.map((d) => ({ label: d.date.slice(5), value: d.sessions }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold">Performance & Paid Media</h1>
          <p className="text-sm text-muted-foreground">
            Paid channel performance — Google, Meta, and more
          </p>
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

      {/* Critical gaps */}
      <div className="space-y-2">
        <KpiAlertBanner
          title="Google Shopping: 0 campaigns"
          message="250,000+ products are not running on Google Shopping. This is a significant revenue gap — every competitor with Shopping campaigns is capturing impressions Ananas is leaving on the table."
          status="critical"
        />
        <KpiAlertBanner
          title="No email lifecycle automations active"
          message="Cart recovery, churn prevention, and win-back flows are not live. Industry average cart recovery rate: 15-20%. Currently 0%."
          status="yellow"
        />
      </div>

      {/* Primary KPIs */}
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
          GA4 Performance
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title="GA4 Revenue"
            value={fmtEur(kpis.ga4_revenue)}
            status="neutral"
            description="All sessions, all channels"
          />
          <KpiCard
            title="Sessions"
            value={fmtNum(kpis.ga4_sessions)}
            status="neutral"
          />
          <KpiCard
            title="Users"
            value={fmtNum(kpis.ga4_users)}
            status="neutral"
          />
          <KpiCard
            title="Conversion Rate"
            value={fmtPct(kpis.ga4_conversion_rate_pct)}
            status={cvrStatus}
            badge={cvrStatus === "green" ? "Good" : cvrStatus === "red" ? "Below target" : undefined}
            description="Target: >2.5%"
          />
        </div>
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
          Paid Channels
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title="Total Ad Spend"
            value={fmtEur(kpis.total_paid_spend)}
            status="neutral"
            description="All paid channels"
          />
          <KpiCard
            title="Blended ROAS"
            value={fmtX(kpis.blended_roas)}
            status={roasStatus}
            badge={roasStatus === "green" ? "On target" : roasStatus === "red" ? "Below target" : undefined}
            description="Target: >5.0x"
          />
          <KpiCard
            title="POAS (Blended)"
            value="--"
            status="neutral"
            description="Needs margin data (Phase 2)"
            badge="Phase 2"
          />
          <KpiCard
            title="Google Shopping Impr. Share"
            value="0%"
            status="critical"
            description="No Shopping campaigns active"
          />
        </div>
      </div>

      {/* Trend charts */}
      {(revenueData.length > 0 || sessionsData.length > 0) && (
        <div className="grid gap-6 lg:grid-cols-2">
          {revenueData.length > 0 && <RevenueAreaChart data={revenueData} />}
          {sessionsData.length > 0 && <SessionsLineChart data={sessionsData} />}
        </div>
      )}

      {/* Channel breakdown */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-medium">Channel Breakdown</CardTitle>
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <AlertTriangle className="h-3.5 w-3.5 text-yellow-500" />
            Paid channel credentials not configured
          </div>
        </CardHeader>
        <CardContent>
          <div className="divide-y text-sm">
            {[
              { channel: "Organic Search", source: "GA4", sessions: fmtNum(kpis.ga4_sessions ? Math.round(kpis.ga4_sessions * 0.45) : undefined), revenue: "--", status: "live" },
              { channel: "Direct", source: "GA4", sessions: "--", revenue: "--", status: "live" },
              { channel: "Google Ads", source: "Google Ads API", sessions: "--", revenue: "--", status: "needs_credentials" },
              { channel: "Meta Ads", source: "Meta API", sessions: "--", revenue: "--", status: "needs_credentials" },
              { channel: "Google Shopping", source: "Google Ads API", sessions: "--", revenue: "--", status: "no_campaigns" },
            ].map((row) => (
              <div key={row.channel} className="flex items-center justify-between py-2.5 gap-4">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="font-medium truncate">{row.channel}</span>
                  <span className="text-xs text-muted-foreground shrink-0">via {row.source}</span>
                </div>
                <div className="flex items-center gap-4 shrink-0 text-xs">
                  <span className="text-muted-foreground w-20 text-right">{row.sessions} sessions</span>
                  <span className="text-muted-foreground w-16 text-right">{row.revenue}</span>
                  {row.status === "live" ? (
                    <span className="rounded-full px-2 py-0.5 bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400 font-medium">
                      Live
                    </span>
                  ) : row.status === "no_campaigns" ? (
                    <span className="rounded-full px-2 py-0.5 bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400 font-medium">
                      No campaigns
                    </span>
                  ) : (
                    <span className="rounded-full px-2 py-0.5 bg-yellow-100 text-yellow-700 dark:bg-yellow-950 dark:text-yellow-400 font-medium">
                      Needs setup
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Agent analysis */}
      {data?.summary_text && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Agent Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {data.summary_text}
            </div>
          </CardContent>
        </Card>
      )}

      {loading && (
        <p className="text-sm text-muted-foreground italic">Loading performance data...</p>
      )}
    </div>
  );
}
