import NextAuth from "next-auth";
import { authConfig } from "@/lib/auth.config";
import type { Role } from "@/types";

async function resolveRoleFromDb(email: string): Promise<Role> {
  try {
    const { getPortalUser } = await import("@/lib/db-portal");
    const user = getPortalUser(email);
    if (user?.role) return user.role as Role;
  } catch {
    // DB unavailable -- fall through to authConfig default
  }
  return "performance_marketer";
}

interface GraphProfile {
  displayName?: string;
  jobTitle?: string;
  department?: string;
  mobilePhone?: string;
  officeLocation?: string;
  birthday?: string;
}

/**
 * Fetch the signed-in user's profile from Microsoft Graph.
 */
async function fetchGraphProfile(accessToken: string): Promise<GraphProfile | null> {
  try {
    const res = await fetch(
      "https://graph.microsoft.com/v1.0/me?$select=displayName,jobTitle,department,mobilePhone,officeLocation,birthday",
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    if (!res.ok) return null;
    return await res.json() as GraphProfile;
  } catch {
    return null;
  }
}

/**
 * Fetch the signed-in user's profile photo from Microsoft Graph.
 * Returns a base64 data URL or null.
 */
async function fetchUserPhoto(accessToken: string): Promise<string | null> {
  try {
    const res = await fetch("https://graph.microsoft.com/v1.0/me/photo/$value", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (!res.ok) return null;
    const buffer = await res.arrayBuffer();
    const base64 = Buffer.from(buffer).toString("base64");
    const contentType = res.headers.get("content-type") ?? "image/jpeg";
    return `data:${contentType};base64,${base64}`;
  } catch {
    return null;
  }
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  ...authConfig,
  callbacks: {
    ...authConfig.callbacks,
    async jwt({ token, profile, account }) {
      if (profile && token.email) {
        token.role = await resolveRoleFromDb(token.email);
        // Store access token for Graph API use in signIn event
        if (account?.access_token) {
          token.accessToken = account.access_token;
        }
      }
      return token;
    },
  },
  events: {
    async signIn({ user, account }) {
      if (!user.email) return;
      try {
        const { getOrCreatePortalUser, touchLastSeen, updatePortalUser, getPendingInvite, markInviteUsed, auditRoleChange, getPortalUser } = await import(
          "@/lib/db-portal"
        );
        getOrCreatePortalUser(user.email, user.name);
        touchLastSeen(user.email);

        // Apply pending invite role if present
        const pendingInvite = getPendingInvite(user.email);
        if (pendingInvite) {
          const existing = getPortalUser(user.email);
          if (existing) {
            auditRoleChange(user.email, existing.role, pendingInvite.role, "system", "Applied from invite");
          }
          markInviteUsed(user.email);
        }

        // Fetch and cache user data from Microsoft Graph
        if (account?.access_token) {
          const [photoUrl, graphProfile] = await Promise.all([
            fetchUserPhoto(account.access_token),
            fetchGraphProfile(account.access_token),
          ]);
          const updates: Parameters<typeof updatePortalUser>[1] = {};
          if (photoUrl) updates.avatar_url = photoUrl;
          if (graphProfile?.displayName) updates.display_name = graphProfile.displayName;
          if (graphProfile?.jobTitle) updates.azure_job_title = graphProfile.jobTitle;
          if (graphProfile?.department) updates.azure_department = graphProfile.department;
          if (graphProfile?.mobilePhone) updates.azure_phone = graphProfile.mobilePhone;
          if (graphProfile?.officeLocation) updates.azure_office = graphProfile.officeLocation;
          if (graphProfile?.birthday) updates.birth_date = graphProfile.birthday;
          if (Object.keys(updates).length > 0) {
            updatePortalUser(user.email, updates);
          }
        }
      } catch {
        // Non-fatal
      }
    },
  },
});
