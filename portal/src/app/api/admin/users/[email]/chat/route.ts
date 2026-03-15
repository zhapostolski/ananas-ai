import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getPortalUser, setChatEnabled } from "@/lib/db-portal";
import { isAdminRole } from "@/lib/roles";
import type { Role } from "@/types";

export async function PATCH(
  request: Request,
  { params }: { params: Promise<{ email: string }> }
) {
  const session = await auth();
  const adminEmail = (session?.user as { email?: string } | undefined)?.email;
  if (!adminEmail) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const admin = getPortalUser(adminEmail);
  if (!admin || !isAdminRole(admin.role as Role)) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const { email: targetEmail } = await params;
  const body = await request.json().catch(() => null) as { enabled?: boolean } | null;
  if (body?.enabled === undefined) {
    return NextResponse.json({ error: "Missing enabled field" }, { status: 400 });
  }

  setChatEnabled(decodeURIComponent(targetEmail), body.enabled);
  return NextResponse.json({ ok: true });
}
