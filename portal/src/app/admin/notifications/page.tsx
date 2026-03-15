"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const NOTIFICATION_TYPES = [
  { value: "admin_message", label: "Admin Message" },
  { value: "system", label: "System Notice" },
  { value: "agent_failure", label: "Agent Failure Alert" },
  { value: "token_cap", label: "Token Cap Warning" },
];

export default function AdminNotificationsPage() {
  const [recipient, setRecipient] = useState("");
  const [type, setType] = useState("admin_message");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [link, setLink] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "done" | "error">("idle");

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    setStatus("sending");

    const res = await fetch("/api/admin/notifications", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        recipient: recipient.trim() || null,
        type,
        title: title.trim(),
        body: body.trim() || undefined,
        link: link.trim() || undefined,
      }),
    });

    if (res.ok) {
      setStatus("done");
      setTitle("");
      setBody("");
      setLink("");
      setRecipient("");
      setTimeout(() => setStatus("idle"), 3000);
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
          Users
        </Link>
        <span className="text-muted-foreground">/</span>
        <span className="text-sm font-medium">Send Notification</span>
      </div>

      <div>
        <h1 className="text-2xl font-bold">Send Notification</h1>
        <p className="text-sm text-muted-foreground">
          Send a targeted or broadcast message to portal users
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Notification Details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSend} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Recipient email</label>
              <p className="text-xs text-muted-foreground mt-0.5">Leave blank to broadcast to all users</p>
              <input
                type="email"
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                placeholder="user@ananas.mk (or leave blank)"
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none"
              />
            </div>

            <div>
              <label className="text-sm font-medium">Type</label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none"
              >
                {NOTIFICATION_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-sm font-medium">Title <span className="text-red-500">*</span></label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Short notification title"
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none"
              />
            </div>

            <div>
              <label className="text-sm font-medium">Body</label>
              <textarea
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="Optional longer message..."
                rows={3}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none resize-none"
              />
            </div>

            <div>
              <label className="text-sm font-medium">Link</label>
              <input
                type="url"
                value={link}
                onChange={(e) => setLink(e.target.value)}
                placeholder="https://... (optional action URL)"
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none"
              />
            </div>

            {status === "done" && (
              <div className="rounded-lg border border-green-200 bg-green-50 dark:bg-green-950/20 px-4 py-3">
                <p className="text-sm font-medium text-green-700 dark:text-green-400">
                  Notification sent successfully
                </p>
              </div>
            )}

            {status === "error" && (
              <p className="text-sm text-red-500">Failed to send. Check permissions and try again.</p>
            )}

            <button
              type="submit"
              disabled={status === "sending"}
              className="rounded-lg px-5 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
              style={{ backgroundColor: "#FE5000" }}
            >
              {status === "sending" ? "Sending..." : "Send Notification"}
            </button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
