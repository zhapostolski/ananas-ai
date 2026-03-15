"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ROLE_LABELS } from "@/lib/roles";
import { INTEREST_OPTIONS } from "@/types";
import type { Role } from "@/types";
import { formatDate, timeAgo } from "@/lib/utils";

interface ProfileData {
  email: string;
  display_name: string;
  role: string;
  bio: string | null;
  avatar_color: string;
  interests: string[];
  preferences: { theme?: string; density?: string };
  favorite_agents: string[];
  last_seen_at: string | null;
  created_at: string;
  activity: Array<{ page: string; title: string | null; created_at: string }>;
  top_pages: Array<{ page: string; count: number }>;
}

function AvatarCircle({
  name,
  email,
  color,
  size = 64,
}: {
  name: string;
  email: string;
  color: string;
  size?: number;
}) {
  const parts = name.trim().split(/\s+/);
  const initials =
    parts.length >= 2
      ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
      : name.slice(0, 2).toUpperCase();

  return (
    <div
      className="flex items-center justify-center rounded-full font-bold text-white select-none shrink-0"
      style={{ width: size, height: size, backgroundColor: color, fontSize: size / 2.8 }}
    >
      {initials}
    </div>
  );
}

function pageLabelFromPath(path: string): string {
  const map: Record<string, string> = {
    "/marketing/overview": "Overview",
    "/marketing/performance": "Performance",
    "/marketing/crm": "CRM",
    "/marketing/reputation": "Reputation",
    "/marketing/influencers": "Influencers",
    "/marketing/ops": "Marketing Ops",
    "/profile": "Profile",
    "/settings": "Settings",
    "/admin/users": "Admin",
  };
  return map[path] ?? path;
}

const AGENT_IDS = [
  { id: "performance-agent", label: "Performance" },
  { id: "crm-lifecycle-agent", label: "CRM & Lifecycle" },
  { id: "reputation-agent", label: "Reputation" },
  { id: "marketing-ops-agent", label: "Marketing Ops" },
  { id: "cross-channel-brief-agent", label: "Overview" },
];

const AVATAR_COLORS = [
  "#FE5000", "#84BD00", "#3B82F6", "#8B5CF6", "#EC4899",
  "#14B8A6", "#F59E0B", "#6366F1", "#10B981", "#EF4444",
];

export default function ProfilePage() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [saving, setSaving] = useState(false);
  const [bio, setBio] = useState("");
  const [interests, setInterests] = useState<string[]>([]);
  const [favorites, setFavorites] = useState<string[]>([]);
  const [color, setColor] = useState("#FE5000");

  useEffect(() => {
    fetch("/api/user/profile")
      .then((r) => r.json())
      .then((data: ProfileData) => {
        setProfile(data);
        setBio(data.bio ?? "");
        setInterests(data.interests ?? []);
        setFavorites(data.favorite_agents ?? []);
        setColor(data.avatar_color);
      });
  }, []);

  async function saveProfile() {
    setSaving(true);
    await Promise.all([
      fetch("/api/user/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bio, avatar_color: color }),
      }),
      fetch("/api/user/interests", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ interests }),
      }),
      fetch("/api/user/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          favorite_agents_json: JSON.stringify(favorites),
          avatar_color: color,
          bio,
        }),
      }),
    ]);
    setSaving(false);
  }

  function toggleInterest(key: string) {
    setInterests((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    );
  }

  function toggleFavorite(id: string) {
    setFavorites((prev) =>
      prev.includes(id) ? prev.filter((k) => k !== id) : [...prev, id]
    );
  }

  if (!profile) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-muted-foreground">Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header card */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
            <AvatarCircle
              name={profile.display_name}
              email={profile.email}
              color={color}
              size={72}
            />
            <div className="flex-1 min-w-0">
              <h1 className="text-xl font-bold">{profile.display_name}</h1>
              <p className="text-sm text-muted-foreground">{profile.email}</p>
              <div className="mt-2 flex flex-wrap gap-2">
                <Badge variant="outline" style={{ borderColor: "#FE5000", color: "#FE5000" }}>
                  {ROLE_LABELS[profile.role as Role]}
                </Badge>
                {profile.last_seen_at && (
                  <span className="text-xs text-muted-foreground">
                    Last active {timeAgo(profile.last_seen_at)}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="mt-4">
            <label className="text-xs font-medium text-muted-foreground">Bio</label>
            <textarea
              className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm resize-none focus:outline-none focus:ring-1"
              style={{ "--tw-ring-color": "#FE5000" } as React.CSSProperties}
              rows={2}
              maxLength={200}
              placeholder="A short bio about yourself..."
              value={bio}
              onChange={(e) => setBio(e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          {/* Avatar color */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Avatar Color</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                {AVATAR_COLORS.map((c) => (
                  <button
                    key={c}
                    onClick={() => setColor(c)}
                    className="h-8 w-8 rounded-full transition-transform hover:scale-110"
                    style={{
                      backgroundColor: c,
                      outline: color === c ? `3px solid ${c}` : "none",
                      outlineOffset: "2px",
                    }}
                  />
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Interests */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Interests</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground mb-3">
                Select topics to personalize your overview cards.
              </p>
              <div className="flex flex-wrap gap-2">
                {INTEREST_OPTIONS.map((opt) => {
                  const active = interests.includes(opt.key);
                  return (
                    <button
                      key={opt.key}
                      onClick={() => toggleInterest(opt.key)}
                      className="rounded-full border px-3 py-1 text-xs font-medium transition-colors"
                      style={
                        active
                          ? { backgroundColor: "#FE5000", borderColor: "#FE5000", color: "white" }
                          : {}
                      }
                    >
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Favorite agents */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Favorite Agents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {AGENT_IDS.map((a) => {
                  const active = favorites.includes(a.id);
                  return (
                    <button
                      key={a.id}
                      onClick={() => toggleFavorite(a.id)}
                      className="rounded-full border px-3 py-1 text-xs font-medium transition-colors"
                      style={
                        active
                          ? { backgroundColor: "#FE5000", borderColor: "#FE5000", color: "white" }
                          : {}
                      }
                    >
                      {a.label}
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          <div>
            <button
              onClick={saveProfile}
              disabled={saving}
              className="rounded-lg px-5 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
              style={{ backgroundColor: "#FE5000" }}
            >
              {saving ? "Saving..." : "Save Profile"}
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {/* Top pages */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Most Visited</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {profile.top_pages.length === 0 ? (
                <p className="text-xs text-muted-foreground italic">No visits tracked yet.</p>
              ) : (
                profile.top_pages.map((p) => (
                  <div key={p.page} className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground truncate">
                      {pageLabelFromPath(p.page)}
                    </span>
                    <span className="text-xs font-semibold">{p.count}x</span>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Recent activity */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 max-h-64 overflow-y-auto">
              {profile.activity.length === 0 ? (
                <p className="text-xs text-muted-foreground italic">No activity yet.</p>
              ) : (
                profile.activity.slice(0, 10).map((a, i) => (
                  <div key={i} className="flex items-start justify-between gap-2">
                    <span className="text-xs truncate text-muted-foreground">
                      {pageLabelFromPath(a.page)}
                    </span>
                    <span className="text-xs text-muted-foreground shrink-0">
                      {timeAgo(a.created_at)}
                    </span>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Member since */}
          <Card>
            <CardContent className="pt-4">
              <p className="text-xs text-muted-foreground">Member since</p>
              <p className="text-sm font-medium">{formatDate(profile.created_at)}</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
