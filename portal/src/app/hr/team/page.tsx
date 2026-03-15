"use client";

import { useEffect, useState, useCallback } from "react";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ROLE_LABELS } from "@/lib/roles";
import type { Role } from "@/types";
import { Loader2, RefreshCw } from "lucide-react";

const SYNC_ROLES: Role[] = ["super_admin", "executive", "hr_head", "hr"];
const STALE_MS = 24 * 60 * 60 * 1000; // 24 hours

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
  const canSync = role ? SYNC_ROLES.includes(role) : false;

  const [users, setUsers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<{ synced: number; photos: number } | null>(null);
  const [syncError, setSyncError] = useState<string | null>(null);

  const loadUsers = useCallback(async () => {
    const res = await fetch("/api/admin/users");
    const d = await res.json();
    setUsers(d.users ?? []);
  }, []);

  const runSync = useCallback(async (silent = false) => {
    if (!silent) setSyncing(true);
    setSyncError(null);
    try {
      const res = await fetch("/api/hr/sync-users", { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        if (!silent) setSyncResult(data);
        await loadUsers();
      } else {
        if (!silent) setSyncError(data.error ?? "Sync failed");
      }
    } catch {
      if (!silent) setSyncError("Sync request failed");
    }
    if (!silent) setSyncing(false);
  }, [loadUsers]);

  useEffect(() => {
    async function init() {
      await loadUsers();
      setLoading(false);

      if (!canSync) return;

      // Check if data is stale and auto-sync
      const statusRes = await fetch("/api/hr/sync-users");
      const status = await statusRes.json();
      const lastSync = status.lastSync ? new Date(status.lastSync).getTime() : 0;
      const isStale = Date.now() - lastSync > STALE_MS;

      if (isStale) {
        runSync(true); // silent background sync
      }
    }
    init();
  }, [canSync, loadUsers, runSync]);

  const departments = Array.from(
    new Set(users.map((u) => u.azure_department ?? "Other"))
  ).sort((a, b) => a === "Other" ? 1 : b === "Other" ? -1 : a.localeCompare(b));

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Team</h1>
          <p className="text-sm text-muted-foreground">
            {users.length} members from Azure AD
          </p>
        </div>
        {canSync && (
          <button
            onClick={() => runSync(false)}
            disabled={syncing}
            className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            style={{ backgroundColor: "#FE5000" }}
          >
            {syncing ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            {syncing ? "Syncing..." : "Sync from Azure"}
          </button>
        )}
      </div>

      {syncResult && (
        <div className="rounded-lg border border-green-200 bg-green-50 dark:bg-green-950/20 px-4 py-3">
          <p className="text-sm font-medium text-green-700 dark:text-green-400">
            Sync complete: {syncResult.synced} users, {syncResult.photos} photos fetched
          </p>
        </div>
      )}

      {syncError && (
        <div className="rounded-lg border border-red-200 bg-red-50 dark:bg-red-950/20 px-4 py-3">
          <p className="text-sm font-medium text-red-700 dark:text-red-400">{syncError}</p>
        </div>
      )}

      {loading ? (
        <div className="flex items-center gap-2 text-sm text-muted-foreground py-8">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading team...
        </div>
      ) : users.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-sm text-muted-foreground">
            No users yet.{canSync ? " Click Sync from Azure to import your organisation." : ""}
          </CardContent>
        </Card>
      ) : (
        departments.map((dept) => {
          const deptUsers = users.filter((u) => (u.azure_department ?? "Other") === dept);
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
