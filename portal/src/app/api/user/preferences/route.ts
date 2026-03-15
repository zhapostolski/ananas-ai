import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getOrCreatePortalUser, updatePortalUser } from "@/lib/db-portal";

export async function PUT(request: Request) {
  const session = await auth();
  if (!session?.user?.email) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = await request.json();
  const user = getOrCreatePortalUser(session.user.email, session.user.name);
  const current = JSON.parse(user.preferences_json ?? "{}");

  const updated = {
    ...current,
    ...(body.theme ? { theme: body.theme } : {}),
    ...(body.density ? { density: body.density } : {}),
  };

  updatePortalUser(session.user.email, {
    preferences_json: JSON.stringify(updated),
  });

  return NextResponse.json({ ok: true, preferences: updated });
}
