import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function FinancePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Finance</h1>
        <p className="text-sm text-muted-foreground">
          P&L overview, margin by category, budget vs actual
        </p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Coming Soon</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Finance modules will be added after department head meetings.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
