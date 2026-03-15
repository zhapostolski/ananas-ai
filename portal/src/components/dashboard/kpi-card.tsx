import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus, AlertTriangle } from "lucide-react";

export type ThresholdStatus = "green" | "yellow" | "red" | "critical" | "neutral";

interface KpiCardProps {
  title: string;
  value: string | null | undefined;
  description?: string;
  delta?: number | null;
  deltaLabel?: string;
  status?: ThresholdStatus;
  badge?: string;
  /** Small label shown below value (e.g. "POAS", "ROAS") */
  unit?: string;
  /** When true, renders a larger card with more prominent value */
  large?: boolean;
}

function statusColors(status: ThresholdStatus | undefined) {
  switch (status) {
    case "green":
      return {
        border: "border-green-200 dark:border-green-900",
        badge: "bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400",
        indicator: "#22c55e",
      };
    case "yellow":
      return {
        border: "border-yellow-200 dark:border-yellow-900",
        badge: "bg-yellow-100 text-yellow-700 dark:bg-yellow-950 dark:text-yellow-400",
        indicator: "#eab308",
      };
    case "red":
    case "critical":
      return {
        border: "border-red-200 dark:border-red-900",
        badge: "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400",
        indicator: "#ef4444",
      };
    default:
      return {
        border: "border-border",
        badge: "bg-muted text-muted-foreground",
        indicator: undefined,
      };
  }
}

export function KpiCard({
  title,
  value,
  description,
  delta,
  deltaLabel,
  status,
  badge,
  unit,
  large = false,
}: KpiCardProps) {
  const colors = statusColors(status);
  const isCritical = status === "critical";

  const deltaPositive = delta !== null && delta !== undefined && delta > 0;
  const deltaNegative = delta !== null && delta !== undefined && delta < 0;

  return (
    <div
      className={cn(
        "rounded-xl border bg-card p-4 flex flex-col gap-1 relative overflow-hidden transition-colors",
        colors.border
      )}
    >
      {/* Status indicator bar at top */}
      {colors.indicator && (
        <div
          className="absolute top-0 left-0 right-0 h-0.5"
          style={{ backgroundColor: colors.indicator }}
        />
      )}

      <div className="flex items-start justify-between gap-2">
        <p className="text-xs font-medium text-muted-foreground">{title}</p>
        {badge && (
          <span className={cn("rounded-full px-2 py-0.5 text-[10px] font-semibold shrink-0", colors.badge)}>
            {badge}
          </span>
        )}
        {isCritical && !badge && (
          <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-red-500" />
        )}
      </div>

      <div className={cn("font-bold tabular-nums", large ? "text-3xl" : "text-2xl")}>
        {value ?? "--"}
      </div>

      {unit && (
        <p className="text-xs text-muted-foreground -mt-0.5">{unit}</p>
      )}

      {(delta !== null && delta !== undefined) && (
        <div className="flex items-center gap-1 mt-0.5">
          {deltaPositive ? (
            <TrendingUp className="h-3 w-3 text-green-500" />
          ) : deltaNegative ? (
            <TrendingDown className="h-3 w-3 text-red-500" />
          ) : (
            <Minus className="h-3 w-3 text-muted-foreground" />
          )}
          <span
            className={cn(
              "text-xs font-medium",
              deltaPositive ? "text-green-600" : deltaNegative ? "text-red-600" : "text-muted-foreground"
            )}
          >
            {delta > 0 ? "+" : ""}{delta.toFixed(1)}% {deltaLabel ?? "WoW"}
          </span>
        </div>
      )}

      {description && (
        <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
      )}
    </div>
  );
}

/** A full-width gap card for missing data or critical alerts */
export function KpiAlertBanner({
  title,
  message,
  status = "critical",
}: {
  title: string;
  message: string;
  status?: "critical" | "yellow";
}) {
  const colors = statusColors(status);
  return (
    <div className={cn("rounded-xl border p-4 flex items-start gap-3", colors.border)}>
      <AlertTriangle className={cn("h-4 w-4 shrink-0 mt-0.5", status === "critical" ? "text-red-500" : "text-yellow-500")} />
      <div>
        <p className={cn("text-sm font-semibold", status === "critical" ? "text-red-700 dark:text-red-400" : "text-yellow-700 dark:text-yellow-400")}>
          {title}
        </p>
        <p className="text-xs text-muted-foreground mt-0.5">{message}</p>
      </div>
    </div>
  );
}
