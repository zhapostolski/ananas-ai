import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { fetchGa4Summary, resolveGa4Dates } from "@/lib/ga4-portal";

export async function GET(request: Request) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const range = searchParams.get("range") ?? "last_7d";
  const { startDate, endDate } = resolveGa4Dates(range);

  try {
    const summary = await fetchGa4Summary(startDate, endDate);
    return NextResponse.json({ startDate, endDate, ...summary });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
