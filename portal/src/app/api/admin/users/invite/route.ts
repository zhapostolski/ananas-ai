import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { createRoleInvite } from "@/lib/db-portal";
import type { Role } from "@/types";

const ADMIN_ROLES: Role[] = ["executive", "marketing_head"];

export async function POST(request: Request) {
  const session = await auth();
  const sessionRole = (session?.user as { role?: Role } | undefined)?.role;
  if (!session?.user?.email || !sessionRole || !ADMIN_ROLES.includes(sessionRole)) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const body = await request.json();
  const email = String(body.email ?? "").toLowerCase().trim();
  const role = String(body.role ?? "");

  if (!email || !role) {
    return NextResponse.json({ error: "email and role required" }, { status: 400 });
  }

  createRoleInvite(email, role, session.user.email);
  return NextResponse.json({ ok: true });
}
