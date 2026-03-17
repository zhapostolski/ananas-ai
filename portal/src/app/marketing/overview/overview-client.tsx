"use client";

import { StatCard } from "@/components/dashboard/stat-card";
import { AgentStatus } from "@/components/dashboard/agent-status";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RevenueAreaChart, SessionsLineChart } from "@/components/dashboard/overview-charts";
import { useT } from "@/lib/i18n";
import { useTranslateContent } from "@/lib/i18n/use-translate-content";

interface AgentRow {
  id: string;
  labelKey: string;
  lastRun?: string;
  status: "ok" | "error" | "skipped";
  summary?: string;
}

interface Props {
  agentData: AgentRow[];
  summaryText: string | null;
  revenueData: { label: string; value: number }[];
  sessionsData: { label: string; value: number }[];
  briefRunAt: string | null;
  briefJson: {
    sessions_7d?: unknown;
    gmv_7d?: unknown;
    roas?: unknown;
    google_rating?: unknown;
    sessions_delta?: number;
    gmv_delta?: number;
  };
}

function dbStr(val: unknown, fallback = "--"): string {
  if (val == null || val === "") return fallback;
  return String(val);
}

function formatDate(val: string): string {
  try {
    return new Date(val).toLocaleString("en-US", {
      month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    });
  } catch {
    return val;
  }
}

export function OverviewClient({ agentData, summaryText, revenueData, sessionsData, briefRunAt, briefJson }: Props) {
  const t = useT();
  const { translated: translatedSummary, translating } = useTranslateContent(summaryText);

  const translatedAgents = agentData.map((a) => ({
    ...a,
    label: t[a.labelKey as keyof typeof t] ?? a.labelKey,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{t.page_overview}</h1>
          <p className="text-sm text-muted-foreground">{t.overview_subtitle}</p>
        </div>
        {briefRunAt && (
          <Badge variant="outline">
            {t.last_updated}: {formatDate(briefRunAt)}
          </Badge>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title={t.overview_sessions_7d} value={dbStr(briefJson.sessions_7d)}
          delta={briefJson.sessions_delta} deltaLabel="WoW" />
        <StatCard title={t.overview_revenue_7d} value={dbStr(briefJson.gmv_7d)}
          delta={briefJson.gmv_delta} deltaLabel="WoW" />
        <StatCard title={t.overview_blended_roas} value={dbStr(briefJson.roas)} description="" />
        <StatCard title={t.overview_google_business} value={dbStr(briefJson.google_rating, "--")} description="" />
      </div>

      {(revenueData.length > 0 || sessionsData.length > 0) && (
        <div className="grid gap-6 lg:grid-cols-2">
          {revenueData.length > 0 && <RevenueAreaChart data={revenueData} />}
          {sessionsData.length > 0 && <SessionsLineChart data={sessionsData} />}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">{t.overview_daily_summary}</CardTitle>
            </CardHeader>
            <CardContent>
              {summaryText ? (
                <div className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">
                  {translating ? (
                    <span className="text-muted-foreground italic">{t.translating}</span>
                  ) : translatedSummary}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground italic">{t.overview_no_summary}</p>
              )}
            </CardContent>
          </Card>
        </div>

        <div>
          <AgentStatus agents={translatedAgents} title={t.overview_agent_status} lastRunLabel={t.last_run} />
        </div>
      </div>
    </div>
  );
}
