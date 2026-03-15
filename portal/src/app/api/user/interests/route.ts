import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { updatePortalUser } from "@/lib/db-portal";

export async function PUT(request: Request) {
  const session = await auth();
  if (!session?.user?.email) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = await request.json();
  const interests = Array.isArray(body.interests) ? body.interests.slice(0, 10) : [];

  updatePortalUser(session.user.email, {
    interests_json: JSON.stringify(interests),
  });

  return NextResponse.json({ ok: true });
}
