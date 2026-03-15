import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { createRoleInvite } from "@/lib/db-portal";
import { ROLE_LABELS, canInvite } from "@/lib/roles";
import type { Role } from "@/types";

async function getGraphAccessToken(): Promise<string | null> {
  const tenantId = process.env.GRAPH_TENANT_ID;
  const clientId = process.env.GRAPH_CLIENT_ID;
  const refreshToken = process.env.GRAPH_REFRESH_TOKEN;

  if (!tenantId || !clientId || !refreshToken) return null;

  const params = new URLSearchParams({
    grant_type: "refresh_token",
    client_id: clientId,
    refresh_token: refreshToken,
    scope: "https://graph.microsoft.com/Mail.Send offline_access",
  });

  const clientSecret = process.env.GRAPH_CLIENT_SECRET;
  if (clientSecret) params.set("client_secret", clientSecret);

  const res = await fetch(
    `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/token`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: params.toString(),
    }
  );

  if (!res.ok) return null;
  const data = await res.json();
  return data.access_token ?? null;
}

async function sendInviteEmail(
  fromEmail: string,
  toEmail: string,
  role: Role,
  invitedBy: string
): Promise<boolean> {
  const token = await getGraphAccessToken();
  if (!token) return false;

  const roleLabel = ROLE_LABELS[role] ?? role;
  const portalUrl = process.env.PORTAL_URL ?? "https://ai.ananas.mk";

  const html = `
<div style="font-family: sans-serif; max-width: 480px; margin: 0 auto; padding: 24px; color: #111827;">
  <div style="margin-bottom: 24px;">
    <span style="font-size: 20px; font-weight: 700; color: #FE5000;">Ananas AI</span>
    <span style="font-size: 14px; font-weight: 600; color: #6B7280; margin-left: 6px;">Portal</span>
  </div>
  <h2 style="font-size: 18px; font-weight: 700; margin: 0 0 8px;">You've been invited to Ananas AI Platform</h2>
  <p style="color: #6B7280; font-size: 14px; margin: 0 0 20px;">
    ${invitedBy} has invited you to access the Ananas AI intelligence portal with the role of <strong>${roleLabel}</strong>.
  </p>
  <a href="${portalUrl}" style="display: inline-block; background: #FE5000; color: white; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-size: 14px; font-weight: 600;">
    Access the Portal
  </a>
  <p style="color: #9CA3AF; font-size: 12px; margin-top: 24px;">
    Sign in with your Ananas Microsoft account (${toEmail}). Your role will be assigned automatically on first login.
  </p>
</div>`;

  const body = {
    message: {
      subject: "You've been invited to Ananas AI Platform",
      body: { contentType: "HTML", content: html },
      toRecipients: [{ emailAddress: { address: toEmail } }],
    },
    saveToSentItems: false,
  };

  const sendRes = await fetch(
    `https://graph.microsoft.com/v1.0/users/${fromEmail}/sendMail`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    }
  );

  return sendRes.status === 202;
}

export async function POST(request: Request) {
  const session = await auth();
  const sessionRole = (session?.user as { role?: Role } | undefined)?.role;
  if (!session?.user?.email || !sessionRole || !canInvite(sessionRole)) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const body = await request.json();
  const email = String(body.email ?? "").toLowerCase().trim();
  const role = String(body.role ?? "") as Role;

  if (!email || !role) {
    return NextResponse.json({ error: "email and role required" }, { status: 400 });
  }

  createRoleInvite(email, role, session.user.email);

  // Send invite email — use configured sender or fall back to no-reply@ananas.mk
  const fromEmail =
    process.env.INVITE_FROM_EMAIL ??
    process.env.EMAIL_FROM_ADDRESS ??
    "no-reply@ananas.mk";

  const emailSent = await sendInviteEmail(
    fromEmail,
    email,
    role,
    session.user.email
  ).catch(() => false);

  return NextResponse.json({ ok: true, emailSent });
}
