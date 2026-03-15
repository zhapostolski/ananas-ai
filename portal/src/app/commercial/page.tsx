import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getLatestOutput } from "@/lib/db";
import { formatDate, dbStr } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function CommercialPage() {
  const categoryLatest = getLatestOutput("category-growth-agent");
  const supplierLatest = getLatestOutput("supplier-intelligence-agent");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Commercial Overview</h1>
        <p className="text-sm text-muted-foreground">
          Category growth, supplier intelligence, and product feed health
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Category Growth</CardTitle>
            {!!categoryLatest?.run_at && (
              <Badge variant="outline" className="text-xs">
                {formatDate(categoryLatest.run_at as string)}
              </Badge>
            )}
          </CardHeader>
          <CardContent>
            {categoryLatest?.summary_text ? (
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {categoryLatest.summary_text as string}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground italic">No data yet.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Supplier Intelligence</CardTitle>
            {!!supplierLatest?.run_at && (
              <Badge variant="outline" className="text-xs">
                {formatDate(supplierLatest.run_at as string)}
              </Badge>
            )}
          </CardHeader>
          <CardContent>
            {supplierLatest?.summary_text ? (
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {supplierLatest.summary_text as string}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground italic">No data yet.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
