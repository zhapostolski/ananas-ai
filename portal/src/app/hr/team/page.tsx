import { auth } from "@/lib/auth";
import { getAllPortalUsers } from "@/lib/db-portal";
import { ROLE_LABELS } from "@/lib/roles";
import type { Role } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function getInitials(name: string | null, email: string): string {
  if (name) {
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    return name.slice(0, 2).toUpperCase();
  }
  return email.slice(0, 2).toUpperCase();
}

export default async function HrTeamPage() {
  const session = await auth();
  const users = getAllPortalUsers();

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold">Team</h1>
        <p className="text-sm text-muted-foreground">
          All portal users with their roles and profile information from Azure AD
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Team Members ({users.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="divide-y">
            {users.map((user) => (
              <div key={user.id} className="flex items-center gap-4 py-3">
                <div className="shrink-0">
                  {user.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt={user.display_name ?? user.email}
                      className="h-10 w-10 rounded-full object-cover"
                    />
                  ) : (
                    <div
                      className="flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold text-white"
                      style={{ backgroundColor: user.avatar_color }}
                    >
                      {getInitials(user.display_name, user.email)}
                    </div>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {user.display_name ?? user.email}
                  </p>
                  <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                  {user.azure_job_title && (
                    <p className="text-xs text-muted-foreground">{user.azure_job_title}</p>
                  )}
                </div>

                <div className="text-right shrink-0 space-y-1">
                  <span
                    className="inline-block rounded-full px-2 py-0.5 text-xs font-medium text-white"
                    style={{ backgroundColor: "#FE5000" }}
                  >
                    {ROLE_LABELS[user.role as Role] ?? user.role}
                  </span>
                  {user.azure_department && (
                    <p className="text-xs text-muted-foreground">{user.azure_department}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Data Sources</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="rounded-lg bg-blue-50 dark:bg-blue-950/20 border border-blue-200 px-4 py-3">
            <p className="text-sm font-medium text-blue-700 dark:text-blue-400">Azure AD Connected</p>
            <p className="text-xs text-blue-600 dark:text-blue-500 mt-0.5">
              Profile photos, job titles, and departments are synced from Microsoft Azure on each login.
            </p>
          </div>
          <div className="rounded-lg bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 px-4 py-3">
            <p className="text-sm font-medium text-yellow-700 dark:text-yellow-400">Berry HR Pending Integration</p>
            <p className="text-xs text-yellow-600 dark:text-yellow-500 mt-0.5">
              Berry HR (tryberry.app) integration will add hire dates, contracts, attendance, and payroll data. API credentials needed to proceed.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
