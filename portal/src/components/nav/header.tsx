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
    <header className="flex h-14 items-center justify-between border-b bg-background px-6">
      <div />
      <div className="flex items-center gap-3">
        <Badge variant="outline" className="text-xs">
          {ROLE_LABELS[role]}
        </Badge>
        <div className="flex items-center gap-2">
          <User className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">{name ?? email}</span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => signOut({ callbackUrl: "/login" })}
          title="Sign out"
        >
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
