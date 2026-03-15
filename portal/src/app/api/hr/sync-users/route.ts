import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getOrgUsers, getUserPhoto } from "@/lib/graph";
import { getPortalDb } from "@/lib/db-portal";
import type { Role } from "@/types";

const SYNC_ROLES: Role[] = ["super_admin", "executive", "hr_head", "hr"];

/**
 * GET /api/hr/sync-users
 * Returns cached users from portal DB + last sync time.
 */
export async function GET() {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const db = getPortalDb();
  const lastSync = db
    .prepare("SELECT MAX(updated_at) as last FROM portal_users WHERE azure_job_title IS NOT NULL")
    .get() as { last: string | null } | undefined;

  return NextResponse.json({ lastSync: lastSync?.last ?? null });
}

/**
 * POST /api/hr/sync-users
 * Pulls all Azure AD users into the portal DB.
 * Allowed for: hr, hr_head, executive, super_admin.
 */
export async function POST() {
  const session = await auth();
  const role = (session?.user as { role?: Role } | undefined)?.role;
  if (!session?.user || !role || !SYNC_ROLES.includes(role)) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const orgUsers = await getOrgUsers();
  if (orgUsers.length === 0) {
    return NextResponse.json(
      { error: "No users returned from Azure. Check that User.Read.All permission has admin consent." },
      { status: 502 }
    );
  }

  const db = getPortalDb();
  let synced = 0;
  let photos = 0;

  for (const u of orgUsers) {
    const email = (u.mail ?? u.userPrincipalName).toLowerCase();
    if (!email) continue;

    const existing = db.prepare("SELECT id, avatar_url FROM portal_users WHERE email = ?").get(email) as { id: number; avatar_url: string | null } | undefined;

    if (existing) {
      db.prepare(`
        UPDATE portal_users SET
          display_name = COALESCE(display_name, @display_name),
          azure_job_title = @azure_job_title,
          azure_department = @azure_department,
          azure_phone = @azure_phone,
          azure_office = @azure_office,
          updated_at = datetime('now')
        WHERE email = @email
      `).run({
        email,
        display_name: u.displayName,
        azure_job_title: u.jobTitle,
        azure_department: u.department,
        azure_phone: u.mobilePhone,
        azure_office: u.officeLocation,
      });

      if (!existing.avatar_url && u.userPrincipalName) {
        const photo = await getUserPhoto(u.userPrincipalName);
        if (photo) {
          db.prepare("UPDATE portal_users SET avatar_url = ? WHERE email = ?").run(photo, email);
          photos++;
        }
      }
    } else {
      db.prepare(`
        INSERT INTO portal_users (email, display_name, azure_job_title, azure_department, azure_phone, azure_office)
        VALUES (@email, @display_name, @azure_job_title, @azure_department, @azure_phone, @azure_office)
      `).run({
        email,
        display_name: u.displayName,
        azure_job_title: u.jobTitle,
        azure_department: u.department,
        azure_phone: u.mobilePhone,
        azure_office: u.officeLocation,
      });

      if (u.userPrincipalName) {
        const photo = await getUserPhoto(u.userPrincipalName);
        if (photo) {
          db.prepare("UPDATE portal_users SET avatar_url = ? WHERE email = ?").run(photo, email);
          photos++;
        }
      }
    }

    synced++;
  }

  return NextResponse.json({ ok: true, synced, photos });
}
