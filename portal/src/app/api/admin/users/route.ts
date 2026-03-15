import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getAllPortalUsers, getUserMostVisitedPages } from "@/lib/db-portal";
import { isAdminRole } from "@/lib/roles";
import type { Role } from "@/types";

export async function GET() {
  const session = await auth();
  const role = (session?.user as { role?: Role } | undefined)?.role;
  if (!role || !isAdminRole(role)) {
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
      avatar_url: u.avatar_url,
      azure_job_title: u.azure_job_title,
      azure_department: u.azure_department,
      azure_phone: u.azure_phone,
      last_seen_at: u.last_seen_at,
      created_at: u.created_at,
      most_visited: topPages[0]?.page ?? null,
      chat_enabled: u.chat_enabled === 1,
    };
  });

  return NextResponse.json({ users });
}
