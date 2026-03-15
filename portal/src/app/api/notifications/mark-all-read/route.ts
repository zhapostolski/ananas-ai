import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { markAllReadForUser } from "@/lib/db-portal";

export async function POST() {
  const session = await auth();
  if (!session?.user?.email) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  markAllReadForUser(session.user.email);
  return NextResponse.json({ ok: true });
}
