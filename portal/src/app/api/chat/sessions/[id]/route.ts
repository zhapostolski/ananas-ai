import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getChatSession, deleteChatSession, getChatMessages } from "@/lib/db-portal";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await auth();
  const email = (session?.user as { email?: string } | undefined)?.email;
  if (!email) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { id } = await params;
  const chatSession = getChatSession(id, email);
  if (!chatSession) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const messages = getChatMessages(id);
  return NextResponse.json({ session: chatSession, messages });
}

export async function DELETE(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await auth();
  const email = (session?.user as { email?: string } | undefined)?.email;
  if (!email) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { id } = await params;
  deleteChatSession(id, email);
  return NextResponse.json({ ok: true });
}
