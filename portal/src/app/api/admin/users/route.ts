import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getAllPortalUsers, getUserMostVisitedPages } from "@/lib/db-portal";
import type { Role } from "@/types";

const ADMIN_ROLES: Role[] = ["executive", "marketing_head"];

export async function GET() {
  const session = await auth();
  const role = (session?.user as { role?: Role } | undefined)?.role;
  if (!role || !ADMIN_ROLES.includes(role)) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const users = getAllPortalUsers().map((u) => {
    const topPages = getUserMostVisitedPages(u.email, 1);
    return {
      id: u.id,
      email: u.email,
      display_name: u.display_name,
      role: u.role,
      department: u.department,
      avatar_color: u.avatar_color,
      last_seen_at: u.last_seen_at,
      created_at: u.created_at,
      most_visited: topPages[0]?.page ?? null,
    };
  });

  return NextResponse.json({ users });
}
