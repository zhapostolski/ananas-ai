"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ROLE_LABELS } from "@/lib/roles";
import type { Role } from "@/types";

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
  "hr_head",
  "hr",
];

export default function InviteUserPage() {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<Role>("performance_marketer");
  const [status, setStatus] = useState<"idle" | "saving" | "done" | "error">("idle");
  const [emailSent, setEmailSent] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("saving");

    const res = await fetch("/api/admin/users/invite", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, role }),
    });

    if (res.ok) {
      const data = await res.json();
      setEmailSent(data.emailSent === true);
      setStatus("done");
    } else {
      setStatus("error");
    }
  }

  return (
    <div className="max-w-lg space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href="/admin/users"
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          Back to Users
        </Link>
      </div>

      <div>
        <h1 className="text-2xl font-bold">Invite User</h1>
        <p className="text-sm text-muted-foreground">
          Pre-assign a role to a user before their first login
        </p>
      </div>

      {status === "done" ? (
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="rounded-lg border border-green-200 bg-green-50 dark:bg-green-950/20 px-4 py-3">
              <p className="text-sm font-medium text-green-700 dark:text-green-400">
                Invite created for {email}
              </p>
              <p className="text-xs text-green-600 dark:text-green-500 mt-1">
                Role assigned: {ROLE_LABELS[role]}. Access granted on first Microsoft login.
              </p>
              {emailSent && (
                <p className="text-xs text-green-600 dark:text-green-500 mt-0.5">
                  Invitation email sent.
                </p>
              )}
              {!emailSent && (
                <p className="text-xs text-yellow-600 dark:text-yellow-500 mt-0.5">
                  Email could not be sent — invite is still active for login.
                </p>
              )}
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => { setEmail(""); setRole("performance_marketer"); setStatus("idle"); }}
                className="rounded-lg px-4 py-2 text-sm font-medium border hover:bg-accent transition-colors"
              >
                Invite Another
              </button>
              <Link
                href="/admin/users"
                className="rounded-lg px-4 py-2 text-sm font-semibold text-white"
                style={{ backgroundColor: "#FE5000" }}
              >
                Back to Users
              </Link>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">User Details</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-sm font-medium">Email address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="user@ananas.mk"
                  className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1"
                  style={{ "--tw-ring-color": "#FE5000" } as React.CSSProperties}
                />
              </div>

              <div>
                <label className="text-sm font-medium">Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value as Role)}
                  className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none"
                >
                  {ALL_ROLES.map((r) => (
                    <option key={r} value={r}>
                      {ROLE_LABELS[r]}
                    </option>
                  ))}
                </select>
              </div>

              {status === "error" && (
                <p className="text-sm text-red-500">Something went wrong. Please try again.</p>
              )}

              <button
                type="submit"
                disabled={status === "saving"}
                className="rounded-lg px-5 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                style={{ backgroundColor: "#FE5000" }}
              >
                {status === "saving" ? "Creating invite..." : "Create Invite"}
              </button>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
