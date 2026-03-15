import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getPortalUser, auditRoleChange } from "@/lib/db-portal";
import { canChangeRoles } from "@/lib/roles";
import type { Role } from "@/types";

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ email: string }> }
) {
  const session = await auth();
  const sessionRole = (session?.user as { role?: Role } | undefined)?.role;
  if (!session?.user?.email || !sessionRole || !canChangeRoles(sessionRole)) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const { email } = await params;
  const targetEmail = decodeURIComponent(email);
  const body = await request.json();
  const newRole = String(body.role ?? "");

  const user = getPortalUser(targetEmail);
  if (!user) return NextResponse.json({ error: "User not found" }, { status: 404 });

  auditRoleChange(targetEmail, user.role, newRole, session.user.email, body.note);

  return NextResponse.json({ ok: true });
}
