/**
 * Edge-compatible auth config for middleware.
 * Must not import any Node.js-only modules (better-sqlite3, fs, path).
 */
import type { NextAuthConfig } from "next-auth";
import MicrosoftEntraID from "next-auth/providers/microsoft-entra-id";
import type { Role } from "@/types";

const EMAIL_ROLE_MAP: Record<string, Role> = {
  "zharko.apostolski@ananas.mk": "executive",
};

export const authConfig: NextAuthConfig = {
  trustHost: true,
  // Explicit cookie config: use __Secure- prefix (works on HTTPS incl. self-signed IP certs).
  // Avoids next-auth beta HKDF salt mismatch that occurs with useSecureCookies:false.
  // Switch to __Host- prefix (remove this override) when running on ai.ananas.mk with real cert.
  cookies: {
    sessionToken: {
      name: "__Secure-authjs.session-token",
      options: { httpOnly: true, sameSite: "lax", path: "/", secure: true },
    },
    callbackUrl: {
      name: "__Secure-authjs.callback-url",
      options: { httpOnly: true, sameSite: "lax", path: "/", secure: true },
    },
    csrfToken: {
      name: "authjs.csrf-token",
      options: { httpOnly: true, sameSite: "lax", path: "/" },
    },
    pkceCodeVerifier: {
      name: "__Secure-authjs.pkce.code_verifier",
      options: { httpOnly: true, sameSite: "lax", path: "/", secure: true },
    },
    state: {
      name: "__Secure-authjs.state",
      options: { httpOnly: true, sameSite: "lax", path: "/", secure: true },
    },
    nonce: {
      name: "__Secure-authjs.nonce",
      options: { httpOnly: true, sameSite: "lax", path: "/", secure: true },
    },
  },
  providers: [
    MicrosoftEntraID({
      clientId: process.env.AZURE_AD_CLIENT_ID!,
      clientSecret: process.env.AZURE_AD_CLIENT_SECRET!,
      issuer: `https://login.microsoftonline.com/${process.env.AZURE_AD_TENANT_ID!}/v2.0`,
      authorization: {
        params: {
          scope: "openid profile email User.Read Mail.Send offline_access",
        },
      },
    }),
  ],
  callbacks: {
    jwt({ token }) {
      // In edge context: preserve existing role or assign default.
      // Full DB-based resolution happens in auth.ts on sign-in.
      if (!token.role) {
        token.role =
          EMAIL_ROLE_MAP[(token.email ?? "").toLowerCase()] ??
          "performance_marketer";
      }
      return token;
    },
    session({ session, token }) {
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
};
