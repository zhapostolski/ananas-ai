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

export const { handlers, auth, signIn, signOut } = NextAuth({
  ...authConfig,
  callbacks: {
    ...authConfig.callbacks,
    async jwt({ token, profile }) {
      if (profile && token.email) {
        token.role = await resolveRoleFromDb(token.email);
      }
      return token;
    },
  },
  events: {
    async signIn({ user }) {
      if (!user.email) return;
      try {
        const { getOrCreatePortalUser, touchLastSeen } = await import(
          "@/lib/db-portal"
        );
        getOrCreatePortalUser(user.email, user.name);
        touchLastSeen(user.email);
      } catch {
        // Non-fatal
      }
    },
  },
});
