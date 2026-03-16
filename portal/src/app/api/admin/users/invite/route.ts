import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { createRoleInvite } from "@/lib/db-portal";
import { ROLE_LABELS, canInvite } from "@/lib/roles";
import { getGraphToken } from "@/lib/graph";
import type { Role } from "@/types";

async function sendViaGraph(
  accessToken: string,
  fromEmail: string,
  toEmail: string,
  subject: string,
  html: string
): Promise<boolean> {
  const res = await fetch(
    `https://graph.microsoft.com/v1.0/users/${encodeURIComponent(fromEmail)}/sendMail`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: {
          subject,
          body: { contentType: "HTML", content: html },
          toRecipients: [{ emailAddress: { address: toEmail } }],
        },
        saveToSentItems: false,
      }),
    }
  );
  return res.status === 202;
}

async function sendInviteEmail(
  toEmail: string,
  role: Role,
  invitedBy: string,
): Promise<{ sent: boolean; from: string }> {
  const roleLabel = ROLE_LABELS[role] ?? role;
  const portalUrl = process.env.PORTAL_URL ?? "https://ai.ananas.mk";

  const html = `
<div style="font-family: sans-serif; max-width: 480px; margin: 0 auto; padding: 24px; color: #111827;">
  <div style="margin-bottom: 24px;">
    <span style="font-size: 20px; font-weight: 700; color: #FE5000;">Ananas AI</span>
    <span style="font-size: 14px; font-weight: 600; color: #6B7280; margin-left: 6px;">Portal</span>
  </div>
  <h2 style="font-size: 18px; font-weight: 700; margin: 0 0 8px;">You have been invited to Ananas AI Platform</h2>
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

  const subject = "You have been invited to Ananas AI Platform";
  const systemFrom = process.env.INVITE_FROM_EMAIL ?? "no-reply@ananas.mk";

  // Try 1: app-level client_credentials (requires Mail.Send application permission)
  try {
    const appToken = await getGraphToken();
    if (appToken) {
      const ok = await sendViaGraph(appToken, systemFrom, toEmail, subject, html);
      if (ok) return { sent: true, from: systemFrom };
    }
  } catch { /* fall through */ }

  return { sent: false, from: "" };
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

  const { sent, from } = await sendInviteEmail(
    email,
    role,
    session.user.email,
  ).catch(() => ({ sent: false, from: "" }));

  return NextResponse.json({ ok: true, emailSent: sent, emailFrom: from });
}
