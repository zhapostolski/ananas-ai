"use client";

import { useEffect, useState } from "react";
import { useTheme } from "next-themes";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ROLE_LABELS } from "@/lib/roles";
import type { Role } from "@/types";

const AGENT_LABELS: Record<string, string> = {
  "performance-agent": "Performance",
  "crm-lifecycle-agent": "CRM & Lifecycle",
  "reputation-agent": "Reputation",
  "marketing-ops-agent": "Marketing Ops",
  "cross-channel-brief-agent": "Overview",
};

interface ProfileData {
  email: string;
  display_name: string;
  role: string;
  preferences: {
    theme?: string;
    density?: string;
    notifications?: Record<string, boolean>;
  };
}

function TabButton({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
      style={
        active
          ? { borderColor: "#FE5000", color: "#FE5000" }
          : { borderColor: "transparent", color: "inherit" }
      }
    >
      {label}
    </button>
  );
}

function Toggle({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  label: string;
}) {
  return (
    <label className="flex items-center justify-between cursor-pointer">
      <span className="text-sm">{label}</span>
      <div
        onClick={() => onChange(!checked)}
        className="relative h-5 w-9 rounded-full transition-colors cursor-pointer"
        style={{ backgroundColor: checked ? "#FE5000" : "#d1d5db" }}
      >
        <div
          className="absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform"
          style={{ transform: checked ? "translateX(16px)" : "translateX(2px)" }}
        />
      </div>
    </label>
  );
}

export default function SettingsPage() {
  const [tab, setTab] = useState<"account" | "appearance" | "notifications">("account");
  const { theme, setTheme } = useTheme();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [notifications, setNotifications] = useState<Record<string, boolean>>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch("/api/user/profile")
      .then((r) => r.json())
      .then((data: ProfileData) => {
        setProfile(data);
        setNotifications(data.preferences?.notifications ?? {});
      });
  }, []);

  async function saveNotifications() {
    setSaving(true);
    await fetch("/api/user/preferences", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ notifications }),
    });
    setSaving(false);
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm text-muted-foreground">Manage your account and preferences</p>
      </div>

      <div className="flex border-b gap-1">
        <TabButton label="Account" active={tab === "account"} onClick={() => setTab("account")} />
        <TabButton label="Appearance" active={tab === "appearance"} onClick={() => setTab("appearance")} />
        <TabButton label="Notifications" active={tab === "notifications"} onClick={() => setTab("notifications")} />
      </div>

      {tab === "account" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Account Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {profile ? (
              <>
                <Row label="Name" value={profile.display_name} />
                <Row label="Email" value={profile.email} />
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Role</span>
                  <Badge
                    variant="outline"
                    style={{ borderColor: "#FE5000", color: "#FE5000" }}
                  >
                    {ROLE_LABELS[profile.role as Role] ?? profile.role}
                  </Badge>
                </div>
                <div className="pt-2 border-t">
                  <p className="text-xs text-muted-foreground">
                    Contact your platform administrator to update your role or access level.
                  </p>
                </div>
              </>
            ) : (
              <p className="text-sm text-muted-foreground italic">Loading...</p>
            )}
          </CardContent>
        </Card>
      )}

      {tab === "appearance" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Appearance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Theme</label>
              <div className="mt-2 grid grid-cols-3 gap-3">
                {(["light", "dark", "system"] as const).map((t) => (
                  <button
                    key={t}
                    onClick={() => setTheme(t)}
                    className="rounded-lg border px-4 py-2 text-sm font-medium capitalize transition-colors"
                    style={
                      theme === t
                        ? { backgroundColor: "#FE5000", borderColor: "#FE5000", color: "white" }
                        : {}
                    }
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {tab === "notifications" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Agent Notifications</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-xs text-muted-foreground">
              Choose which agent outputs you want highlighted in your overview.
            </p>
            {Object.entries(AGENT_LABELS).map(([id, label]) => (
              <Toggle
                key={id}
                label={label}
                checked={notifications[id] !== false}
                onChange={(v) => setNotifications((prev) => ({ ...prev, [id]: v }))}
              />
            ))}
            <div className="pt-2">
              <button
                onClick={saveNotifications}
                disabled={saving}
                className="rounded-lg px-5 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                style={{ backgroundColor: "#FE5000" }}
              >
                {saving ? "Saving..." : "Save Preferences"}
              </button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function Row({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-sm font-medium">{value ?? "--"}</span>
    </div>
  );
}
