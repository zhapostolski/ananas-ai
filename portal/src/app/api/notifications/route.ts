import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getNotificationsForUser, countUnreadForUser } from "@/lib/db-portal";

export async function GET() {
  const session = await auth();
  if (!session?.user?.email) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const email = session.user.email;
  const notifications = getNotificationsForUser(email, 30);
  const unread = countUnreadForUser(email);

  return NextResponse.json({ notifications, unread });
}
