"use client";

import { ResponsiveContainer, LineChart, Line, Tooltip } from "recharts";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface SparklineCardProps {
  title: string;
  value: string;
  delta?: number;
  deltaLabel?: string;
  description?: string;
  data?: number[];
  icon?: React.ReactNode;
  iconBg?: string;
  status?: "ok" | "warning" | "critical";
}

export function SparklineCard({
  title,
  value,
  delta,
  deltaLabel,
  description,
  data,
  icon,
  iconBg = "#FE5000",
  status = "ok",
}: SparklineCardProps) {
  const chartData = (data ?? []).map((v, i) => ({ i, v }));

  const trendIcon =
    delta == null ? null : delta > 0 ? (
      <TrendingUp className="h-3 w-3" />
    ) : delta < 0 ? (
      <TrendingDown className="h-3 w-3" />
    ) : (
      <Minus className="h-3 w-3" />
    );

  const trendColor =
    delta == null
      ? ""
      : delta > 0
      ? "text-green-500"
      : delta < 0
      ? "text-red-400"
      : "text-muted-foreground";

  return (
    <div
      className={cn(
        "rounded-xl border bg-card p-4 transition-shadow hover:shadow-md",
        status === "critical" && "border-red-300 bg-red-50/40 dark:bg-red-950/20",
        status === "warning" && "border-yellow-300 bg-yellow-50/40 dark:bg-yellow-950/20"
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {icon && (
            <div
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-white"
              style={{ backgroundColor: iconBg }}
            >
              {icon}
            </div>
          )}
          <div className="min-w-0">
            <p className="text-xs font-medium text-muted-foreground truncate">
              {title}
            </p>
            <p className="mt-0.5 text-xl font-bold leading-none">{value}</p>
          </div>
        </div>

        {chartData.length > 0 && (
          <div className="ml-2 h-10 w-20 shrink-0">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <Line
                  type="monotone"
                  dataKey="v"
                  stroke="#FE5000"
                  strokeWidth={1.5}
                  dot={false}
                  isAnimationActive={false}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null;
                    return (
                      <div className="rounded border bg-card px-2 py-1 text-xs shadow">
                        {payload[0].value}
                      </div>
                    );
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="mt-3 flex items-center justify-between">
        {delta != null && (
          <span
            className={cn("flex items-center gap-1 text-xs font-medium", trendColor)}
          >
            {trendIcon}
            {delta > 0 ? "+" : ""}
            {delta}%{deltaLabel ? ` ${deltaLabel}` : ""}
          </span>
        )}
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
    </div>
  );
}
