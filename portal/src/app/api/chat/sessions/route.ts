import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getPortalUser, createChatSession, getChatSessions } from "@/lib/db-portal";
import { randomUUID } from "crypto";

export async function GET() {
  const session = await auth();
  const email = (session?.user as { email?: string } | undefined)?.email;
  if (!email) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const user = getPortalUser(email);
  if (!user?.chat_enabled) return NextResponse.json({ error: "Chat not enabled for your account" }, { status: 403 });

  const sessions = getChatSessions(email);
  return NextResponse.json({ sessions });
}

export async function POST(request: Request) {
  const session = await auth();
  const email = (session?.user as { email?: string } | undefined)?.email;
  if (!email) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const user = getPortalUser(email);
  if (!user?.chat_enabled) return NextResponse.json({ error: "Chat not enabled for your account" }, { status: 403 });

  const body = await request.json().catch(() => ({})) as { title?: string };
  const id = randomUUID();
  const chatSession = createChatSession(email, id, body.title);
  return NextResponse.json({ session: chatSession }, { status: 201 });
}
