import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { createNotification } from "@/lib/db-portal";
import { canSendNotifications } from "@/lib/roles";
import type { Role } from "@/types";

export async function POST(request: Request) {
  const session = await auth();
  const sessionRole = (session?.user as { role?: Role } | undefined)?.role;
  if (!session?.user?.email || !sessionRole || !canSendNotifications(sessionRole)) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const body = await request.json();
  const { recipient, type, title, body: msgBody, link } = body;

  if (!title) {
    return NextResponse.json({ error: "title required" }, { status: 400 });
  }

  // Use ai@ananas.mk as display sender for system-type notifications
  const systemTypes = ["system", "token_cap", "agent_failure"];
  const sender = systemTypes.includes(type ?? "")
    ? (process.env.SYSTEM_NOTIFICATION_EMAIL ?? "ai@ananas.mk")
    : session.user.email;

  createNotification({
    recipient: recipient ?? null, // null = broadcast to all
    sender,
    type: type ?? "admin_message",
    title,
    body: msgBody,
    link,
  });

  return NextResponse.json({ ok: true });
}
