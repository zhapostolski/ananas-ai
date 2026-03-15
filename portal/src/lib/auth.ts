import NextAuth from "next-auth";
import MicrosoftEntraID from "next-auth/providers/microsoft-entra-id";
import type { Role } from "@/types";

/**
 * Map Entra ID group membership or email to a platform role.
 * Extend this map once Azure group IDs are confirmed.
 */
const EMAIL_ROLE_MAP: Record<string, Role> = {
  "zharko.apostolski@ananas.mk": "marketing_head",
};

function resolveRole(email: string | undefined | null): Role {
  if (!email) return "marketing_ops";
  return EMAIL_ROLE_MAP[email.toLowerCase()] ?? "performance_marketer";
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    MicrosoftEntraID({
      clientId: process.env.AZURE_AD_CLIENT_ID!,
      clientSecret: process.env.AZURE_AD_CLIENT_SECRET!,
      issuer: `https://login.microsoftonline.com/${process.env.AZURE_AD_TENANT_ID!}/v2.0`,
    }),
  ],
  callbacks: {
    async jwt({ token, profile }) {
      if (profile) {
        token.role = resolveRole(token.email);
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as { role?: Role }).role = token.role as Role;
      }
      return session;
    },
  },
  pages: {
    signIn: "/login",
    error: "/login",
  },
});
