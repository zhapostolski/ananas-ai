"use client";

import { signOut } from "next-auth/react";
import Link from "next/link";
import { LogOut, User, Settings, Shield } from "lucide-react";
import { ROLE_LABELS } from "@/lib/roles";
import type { Role } from "@/types";

function getInitials(name?: string | null, email?: string | null): string {
  if (name) {
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return name.slice(0, 2).toUpperCase();
  }
  if (email) return email.slice(0, 2).toUpperCase();
  return "AN";
}

interface UserMenuProps {
  name?: string | null;
  email?: string | null;
  role: Role;
  avatarColor?: string;
  avatarUrl?: string | null;
  isAdmin?: boolean;
}

export function UserAvatar({
  name,
  email,
  avatarColor = "#FE5000",
  avatarUrl,
  size = "sm",
}: {
  name?: string | null;
  email?: string | null;
  avatarColor?: string;
  avatarUrl?: string | null;
  size?: "sm" | "md";
}) {
  const initials = getInitials(name, email);
  const dim = size === "md" ? "h-9 w-9 text-sm" : "h-7 w-7 text-xs";
  if (avatarUrl) {
    return (
      <img
        src={avatarUrl}
        alt={name ?? email ?? "avatar"}
        className={`${dim} shrink-0 rounded-full object-cover`}
      />
    );
  }
  return (
    <div
      className={`flex ${dim} shrink-0 items-center justify-center rounded-full font-semibold text-white select-none`}
      style={{ backgroundColor: avatarColor }}
    >
      {initials}
    </div>
  );
}

export function UserMenu({ name, email, role, avatarColor = "#FE5000", avatarUrl, isAdmin = false }: UserMenuProps) {
  return (
    <div className="group relative">
      <button
        className="flex items-center gap-2 rounded-lg p-1 hover:bg-accent transition-colors"
        aria-label="User menu"
      >
        <UserAvatar name={name} email={email} avatarColor={avatarColor} avatarUrl={avatarUrl} size="sm" />
        <span className="hidden lg:block text-sm font-medium max-w-[120px] truncate">
          {name ?? email}
        </span>
      </button>

      <div className="absolute right-0 top-full z-50 mt-1 hidden w-52 rounded-xl border border-border bg-white dark:bg-gray-900 shadow-xl ring-1 ring-black/5 group-focus-within:block group-hover:block">
        <div className="px-3 py-2 border-b">
          <p className="text-sm font-medium truncate">{name ?? email}</p>
          <p className="text-xs text-muted-foreground truncate">{email}</p>
          <span
            className="mt-1 inline-block rounded-full px-2 py-0.5 text-xs font-medium text-white"
            style={{ backgroundColor: "#FE5000" }}
          >
            {ROLE_LABELS[role]}
          </span>
        </div>

        <div className="py-1">
          <Link
            href="/profile"
            className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent transition-colors"
          >
            <User className="h-4 w-4 text-muted-foreground" />
            My Profile
          </Link>
          <Link
            href="/settings"
            className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent transition-colors"
          >
            <Settings className="h-4 w-4 text-muted-foreground" />
            Settings
          </Link>
          {isAdmin && (
            <Link
              href="/admin/users"
              className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent transition-colors"
            >
              <Shield className="h-4 w-4 text-muted-foreground" />
              Admin
            </Link>
          )}
        </div>

        <div className="border-t py-1">
          <button
            onClick={() => signOut({ callbackUrl: "/login" })}
            className="flex w-full items-center gap-2 px-3 py-2 text-sm text-red-500 hover:bg-accent transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}
