import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { trackPageView, touchLastSeen } from "@/lib/db-portal";

export async function POST(request: Request) {
  const session = await auth();
  if (!session?.user?.email) return NextResponse.json({ ok: false }, { status: 401 });

  const body = await request.json();
  const page = String(body.page ?? "").slice(0, 200);
  const title = body.title ? String(body.title).slice(0, 200) : undefined;
  const sessionId = body.session_id ? String(body.session_id).slice(0, 64) : undefined;

  if (!page) return NextResponse.json({ ok: false }, { status: 400 });

  trackPageView(session.user.email, page, title, sessionId);
  touchLastSeen(session.user.email);

  return NextResponse.json({ ok: true });
}
