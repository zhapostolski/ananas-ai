"use client";

import { useEffect, useState, useCallback } from "react";
import { Bell, X, CheckCheck, AlertTriangle, Info, MessageSquare, Zap } from "lucide-react";

interface Notification {
  id: number;
  recipient: string | null;
  sender: string;
  type: string;
  title: string;
  body: string | null;
  link: string | null;
  read_by_json: string;
  created_at: string;
}

function timeAgo(dateStr: string): string {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

function isRead(notification: Notification, email: string): boolean {
  try {
    const map = JSON.parse(notification.read_by_json) as Record<string, string>;
    return !!map[email];
  } catch {
    return false;
  }
}

function TypeIcon({ type }: { type: string }) {
  const cls = "h-3.5 w-3.5 shrink-0 mt-0.5";
  switch (type) {
    case "agent_failure":
      return <AlertTriangle className={`${cls} text-red-500`} />;
    case "token_cap":
      return <Zap className={`${cls} text-yellow-500`} />;
    case "system":
      return <Info className={`${cls} text-blue-500`} />;
    default:
      return <MessageSquare className={`${cls} text-orange-500`} />;
  }
}

export function NotificationBell({ userEmail }: { userEmail: string }) {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = useCallback(() => {
    setLoading(true);
    fetch("/api/notifications")
      .then((r) => r.json())
      .then((data) => {
        setNotifications(data.notifications ?? []);
        setUnread(data.unread ?? 0);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchNotifications();
    // Poll every 60 seconds
    const interval = setInterval(fetchNotifications, 60_000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  async function markRead(id: number) {
    await fetch(`/api/notifications/${id}/read`, { method: "PATCH" });
    setNotifications((prev) =>
      prev.map((n) => {
        if (n.id !== id) return n;
        let map: Record<string, string> = {};
        try { map = JSON.parse(n.read_by_json); } catch { /* empty */ }
        map[userEmail] = new Date().toISOString();
        return { ...n, read_by_json: JSON.stringify(map) };
      })
    );
    setUnread((prev) => Math.max(0, prev - 1));
  }

  async function markAllRead() {
    await fetch("/api/notifications/mark-all-read", { method: "POST" });
    const now = new Date().toISOString();
    setNotifications((prev) =>
      prev.map((n) => {
        let map: Record<string, string> = {};
        try { map = JSON.parse(n.read_by_json); } catch { /* empty */ }
        map[userEmail] = now;
        return { ...n, read_by_json: JSON.stringify(map) };
      })
    );
    setUnread(0);
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="relative flex h-8 w-8 items-center justify-center rounded-lg hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
        title="Notifications"
        aria-label="Notifications"
      >
        <Bell className="h-4 w-4" />
        {unread > 0 && (
          <span
            className="absolute right-1 top-1 flex h-4 w-4 items-center justify-center rounded-full text-[9px] font-bold text-white border-2 border-card"
            style={{ backgroundColor: "#FE5000" }}
          >
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>

      {open && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />

          {/* Dropdown */}
          <div className="absolute right-0 top-full z-50 mt-2 w-80 rounded-xl border bg-white dark:bg-gray-900 shadow-xl">
            {/* Header */}
            <div className="flex items-center justify-between border-b px-4 py-3">
              <span className="text-sm font-semibold">Notifications</span>
              <div className="flex items-center gap-2">
                {unread > 0 && (
                  <button
                    onClick={markAllRead}
                    className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <CheckCheck className="h-3.5 w-3.5" />
                    Mark all read
                  </button>
                )}
                <button
                  onClick={() => setOpen(false)}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* List */}
            <div className="max-h-80 overflow-y-auto">
              {loading && notifications.length === 0 ? (
                <p className="px-4 py-6 text-center text-sm text-muted-foreground">
                  Loading...
                </p>
              ) : notifications.length === 0 ? (
                <div className="flex flex-col items-center gap-2 px-4 py-8 text-muted-foreground">
                  <Bell className="h-8 w-8 opacity-20" />
                  <p className="text-sm">No notifications yet</p>
                </div>
              ) : (
                notifications.map((n) => {
                  const read = isRead(n, userEmail);
                  return (
                    <div
                      key={n.id}
                      className={`flex gap-3 px-4 py-3 border-b last:border-0 transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer ${
                        read ? "opacity-60" : ""
                      }`}
                      onClick={() => {
                        if (!read) markRead(n.id);
                        if (n.link) window.open(n.link, "_blank");
                      }}
                    >
                      <TypeIcon type={n.type} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <p className={`text-xs leading-snug ${read ? "" : "font-semibold"}`}>
                            {n.title}
                          </p>
                          {!read && (
                            <span
                              className="mt-1 h-2 w-2 shrink-0 rounded-full"
                              style={{ backgroundColor: "#FE5000" }}
                            />
                          )}
                        </div>
                        {n.body && (
                          <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                            {n.body}
                          </p>
                        )}
                        <p className="text-[10px] text-muted-foreground mt-1">
                          {timeAgo(n.created_at)}
                        </p>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
