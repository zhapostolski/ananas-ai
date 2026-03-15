/**
 * GA4 Data API client for the portal.
 * Uses service account credentials (JWT -> access token) via Node.js built-in crypto.
 * Env vars: GA4_PROPERTY_ID, GA4_CREDENTIALS (path to service account JSON)
 */
import { createSign } from "crypto";
import { readFileSync } from "fs";

interface ServiceAccountKey {
  client_email: string;
  private_key: string;
}

interface ChannelRow {
  channel: string;
  sessions: number;
  revenue: number;
  users: number;
}

interface Ga4Summary {
  sessions: number;
  users: number;
  revenue: number;
  conversionRate: number;
  channels: ChannelRow[];
}

let _cachedToken: { token: string; expiresAt: number } | null = null;

function loadServiceAccount(): ServiceAccountKey {
  const credPath = process.env.GA4_CREDENTIALS;
  if (!credPath) throw new Error("GA4_CREDENTIALS env var not set");
  return JSON.parse(readFileSync(credPath, "utf-8")) as ServiceAccountKey;
}

function base64url(buf: Buffer | string): string {
  const b = typeof buf === "string" ? Buffer.from(buf) : buf;
  return b.toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function getAccessToken(): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  if (_cachedToken && _cachedToken.expiresAt > now + 60) {
    return _cachedToken.token;
  }

  const sa = loadServiceAccount();
  const header = base64url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const payload = base64url(
    JSON.stringify({
      iss: sa.client_email,
      scope: "https://www.googleapis.com/auth/analytics.readonly",
      aud: "https://oauth2.googleapis.com/token",
      exp: now + 3600,
      iat: now,
    })
  );

  const sigInput = `${header}.${payload}`;
  const sign = createSign("RSA-SHA256");
  sign.update(sigInput);
  const sig = sign.sign(sa.private_key, "base64")
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

  const jwt = `${sigInput}.${sig}`;

  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
      assertion: jwt,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GA4 token error: ${res.status} ${text}`);
  }

  const data = (await res.json()) as { access_token: string; expires_in: number };
  _cachedToken = { token: data.access_token, expiresAt: now + data.expires_in };
  return data.access_token;
}

export async function fetchGa4Summary(startDate: string, endDate: string): Promise<Ga4Summary> {
  const propertyId = process.env.GA4_PROPERTY_ID;
  if (!propertyId) throw new Error("GA4_PROPERTY_ID env var not set");

  const token = await getAccessToken();

  const body = {
    dateRanges: [{ startDate, endDate }],
    dimensions: [{ name: "sessionDefaultChannelGroup" }],
    metrics: [
      { name: "sessions" },
      { name: "totalUsers" },
      { name: "purchaseRevenue" },
      { name: "ecommercePurchases" },
    ],
  };

  const res = await fetch(
    `https://analyticsdata.googleapis.com/v1beta/properties/${propertyId}:runReport`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    }
  );

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GA4 API error: ${res.status} ${text}`);
  }

  const data = await res.json() as {
    rows?: Array<{ dimensionValues: Array<{ value: string }>; metricValues: Array<{ value: string }> }>;
  };

  const rows = data.rows ?? [];
  let totalSessions = 0;
  let totalUsers = 0;
  let totalRevenue = 0;
  let totalPurchases = 0;

  const channels: ChannelRow[] = rows.map((r) => {
    const channel = r.dimensionValues[0].value;
    const sessions = parseInt(r.metricValues[0].value, 10) || 0;
    const users = parseInt(r.metricValues[1].value, 10) || 0;
    const revenue = parseFloat(r.metricValues[2].value) || 0;
    const purchases = parseInt(r.metricValues[3].value, 10) || 0;
    totalSessions += sessions;
    totalUsers += users;
    totalRevenue += revenue;
    totalPurchases += purchases;
    return { channel, sessions, revenue, users };
  });

  channels.sort((a, b) => b.sessions - a.sessions);

  const conversionRate = totalSessions > 0 ? (totalPurchases / totalSessions) * 100 : 0;

  return { sessions: totalSessions, users: totalUsers, revenue: totalRevenue, conversionRate, channels };
}

/** Resolve preset string to GA4 date strings (YYYY-MM-DD). */
export function resolveGa4Dates(preset: string): { startDate: string; endDate: string } {
  const now = new Date();
  const fmt = (d: Date) => d.toISOString().slice(0, 10);

  switch (preset) {
    case "today":
      return { startDate: fmt(now), endDate: fmt(now) };
    case "yesterday": {
      const d = new Date(now);
      d.setDate(d.getDate() - 1);
      return { startDate: fmt(d), endDate: fmt(d) };
    }
    case "last_7d": {
      const d = new Date(now);
      d.setDate(d.getDate() - 6);
      return { startDate: fmt(d), endDate: fmt(now) };
    }
    case "last_week": {
      // Previous Mon-Sun
      const day = now.getDay() || 7;
      const mon = new Date(now);
      mon.setDate(now.getDate() - day - 6);
      const sun = new Date(mon);
      sun.setDate(mon.getDate() + 6);
      return { startDate: fmt(mon), endDate: fmt(sun) };
    }
    case "mtd": {
      const start = new Date(now.getFullYear(), now.getMonth(), 1);
      return { startDate: fmt(start), endDate: fmt(now) };
    }
    case "last_month": {
      const start = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const end = new Date(now.getFullYear(), now.getMonth(), 0);
      return { startDate: fmt(start), endDate: fmt(end) };
    }
    case "qtd": {
      const q = Math.floor(now.getMonth() / 3);
      const start = new Date(now.getFullYear(), q * 3, 1);
      return { startDate: fmt(start), endDate: fmt(now) };
    }
    case "ytd": {
      const start = new Date(now.getFullYear(), 0, 1);
      return { startDate: fmt(start), endDate: fmt(now) };
    }
    default: {
      // Try custom format "2024-01-01,2024-01-31"
      if (preset.includes(",")) {
        const [s, e] = preset.split(",");
        return { startDate: s, endDate: e };
      }
      const d = new Date(now);
      d.setDate(d.getDate() - 6);
      return { startDate: fmt(d), endDate: fmt(now) };
    }
  }
}
