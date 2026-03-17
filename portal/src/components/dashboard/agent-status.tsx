import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, XCircle, Clock } from "lucide-react";
import { timeAgo } from "@/lib/utils";

interface AgentStatusProps {
  agents: {
    id: string;
    label: string;
    lastRun?: string;
    status?: "ok" | "error" | "skipped";
    summary?: string;
  }[];
  title?: string;
  lastRunLabel?: string;
}

const STATUS_ICON = {
  ok: <CheckCircle2 className="h-4 w-4 text-green-500" />,
  error: <XCircle className="h-4 w-4 text-red-500" />,
  skipped: <Clock className="h-4 w-4 text-yellow-500" />,
};

export function AgentStatus({ agents, title = "Agent Status", lastRunLabel }: AgentStatusProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {agents.map((a) => (
          <div key={a.id} className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              {STATUS_ICON[a.status ?? "skipped"]}
              <div className="min-w-0">
                <div className="text-sm font-medium truncate">{a.label}</div>
                {a.summary && (
                  <div className="text-xs text-muted-foreground truncate max-w-xs">{a.summary}</div>
                )}
              </div>
            </div>
            <div className="shrink-0 text-xs text-muted-foreground">
              {a.lastRun ? timeAgo(a.lastRun) : "never"}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
