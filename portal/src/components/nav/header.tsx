"use client";

import { signOut } from "next-auth/react";
import { LogOut, User } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ROLE_LABELS } from "@/lib/roles";
import type { Role } from "@/types";

interface HeaderProps {
  name?: string | null;
  email?: string | null;
  role: Role;
}

export function Header({ name, email, role }: HeaderProps) {
  return (
    <header className="flex h-14 items-center justify-between border-b bg-white px-6">
      {/* Orange accent line at top */}
      <div className="absolute top-0 left-0 right-0 h-0.5" style={{ backgroundColor: "#FE5000" }} />
      <div />
      <div className="flex items-center gap-3">
        <Badge
          variant="outline"
          className="text-xs font-medium"
          style={{ borderColor: "#FE5000", color: "#FE5000" }}
        >
          {ROLE_LABELS[role]}
        </Badge>
        <div className="flex items-center gap-2">
          <User className="h-4 w-4 text-gray-400" />
          <span className="text-sm text-gray-500">{name ?? email}</span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => signOut({ callbackUrl: "/login" })}
          title="Sign out"
          className="hover:text-orange-600"
        >
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
