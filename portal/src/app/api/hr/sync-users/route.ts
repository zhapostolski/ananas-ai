import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { getOrgUsers, getUserPhoto } from "@/lib/graph";
import { getPortalDb } from "@/lib/db-portal";
import { isAdminRole } from "@/lib/roles";
import type { Role } from "@/types";

/**
 * POST /api/hr/sync-users
 * Pulls all Azure AD users into the portal DB.
 * Only admins and HR heads can trigger this.
 *
 * GET /api/hr/sync-users
 * Returns all org users from Azure Graph (no DB sync, just read).
 */

export async function GET() {
  const session = await auth();
  const role = (session?.user as { role?: Role } | undefined)?.role;
  if (!session?.user || !role) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const users = await getOrgUsers();
  return NextResponse.json({ users, count: users.length });
}

export async function POST() {
  const session = await auth();
  const role = (session?.user as { role?: Role } | undefined)?.role;
  if (!session?.user || !role || !isAdminRole(role)) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const orgUsers = await getOrgUsers();
  if (orgUsers.length === 0) {
    return NextResponse.json({ error: "No users returned from Azure. Check app permissions." }, { status: 502 });
  }

  const db = getPortalDb();
  let synced = 0;
  let photos = 0;

  for (const u of orgUsers) {
    const email = (u.mail ?? u.userPrincipalName).toLowerCase();
    if (!email) continue;

    // Upsert: create if not exists, update Azure fields
    const existing = db.prepare("SELECT id FROM portal_users WHERE email = ?").get(email);

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
    }

    // Fetch and store photo for users without one
    const withPhoto = db.prepare("SELECT avatar_url FROM portal_users WHERE email = ?").get(email) as { avatar_url: string | null } | undefined;
    if (!withPhoto?.avatar_url && u.userPrincipalName) {
      const photo = await getUserPhoto(u.userPrincipalName);
      if (photo) {
        db.prepare("UPDATE portal_users SET avatar_url = ? WHERE email = ?").run(photo, email);
        photos++;
      }
    }

    synced++;
  }

  return NextResponse.json({ ok: true, synced, photos });
}
