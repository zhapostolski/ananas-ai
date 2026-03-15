import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function LogisticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Logistics</h1>
        <p className="text-sm text-muted-foreground">
          Fulfillment rates, delivery SLAs, returns
        </p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Coming Soon</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Logistics modules will be added after department head meetings.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
