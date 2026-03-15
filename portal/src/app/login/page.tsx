"use client";

import { signIn } from "next-auth/react";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="w-full max-w-sm rounded-2xl border bg-white p-8 shadow-sm">
        <div className="mb-8 text-center">
          <div className="mb-3 text-5xl">🍍</div>
          <h1 className="text-xl font-bold">Ananas AI Platform</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Sign in with your Ananas account
          </p>
        </div>

        <Button
          className="w-full"
          onClick={() => signIn("microsoft-entra-id", { callbackUrl: "/marketing" })}
        >
          <svg className="mr-2 h-4 w-4" viewBox="0 0 21 21" xmlns="http://www.w3.org/2000/svg">
            <rect x="1" y="1" width="9" height="9" fill="#f25022" />
            <rect x="11" y="1" width="9" height="9" fill="#7fba00" />
            <rect x="1" y="11" width="9" height="9" fill="#00a4ef" />
            <rect x="11" y="11" width="9" height="9" fill="#ffb900" />
          </svg>
          Sign in with Microsoft
        </Button>

        <p className="mt-4 text-center text-xs text-muted-foreground">
          Secured by Entra ID — only @ananas.mk accounts allowed
        </p>
      </div>
    </div>
  );
}
