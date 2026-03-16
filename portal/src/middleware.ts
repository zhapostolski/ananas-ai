import NextAuth from "next-auth";
import { authConfig } from "@/lib/auth.config";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import type { Role } from "@/types";

const { auth } = NextAuth(authConfig);

const PUBLIC_PATHS = ["/login", "/api/auth"];

const PROTECTED_ROUTES: Array<{
  pattern: RegExp;
  requiredRoles: Role[];
}> = [
  {
    pattern: /^\/admin/,
    requiredRoles: ["executive", "marketing_head"],
  },
  {
    pattern: /^\/finance/,
    requiredRoles: [
      "executive",
      "finance_head",
      "finance_team",
      "marketing_head",
    ],
  },
  {
    pattern: /^\/logistics/,
    requiredRoles: [
      "executive",
      "logistics_head",
      "logistics_team",
      "finance_head",
    ],
  },
  {
    pattern: /^\/commercial/,
    requiredRoles: [
      "executive",
      "commercial_head",
      "commercial_3p",
      "commercial_1p",
      "finance_head",
      "logistics_head",
    ],
  },
  {
    pattern: /^\/executive/,
    requiredRoles: [
      "executive",
      "marketing_head",
      "finance_head",
      "cx_head",
    ],
  },
  {
    pattern: /^\/marketing/,
    requiredRoles: [
      "executive",
      "marketing_head",
      "performance_marketer",
      "crm_specialist",
      "content_brand",
      "marketing_ops",
      "commercial_head",
      "finance_head",
      "cx_head",
    ],
  },
  {
    pattern: /^\/customer-experience/,
    requiredRoles: ["executive", "cx_head", "cx_team", "marketing_head"],
  },
];

export default auth((req: NextRequest & { auth: unknown }) => {
  const pathname = req.nextUrl.pathname;

  const isPublic = PUBLIC_PATHS.some((p) => pathname.startsWith(p));

  // If a non-public page has a session cookie that failed to decrypt
  // (JWTSessionError), wipe every auth cookie variant and redirect to /login.
  // The cookie names and Secure attributes must match exactly so the browser
  // actually deletes them.
  const hasSessionCookie =
    req.cookies.has("authjs.session-token") ||
    req.cookies.has("__Secure-authjs.session-token") ||
    req.cookies.has("next-auth.session-token");

  if (!req.auth && hasSessionCookie && !isPublic) {
    const res = NextResponse.redirect(new URL("/login", req.url));
    // Plain cookies (no Secure flag)
    for (const name of ["authjs.session-token", "authjs.callback-url", "authjs.csrf-token", "next-auth.session-token", "next-auth.csrf-token", "next-auth.callback-url"]) {
      res.cookies.set({ name, value: "", maxAge: 0, path: "/", httpOnly: true, sameSite: "lax" });
    }
    // Secure-prefixed cookies
    for (const name of ["__Secure-authjs.session-token", "__Secure-authjs.callback-url"]) {
      res.cookies.set({ name, value: "", maxAge: 0, path: "/", httpOnly: true, secure: true, sameSite: "lax" });
    }
    // __Host-prefixed cookie (must have secure, httpOnly, path=/, no domain)
    res.cookies.set({ name: "__Host-authjs.csrf-token", value: "", maxAge: 0, path: "/", httpOnly: true, secure: true, sameSite: "lax" });
    return res;
  }

  if (!req.auth && !isPublic) {
    return NextResponse.redirect(new URL("/login", req.url));
  }

  if (!req.auth) return NextResponse.next();

  const role = (
    (req.auth as { user?: { role?: Role } })?.user?.role ?? "performance_marketer"
  ) as Role;

  for (const route of PROTECTED_ROUTES) {
    if (route.pattern.test(pathname)) {
      if (!route.requiredRoles.includes(role)) {
        return NextResponse.redirect(new URL("/marketing/overview", req.url));
      }
      break;
    }
  }

  return NextResponse.next();
});

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.png$|.*\\.svg$).*)",
  ],
};
