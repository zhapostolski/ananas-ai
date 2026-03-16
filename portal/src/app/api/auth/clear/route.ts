import { NextResponse } from "next/server";

const COOKIE_NAMES = [
  // Session tokens — prefixed and unprefixed
  "authjs.session-token",
  "__Secure-authjs.session-token",
  // PKCE verifier — prefixed and unprefixed (added in builds with useSecureCookies:false)
  "authjs.pkce.code_verifier",
  "__Secure-authjs.pkce.code_verifier",
  // Callback URLs
  "authjs.callback-url",
  "__Secure-authjs.callback-url",
  // CSRF tokens
  "authjs.csrf-token",
  "__Host-authjs.csrf-token",
  "__Secure-authjs.csrf-token",
  // next-auth v4 variants
  "next-auth.session-token",
  "next-auth.callback-url",
  "next-auth.csrf-token",
  "__Secure-next-auth.session-token",
  "__Host-next-auth.csrf-token",
  "__Secure-next-auth.pkce.code_verifier",
];

export async function GET() {
  const res = NextResponse.redirect(
    new URL("/login", process.env.NEXTAUTH_URL ?? "https://52.29.60.185"),
    { status: 302 }
  );

  for (const name of COOKIE_NAMES) {
    // Delete without Secure (plain cookies)
    res.cookies.set({ name, value: "", maxAge: 0, path: "/" });
    // Delete with Secure (Secure/Host-prefixed cookies)
    res.cookies.set({ name, value: "", maxAge: 0, path: "/", secure: true });
    // Delete with HttpOnly variants
    res.cookies.set({ name, value: "", maxAge: 0, path: "/", httpOnly: true });
    res.cookies.set({ name, value: "", maxAge: 0, path: "/", httpOnly: true, secure: true });
    // Delete with SameSite=Lax variants
    res.cookies.set({ name, value: "", maxAge: 0, path: "/", httpOnly: true, sameSite: "lax" });
    res.cookies.set({ name, value: "", maxAge: 0, path: "/", httpOnly: true, secure: true, sameSite: "lax" });
  }

  return res;
}
