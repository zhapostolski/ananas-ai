import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function HrAttendancePage() {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">Attendance</h1>
        <p className="text-sm text-muted-foreground">
          Leave requests, attendance tracking, and scheduling
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Pending Integration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 px-4 py-4 space-y-2">
            <p className="text-sm font-medium text-yellow-700 dark:text-yellow-400">
              Berry HR Integration Required
            </p>
            <p className="text-sm text-yellow-600 dark:text-yellow-500">
              Attendance data, leave requests, and scheduling will be pulled from Berry HR (tryberry.app) once the API integration is configured.
            </p>
            <p className="text-xs text-yellow-500 dark:text-yellow-600 mt-2">
              To proceed: provide Berry HR API credentials or enable API access in your Berry HR admin settings.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
