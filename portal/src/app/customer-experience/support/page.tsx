import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function SupportInsightsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Support Insights</h1>
        <p className="text-sm text-muted-foreground">
          Ticket volume, resolution time, satisfaction scores
        </p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Coming Soon</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Support data integration will be configured after department head meetings.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
