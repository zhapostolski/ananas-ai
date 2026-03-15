"use client";

import { useState, useEffect } from "react";
import { KpiCard, KpiAlertBanner } from "@/components/dashboard/kpi-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DateRangeFilter, type DateRange, resolveDateRange } from "@/components/dashboard/date-range-filter";
import { formatDate } from "@/lib/utils";

function ratingStatus(val: number | undefined) {
  if (val == null) return "neutral" as const;
  return val >= 4.0 ? "green" : val >= 3.5 ? "yellow" : "red";
}

interface AgentOutput {
  run_at: string;
  output_json: Record<string, unknown>;
  summary_text: string | null;
}

export default function ReputationPage() {
  const [dateRange, setDateRange] = useState<DateRange>({ preset: "last_7d" });
  const [latest, setLatest] = useState<AgentOutput | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const { from, to } = resolveDateRange(dateRange);
    const fmt = (d: Date) => d.toISOString().slice(0, 10);
    const params = new URLSearchParams({ agent: "reputation-agent" });
    params.set("from", fmt(from));
    params.set("to", fmt(to));

    fetch("/api/marketing/agent-output?" + params)
      .then((r) => r.json())
      .then((d) => { setLatest(d.latest ?? null); setLoading(false); })
      .catch(() => setLoading(false));
  }, [dateRange]);

  const json = latest?.output_json as Record<string, unknown> | null ?? null;
  const tp = json?.trustpilot as Record<string, unknown> | undefined;
  const gb = json?.google_business as Record<string, unknown> | undefined;

  const tpRating = tp?.average_rating as number | undefined;
  const tpCount = tp?.review_count as number | undefined;
  const tpResponseRate = tp?.response_rate as number | undefined;
  const tpClaimed = tp?.claimed === true;

  const gbRating = gb?.average_rating as number | undefined;
  const gbTotal = gb?.total_reviews as number | undefined;
  const gbUnanswered = gb?.unanswered_reviews as number | undefined;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold">Reputation</h1>
          <p className="text-sm text-muted-foreground">
            Trustpilot, Google Business, sentiment, and response tracking
          </p>
        </div>
        <div className="flex items-center gap-3">
          {!!latest?.run_at && (
            <Badge variant="outline">{formatDate(latest.run_at)}</Badge>
          )}
          <DateRangeFilter value={dateRange} onChange={setDateRange} />
        </div>
      </div>

      {/* Critical reputation alerts */}
      <div className="space-y-2">
        <KpiAlertBanner
          title="Trustpilot: 2.0 star rating - CRITICAL"
          message="Ananas has a 2.0/5.0 rating on Trustpilot. This is actively damaging brand trust and acquisition. The profile has not yet been claimed - claiming it is the immediate first step."
          status="critical"
        />
        {!tpClaimed && (
          <KpiAlertBanner
            title="Trustpilot profile not claimed"
            message="An unclaimed profile cannot respond to reviews, update business information, or run reputation campaigns. Claim at business.trustpilot.com."
            status="critical"
          />
        )}
      </div>

      {/* Trustpilot KPIs */}
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
          Trustpilot
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title="Trustpilot Rating"
            value={tpRating != null ? tpRating.toFixed(1) + " / 5.0" : "2.0 / 5.0"}
            status={ratingStatus(tpRating ?? 2.0)}
            badge="CRITICAL"
            description="Target: >4.0 within 6 months"
            large
          />
          <KpiCard
            title="Total Reviews"
            value={tpCount != null ? tpCount.toLocaleString() : "--"}
            status="neutral"
          />
          <KpiCard
            title="Response Rate"
            value={tpResponseRate != null ? tpResponseRate.toFixed(0) + "%" : "0%"}
            status={tpResponseRate != null && tpResponseRate >= 80 ? "green" : tpResponseRate != null && tpResponseRate >= 50 ? "yellow" : "red"}
            description="Target: >80% response rate"
          />
          <KpiCard
            title="Profile Status"
            value={tpClaimed ? "Claimed" : "Not claimed"}
            status={tpClaimed ? "green" : "critical"}
            badge={tpClaimed ? undefined : "Action required"}
            description={tpClaimed ? "Reputation campaigns possible" : "Claim at business.trustpilot.com"}
          />
        </div>
      </div>

      {/* Google Business KPIs */}
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
          Google Business Profile
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title="Google Rating"
            value={gbRating != null ? gbRating.toFixed(1) + " / 5.0" : "--"}
            status={ratingStatus(gbRating)}
            description="Target: >4.0"
            large
          />
          <KpiCard
            title="Total Reviews"
            value={gbTotal != null ? gbTotal.toLocaleString() : "--"}
            status="neutral"
          />
          <KpiCard
            title="Unanswered Reviews"
            value={gbUnanswered != null ? gbUnanswered.toString() : "--"}
            status={gbUnanswered != null ? (gbUnanswered > 10 ? "red" : gbUnanswered > 5 ? "yellow" : "green") : "neutral"}
            description="Respond within 24h"
          />
          <KpiCard
            title="GBP Setup"
            value={gb?.status as string ?? "Not configured"}
            status={gb?.status ? "neutral" : "yellow"}
            description="GBP_ACCOUNT_ID and GBP_LOCATION_ID needed"
          />
        </div>
      </div>

      {/* Action checklist */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Immediate Actions Required</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            {[
              { done: tpClaimed, label: "Claim Trustpilot business profile at business.trustpilot.com", priority: "CRITICAL" },
              { done: false, label: "Respond to all existing Trustpilot reviews (1-star priority)", priority: "CRITICAL" },
              { done: false, label: "Set up review invitation emails post-purchase", priority: "HIGH" },
              { done: !!gb?.status, label: "Configure Google Business Profile (GBP_ACCOUNT_ID + GBP_LOCATION_ID)", priority: "HIGH" },
              { done: gbUnanswered === 0, label: "Respond to all unanswered Google reviews", priority: "MEDIUM" },
            ].map((item, i) => (
              <div key={i} className="flex items-start gap-3 py-1.5 border-b last:border-0">
                <div className={`mt-0.5 h-4 w-4 shrink-0 rounded-full border-2 ${item.done ? "border-green-500 bg-green-500" : "border-muted-foreground"}`} />
                <div className="flex-1 min-w-0">
                  <span className={item.done ? "line-through text-muted-foreground" : ""}>{item.label}</span>
                </div>
                <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-bold ${
                  item.priority === "CRITICAL" ? "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400"
                  : item.priority === "HIGH" ? "bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-400"
                  : "bg-yellow-100 text-yellow-700 dark:bg-yellow-950 dark:text-yellow-400"
                }`}>
                  {item.priority}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Agent analysis */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Reputation Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground italic">Loading...</p>
          ) : latest?.summary_text ? (
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {latest.summary_text}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">
              No data for this period. Reputation agent runs at 07:00 daily.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
