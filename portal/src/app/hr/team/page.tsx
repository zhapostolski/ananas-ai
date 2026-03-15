"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ROLE_LABELS, isAdminRole } from "@/lib/roles";
import type { Role } from "@/types";
import { Loader2, RefreshCw } from "lucide-react";

interface TeamMember {
  id: number;
  email: string;
  display_name: string | null;
  role: string;
  avatar_color: string;
  avatar_url: string | null;
  azure_job_title: string | null;
  azure_department: string | null;
  azure_phone: string | null;
  last_seen_at: string | null;
}

function getInitials(name: string | null, email: string): string {
  if (name) {
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    return name.slice(0, 2).toUpperCase();
  }
  return email.slice(0, 2).toUpperCase();
}

export default function HrTeamPage() {
  const { data: session } = useSession();
  const role = (session?.user as { role?: Role } | undefined)?.role;
  const canSync = role ? isAdminRole(role) : false;

  const [users, setUsers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<{ synced: number; photos: number } | null>(null);

  useEffect(() => {
    fetch("/api/admin/users")
      .then((r) => r.json())
      .then((d) => { setUsers(d.users ?? []); setLoading(false); });
  }, []);

  async function handleSync() {
    setSyncing(true);
    setSyncResult(null);
    const res = await fetch("/api/hr/sync-users", { method: "POST" });
    if (res.ok) {
      const data = await res.json();
      setSyncResult(data);
      // Refresh the list
      const listRes = await fetch("/api/admin/users");
      const listData = await listRes.json();
      setUsers(listData.users ?? []);
    }
    setSyncing(false);
  }

  // Group by department
  const departments = Array.from(
    new Set(users.map((u) => u.azure_department ?? "Unassigned"))
  ).sort();

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Team</h1>
          <p className="text-sm text-muted-foreground">
            {users.length} members synced from Azure AD
          </p>
        </div>
        {canSync && (
          <button
            onClick={handleSync}
            disabled={syncing}
            className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            style={{ backgroundColor: "#FE5000" }}
          >
            {syncing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            {syncing ? "Syncing..." : "Sync from Azure"}
          </button>
        )}
      </div>

      {syncResult && (
        <div className="rounded-lg border border-green-200 bg-green-50 dark:bg-green-950/20 px-4 py-3">
          <p className="text-sm font-medium text-green-700 dark:text-green-400">
            Sync complete: {syncResult.synced} users updated, {syncResult.photos} photos fetched
          </p>
        </div>
      )}

      {loading ? (
        <div className="flex items-center gap-2 text-sm text-muted-foreground py-8">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading team...
        </div>
      ) : (
        departments.map((dept) => {
          const deptUsers = users.filter((u) => (u.azure_department ?? "Unassigned") === dept);
          return (
            <Card key={dept}>
              <CardHeader>
                <CardTitle className="text-sm font-medium">
                  {dept} ({deptUsers.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="divide-y">
                  {deptUsers.map((user) => (
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
                            className="flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold text-white select-none"
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

                      <div className="text-right shrink-0">
                        <span
                          className="inline-block rounded-full px-2 py-0.5 text-xs font-medium text-white"
                          style={{ backgroundColor: "#FE5000" }}
                        >
                          {ROLE_LABELS[user.role as Role] ?? user.role}
                        </span>
                        {user.azure_phone && (
                          <p className="text-xs text-muted-foreground mt-0.5">{user.azure_phone}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          );
        })
      )}
    </div>
  );
}
