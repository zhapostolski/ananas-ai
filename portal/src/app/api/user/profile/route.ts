import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getPortalUser, getOrCreatePortalUser, updatePortalUser } from "@/lib/db-portal";
import { getUserActivity, getUserMostVisitedPages } from "@/lib/db-portal";

export async function GET() {
  const session = await auth();
  if (!session?.user?.email) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const user = getOrCreatePortalUser(session.user.email, session.user.name);
  const activity = getUserActivity(session.user.email, 15);
  const topPages = getUserMostVisitedPages(session.user.email, 5);

  return NextResponse.json({
    email: user.email,
    display_name: user.display_name ?? session.user.name ?? user.email,
    role: user.role,
    department: user.department,
    avatar_color: user.avatar_color,
    bio: user.bio,
    interests: JSON.parse(user.interests_json),
    preferences: JSON.parse(user.preferences_json),
    favorite_agents: JSON.parse(user.favorite_agents_json),
    last_seen_at: user.last_seen_at,
    created_at: user.created_at,
    activity,
    top_pages: topPages,
  });
}

export async function PUT(request: Request) {
  const session = await auth();
  if (!session?.user?.email) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = await request.json();
  const allowed = ["display_name", "bio", "avatar_color"];
  const updates: Record<string, string> = {};
  for (const key of allowed) {
    if (body[key] !== undefined) updates[key] = String(body[key]).slice(0, 200);
  }

  if (Object.keys(updates).length > 0) {
    updatePortalUser(session.user.email, updates as Parameters<typeof updatePortalUser>[1]);
  }

  return NextResponse.json({ ok: true });
}
