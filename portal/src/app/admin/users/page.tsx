"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ROLE_LABELS } from "@/lib/roles";
import { timeAgo, formatDate } from "@/lib/utils";
import type { Role } from "@/types";

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

export default function AdminUsersPage() {
  const [users, setUsers] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingRole, setSavingRole] = useState<number | null>(null);

  useEffect(() => {
    fetch("/api/admin/users")
      .then((r) => r.json())
      .then((data) => {
        setUsers(data.users ?? []);
        setLoading(false);
      });
  }, []);

  async function changeRole(email: string, newRole: string, userId: number) {
    setSavingRole(userId);
    await fetch(`/api/admin/users/${encodeURIComponent(email)}/role`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role: newRole }),
    });
    setUsers((prev) =>
      prev.map((u) => (u.email === email ? { ...u, role: newRole } : u))
    );
    setSavingRole(null);
  }

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">User Management</h1>
          <p className="text-sm text-muted-foreground">
            Manage roles and access for all platform users
          </p>
        </div>
        <Link
          href="/admin/users/invite"
          className="rounded-lg px-4 py-2 text-sm font-semibold text-white"
          style={{ backgroundColor: "#FE5000" }}
        >
          Invite User
        </Link>
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
              {users.map((user) => (
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

                    <select
                      value={user.role}
                      disabled={savingRole === user.id}
                      onChange={(e) => changeRole(user.email, e.target.value, user.id)}
                      className="rounded-md border bg-background px-2 py-1 text-xs font-medium focus:outline-none disabled:opacity-50"
                      style={{ minWidth: 140 }}
                    >
                      {ALL_ROLES.map((r) => (
                        <option key={r} value={r}>
                          {ROLE_LABELS[r]}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
