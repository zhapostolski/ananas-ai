import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CustomerExperiencePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Customer Experience</h1>
        <p className="text-sm text-muted-foreground">
          Reviews, support insights, satisfaction trends
        </p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Coming Soon</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            CX modules will be configured after department head meetings.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
