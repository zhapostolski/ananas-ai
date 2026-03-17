"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DateRangeFilter, type DateRange, resolveDateRange } from "@/components/dashboard/date-range-filter";
import { formatDate, stripMarkdown } from "@/lib/utils";
import { useT } from "@/lib/i18n";
import { useTranslateContent } from "@/lib/i18n/use-translate-content";

interface Journey {
  status: string;
  priority: string;
  est_impact?: string;
}

interface AgentOutput {
  run_at: string;
  output_json: Record<string, unknown>;
  summary_text: string | null;
}

function journeyStatusColor(status: string) {
  if (status === "live") return "text-green-600 dark:text-green-400";
  if (status === "partial") return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
}

function priorityBadge(priority: string) {
  if (priority === "critical") return "border-red-300 text-red-700 dark:text-red-400";
  if (priority === "high") return "border-yellow-300 text-yellow-700 dark:text-yellow-400";
  return "text-muted-foreground";
}

const JOURNEY_LABELS: Record<string, string> = {
  "cart-recovery": "Cart Recovery",
  "welcome-series": "Welcome Series",
  "churn-prevention": "Churn Prevention",
  "winback": "Win-back",
  "post-purchase": "Post Purchase",
  "browse-abandonment": "Browse Abandonment",
};

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

  const json = latest?.output_json ?? null;
  const journeys = (json?.journeys as Record<string, Journey> | undefined) ?? {};
  const journeyEntries = Object.entries(journeys);
  const automationsLive = json?.automations_live as number | undefined;
  const automationsTotal = json?.automations_total as number | undefined;
  const priorityAction = json?.priority_action as string | undefined;
  const crmPlatform = json?.crm_platform as string | undefined;

  const { translated: translatedSummary, translating } = useTranslateContent(
    latest?.summary_text ? stripMarkdown(latest.summary_text) : null
  );

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

      {/* Automation summary */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border bg-card p-4">
          <p className="text-xs text-muted-foreground uppercase tracking-wide font-medium mb-1">Automations Live</p>
          <p className="text-3xl font-bold">
            {automationsLive != null ? automationsLive : "--"}
            {automationsTotal != null && (
              <span className="text-base font-normal text-muted-foreground"> / {automationsTotal}</span>
            )}
          </p>
          {automationsLive === 0 && (
            <p className="text-xs text-red-600 dark:text-red-400 mt-1">No active automations</p>
          )}
        </div>
        <div className="rounded-xl border bg-card p-4">
          <p className="text-xs text-muted-foreground uppercase tracking-wide font-medium mb-1">CRM Platform</p>
          <p className="text-lg font-semibold">{crmPlatform ?? "--"}</p>
          <p className="text-xs text-muted-foreground mt-1">Current integration</p>
        </div>
        <div className="rounded-xl border bg-card p-4">
          <p className="text-xs text-muted-foreground uppercase tracking-wide font-medium mb-1">Journey Coverage</p>
          <p className="text-3xl font-bold">
            {journeyEntries.filter(([, j]) => j.status === "live").length}
            <span className="text-base font-normal text-muted-foreground"> / {journeyEntries.length}</span>
          </p>
          <p className="text-xs text-muted-foreground mt-1">Journeys active</p>
        </div>
      </div>

      {/* Journey status table */}
      {journeyEntries.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Lifecycle Journeys</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="divide-y text-sm">
              {journeyEntries.map(([key, journey]) => (
                <div key={key} className="flex items-center justify-between py-2.5 gap-4">
                  <div className="flex items-center gap-3 min-w-0">
                    <span className={`font-medium ${journeyStatusColor(journey.status)}`}>
                      {journey.status === "live" ? "●" : "○"}
                    </span>
                    <span className="font-medium">{JOURNEY_LABELS[key] ?? key}</span>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    {journey.est_impact && (
                      <span className="text-xs text-muted-foreground">Impact: {journey.est_impact}</span>
                    )}
                    <Badge variant="outline" className={`text-xs ${priorityBadge(journey.priority)}`}>
                      {journey.priority}
                    </Badge>
                    <span className={`text-xs font-medium ${journeyStatusColor(journey.status)}`}>
                      {journey.status.replace(/_/g, " ")}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Priority action */}
      {priorityAction && (
        <div className="rounded-xl border border-red-200 dark:border-red-900 bg-red-50/50 dark:bg-red-950/30 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-red-700 dark:text-red-400 mb-1">Priority Action</p>
          <p className="text-sm text-foreground">{priorityAction}</p>
        </div>
      )}

      {/* Agent analysis */}
      <Card>
        <CardHeader><CardTitle className="text-sm font-medium">{t.agent_analysis}</CardTitle></CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground italic">{t.loading}</p>
          ) : latest?.summary_text ? (
            <div className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">
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
