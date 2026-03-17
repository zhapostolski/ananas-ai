import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";

const SUPPORTED = ["en", "sr", "mk"] as const;
type Lang = (typeof SUPPORTED)[number];

const GT_LANG: Record<Lang, string> = { en: "en", sr: "sr", mk: "mk" };

async function googleTranslate(text: string, source: Lang, target: Lang): Promise<string> {
  const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${GT_LANG[source]}&tl=${GT_LANG[target]}&dt=t&q=${encodeURIComponent(text)}`;
  const res = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0" } });
  if (!res.ok) throw new Error(`Google Translate HTTP ${res.status}`);
  const data = (await res.json()) as Array<Array<Array<string>>>;
  return data[0]?.map((chunk) => chunk[0]).join("") ?? text;
}

function detectLanguage(text: string): Lang {
  // Simple heuristic: check for Macedonian-specific characters and words
  // Full detection is done server-side in Python; this is a lightweight fallback
  const cyrillic = /[\u0400-\u04FF]/.test(text);
  if (!cyrillic) return "en";
  // Macedonian-specific letters: Ѓ ѓ Ќ ќ Ѕ ѕ Ј ј Љ љ Њ њ Џ џ
  const mkSpecific = /[ЃѓЌќЅѕЈјЉљЊњЏџ]/.test(text);
  return mkSpecific ? "mk" : "sr";
}

export async function POST(request: Request) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json().catch(() => null) as {
    text?: string;
    target?: string;
    source?: string;
  } | null;

  const text = body?.text?.trim();
  if (!text) return NextResponse.json({ error: "Missing text" }, { status: 400 });

  const target = body?.target as Lang | undefined;
  if (!target || !SUPPORTED.includes(target)) {
    return NextResponse.json({ error: `Invalid target. Supported: ${SUPPORTED.join(", ")}` }, { status: 400 });
  }

  const source: Lang = (body?.source && SUPPORTED.includes(body.source as Lang))
    ? (body.source as Lang)
    : detectLanguage(text);

  if (source === target) {
    return NextResponse.json({ original: text, translated: text, source, target, cached: true });
  }

  try {
    const translated = await googleTranslate(text, source, target);
    return NextResponse.json({ original: text, translated, source, target });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Translation failed";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}

export async function GET() {
  return NextResponse.json({
    supported_languages: [
      { code: "en", label: "English", native: "English" },
      { code: "sr", label: "Serbian", native: "Srpski" },
      { code: "mk", label: "Macedonian", native: "Македонски" },
    ],
  });
}
