"use client";

import { useState, useEffect } from "react";
import { KpiCard, KpiAlertBanner } from "@/components/dashboard/kpi-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DateRangeFilter, type DateRange, resolveDateRange } from "@/components/dashboard/date-range-filter";
import { formatDate } from "@/lib/utils";
import { useT } from "@/lib/i18n";
import { useTranslateContent } from "@/lib/i18n/use-translate-content";

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
  const t = useT();
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

  const { translated: translatedSummary, translating } = useTranslateContent(latest?.summary_text);

  type Priority = "CRITICAL" | "HIGH" | "MEDIUM";
  const actionItems: { done: boolean; label: string; priority: Priority }[] = [
    { done: !!gb?.status, label: t.rep_action_claim_gbp, priority: "HIGH" },
    { done: gbUnanswered === 0, label: t.rep_action_respond, priority: "HIGH" },
    { done: tpClaimed, label: t.rep_action_claim_tp, priority: "HIGH" },
    { done: false, label: t.rep_action_review_email, priority: "HIGH" },
    { done: false, label: t.rep_action_weekly_review, priority: "MEDIUM" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold">{t.page_reputation}</h1>
          <p className="text-sm text-muted-foreground">{t.rep_subtitle}</p>
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
          title={t.rep_critical_trustpilot}
          message={t.rep_critical_trustpilot_detail}
          status="critical"
        />
        {!tpClaimed && (
          <KpiAlertBanner
            title={t.rep_critical_unclaimed}
            message={t.rep_critical_unclaimed_detail}
            status="critical"
          />
        )}
      </div>

      {/* Google Business KPIs - primary */}
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
          {t.rep_google_section}
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title={t.rep_rating}
            value={gbRating != null ? gbRating.toFixed(1) + " / 5.0" : "--"}
            status={ratingStatus(gbRating)}
            description={t.rep_gbp_rating_desc}
            large
          />
          <KpiCard
            title={t.rep_total_reviews}
            value={gbTotal != null ? gbTotal.toLocaleString() : "--"}
            status="neutral"
          />
          <KpiCard
            title={t.rep_unanswered}
            value={gbUnanswered != null ? gbUnanswered.toString() : "--"}
            status={gbUnanswered != null ? (gbUnanswered > 10 ? "red" : gbUnanswered > 5 ? "yellow" : "green") : "neutral"}
            description={t.rep_respond_sla}
          />
          <KpiCard
            title={t.rep_gbp_status}
            value={gb?.status as string ?? t.rep_not_configured}
            status={gb?.status ? "neutral" : "yellow"}
          />
        </div>
      </div>

      {/* Trustpilot KPIs */}
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
          {t.rep_trustpilot_section}
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title={t.rep_rating}
            value={tpRating != null ? tpRating.toFixed(1) + " / 5.0" : "2.0 / 5.0"}
            status={ratingStatus(tpRating ?? 2.0)}
            badge="CRITICAL"
            description={t.rep_tp_rating_desc}
            large
          />
          <KpiCard
            title={t.rep_total_reviews}
            value={tpCount != null ? tpCount.toLocaleString() : "--"}
            status="neutral"
          />
          <KpiCard
            title={t.rep_response_rate}
            value={tpResponseRate != null ? tpResponseRate.toFixed(0) + "%" : "0%"}
            status={tpResponseRate != null && tpResponseRate >= 80 ? "green" : tpResponseRate != null && tpResponseRate >= 50 ? "yellow" : "red"}
            description={t.rep_target_80}
          />
          <KpiCard
            title={t.rep_profile_status}
            value={tpClaimed ? t.rep_claimed : t.rep_unclaimed}
            status={tpClaimed ? "green" : "critical"}
            badge={tpClaimed ? undefined : t.action_required}
          />
        </div>
      </div>

      {/* Action checklist */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">{t.rep_action_plan}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            {actionItems.map((item, i) => (
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
          <CardTitle className="text-sm font-medium">{t.agent_analysis}</CardTitle>
        </CardHeader>
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
