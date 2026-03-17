import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string;
  delta?: number;
  deltaLabel?: string;
  description?: string;
  status?: "ok" | "warning" | "critical";
}

export function StatCard({
  title,
  value,
  delta,
  deltaLabel,
  description,
  status = "ok",
}: StatCardProps) {
  const trendIcon =
    delta == null ? null : delta > 0 ? (
      <TrendingUp className="h-3.5 w-3.5" />
    ) : delta < 0 ? (
      <TrendingDown className="h-3.5 w-3.5" />
    ) : (
      <Minus className="h-3.5 w-3.5" />
    );

  const trendColor =
    delta == null
      ? ""
      : delta > 0
      ? "text-green-600"
      : delta < 0
      ? "text-red-500"
      : "text-muted-foreground";

  return (
    <Card
      className={cn(
        "transition-shadow hover:shadow-md",
        status === "critical" && "border-red-200 dark:border-red-900 bg-red-50/50 dark:bg-red-950/30",
        status === "warning" && "border-yellow-200 dark:border-yellow-900 bg-yellow-50/50 dark:bg-yellow-950/30"
      )}
    >
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-end justify-between">
          <span className="text-2xl font-bold">{value}</span>
          {delta != null && (
            <span className={cn("flex items-center gap-1 text-xs font-medium", trendColor)}>
              {trendIcon}
              {delta > 0 ? "+" : ""}
              {delta}%{deltaLabel ? ` ${deltaLabel}` : ""}
            </span>
          )}
        </div>
        {description && (
          <p className="mt-1 text-xs text-muted-foreground">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}
