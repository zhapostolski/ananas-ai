"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ROLE_LABELS, canInvite, canChangeRoles } from "@/lib/roles";
import { timeAgo } from "@/lib/utils";
import type { Role } from "@/types";
import { Check, Loader2 } from "lucide-react";

interface UserRow {
  id: number;
  email: string;
  display_name: string | null;
  role: string;
  department: string | null;
  avatar_color: string;
  last_seen_at: string | null;
  created_at: string;
  most_visited: string | null;
}

const ALL_ROLES: Role[] = [
  "super_admin",
  "executive",
  "marketing_head",
  "performance_marketer",
  "crm_specialist",
  "content_brand",
  "marketing_ops",
  "commercial_head",
  "commercial_3p",
  "commercial_1p",
  "finance_head",
  "finance_team",
  "logistics_head",
  "logistics_team",
  "cx_head",
  "cx_team",
  "hr_head",
  "hr",
];

function pageLabelFromPath(path: string | null): string {
  if (!path) return "--";
  const map: Record<string, string> = {
    "/marketing/overview": "Overview",
    "/marketing/performance": "Performance",
    "/marketing/crm": "CRM",
    "/marketing/reputation": "Reputation",
    "/marketing/influencers": "Influencers",
    "/marketing/ops": "Marketing Ops",
    "/profile": "Profile",
    "/settings": "Settings",
  };
  return map[path] ?? path;
}

function AvatarCircle({ name, color }: { name: string; color: string }) {
  const parts = name.trim().split(/\s+/);
  const initials =
    parts.length >= 2
      ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
      : name.slice(0, 2).toUpperCase();
  return (
    <div
      className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white select-none"
      style={{ backgroundColor: color }}
    >
      {initials}
    </div>
  );
}

type SaveState = "idle" | "saving" | "saved" | "error";

export default function AdminUsersPage() {
  const { data: session } = useSession();
  const currentRole = (session?.user as { role?: Role } | undefined)?.role;
  const showInvite = currentRole ? canInvite(currentRole) : false;
  const showRoleEditor = currentRole ? canChangeRoles(currentRole) : false;

  const [users, setUsers] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(true);
  // Map of userId -> pending role (before save)
  const [pendingRoles, setPendingRoles] = useState<Record<number, string>>({});
  // Map of userId -> save state
  const [saveStates, setSaveStates] = useState<Record<number, SaveState>>({});

  useEffect(() => {
    fetch("/api/admin/users")
      .then((r) => r.json())
      .then((data) => {
        setUsers(data.users ?? []);
        setLoading(false);
      });
  }, []);

  function handleRoleChange(userId: number, email: string, newRole: string) {
    const original = users.find((u) => u.id === userId)?.role;
    if (newRole === original) {
      // Revert to no pending change
      setPendingRoles((prev) => {
        const next = { ...prev };
        delete next[userId];
        return next;
      });
    } else {
      setPendingRoles((prev) => ({ ...prev, [userId]: newRole }));
    }
    // Clear any previous save feedback
    setSaveStates((prev) => {
      const next = { ...prev };
      delete next[userId];
      return next;
    });
  }

  const saveRole = useCallback(async (user: UserRow) => {
    const newRole = pendingRoles[user.id];
    if (!newRole) return;

    setSaveStates((prev) => ({ ...prev, [user.id]: "saving" }));

    const res = await fetch(`/api/admin/users/${encodeURIComponent(user.email)}/role`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role: newRole }),
    });

    if (res.ok) {
      setUsers((prev) =>
        prev.map((u) => (u.id === user.id ? { ...u, role: newRole } : u))
      );
      setPendingRoles((prev) => {
        const next = { ...prev };
        delete next[user.id];
        return next;
      });
      setSaveStates((prev) => ({ ...prev, [user.id]: "saved" }));
      // Clear "saved" feedback after 3 seconds
      setTimeout(() => {
        setSaveStates((prev) => {
          const next = { ...prev };
          delete next[user.id];
          return next;
        });
      }, 3000);
    } else {
      setSaveStates((prev) => ({ ...prev, [user.id]: "error" }));
    }
  }, [pendingRoles]);

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">User Management</h1>
          <p className="text-sm text-muted-foreground">
            Manage roles and access for all platform users
          </p>
        </div>
        {showInvite && (
          <Link
            href="/admin/users/invite"
            className="rounded-lg px-4 py-2 text-sm font-semibold text-white"
            style={{ backgroundColor: "#FE5000" }}
          >
            Invite User
          </Link>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            All Users ({users.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground italic py-4">Loading users...</p>
          ) : users.length === 0 ? (
            <p className="text-sm text-muted-foreground italic py-4">
              No users have logged in yet.
            </p>
          ) : (
            <div className="divide-y">
              {users.map((user) => {
                const pending = pendingRoles[user.id];
                const hasPending = pending !== undefined;
                const saveState = saveStates[user.id] ?? "idle";
                const currentDisplayRole = pending ?? user.role;

                return (
                  <div
                    key={user.id}
                    className="flex flex-col sm:flex-row sm:items-center gap-3 py-3"
                  >
                    <AvatarCircle
                      name={user.display_name ?? user.email}
                      color={user.avatar_color}
                    />

                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {user.display_name ?? user.email}
                      </p>
                      <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <div className="text-right hidden sm:block">
                        <p className="text-xs text-muted-foreground">
                          {user.last_seen_at ? timeAgo(user.last_seen_at) : "Never"}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {pageLabelFromPath(user.most_visited)}
                        </p>
                      </div>

                      {showRoleEditor ? (
                        <select
                          value={currentDisplayRole}
                          disabled={saveState === "saving"}
                          onChange={(e) => handleRoleChange(user.id, user.email, e.target.value)}
                          className="rounded-md border bg-background px-2 py-1 text-xs font-medium focus:outline-none disabled:opacity-50"
                          style={{ minWidth: 140 }}
                        >
                          {ALL_ROLES.map((r) => (
                            <option key={r} value={r}>
                              {ROLE_LABELS[r]}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <span className="rounded-full px-2 py-0.5 text-xs font-medium text-white" style={{ backgroundColor: "#FE5000" }}>
                          {ROLE_LABELS[user.role as Role] ?? user.role}
                        </span>
                      )}

                      {/* Save button — visible only when there's a pending change */}
                      <div className="w-16 flex items-center justify-center">
                        {saveState === "saving" ? (
                          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                        ) : saveState === "saved" ? (
                          <span className="flex items-center gap-1 text-xs text-green-600 font-medium">
                            <Check className="h-3.5 w-3.5" />
                            Saved
                          </span>
                        ) : saveState === "error" ? (
                          <span className="text-xs text-red-500 font-medium">Error</span>
                        ) : hasPending ? (
                          <button
                            onClick={() => saveRole(user)}
                            className="rounded-md px-3 py-1 text-xs font-semibold text-white transition-opacity hover:opacity-90"
                            style={{ backgroundColor: "#FE5000" }}
                          >
                            Save
                          </button>
                        ) : null}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
