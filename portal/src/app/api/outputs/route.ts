import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getLatestOutput, getOutputHistory } from "@/lib/db";

export async function GET(req: NextRequest) {
  const session = await auth();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { searchParams } = req.nextUrl;
  const agentId = searchParams.get("agent");
  const history = searchParams.get("history") === "1";
  const days = parseInt(searchParams.get("days") ?? "7");

  if (!agentId) {
    return NextResponse.json({ error: "agent param required" }, { status: 400 });
  }

  if (history) {
    const rows = getOutputHistory(agentId, days);
    return NextResponse.json({ data: rows });
  }

  const row = getLatestOutput(agentId);
  if (!row) {
    return NextResponse.json({ data: null });
  }

  return NextResponse.json({ data: row });
}
