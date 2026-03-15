import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getUserActivity, getUserMostVisitedPages } from "@/lib/db-portal";

export async function GET(request: Request) {
  const session = await auth();
  if (!session?.user?.email) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { searchParams } = new URL(request.url);
  const limit = Math.min(parseInt(searchParams.get("limit") ?? "20"), 50);

  const activity = getUserActivity(session.user.email, limit);
  const topPages = getUserMostVisitedPages(session.user.email, 5);

  return NextResponse.json({ activity, top_pages: topPages });
}
