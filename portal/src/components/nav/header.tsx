"use client";

import { usePathname } from "next/navigation";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { UserMenu } from "@/components/nav/user-menu";
import { NotificationBell } from "@/components/nav/notification-bell";
import type { Role } from "@/types";

const BREADCRUMBS: Record<string, string> = {
  "/marketing/overview": "Overview",
  "/marketing/performance": "Performance & Paid Media",
  "/marketing/crm": "CRM & Lifecycle",
  "/marketing/reputation": "Reputation",
  "/marketing/influencers": "Influencers",
  "/marketing/ops": "Marketing Ops",
  "/finance": "Finance",
  "/logistics": "Logistics",
  "/executive": "Executive",
  "/customer-experience": "Customer Experience",
  "/customer-experience/reputation": "Reputation & Reviews",
  "/customer-experience/support": "Support Insights",
  "/profile": "My Profile",
  "/settings": "Settings",
  "/admin/users": "User Management",
  "/admin/users/invite": "Invite User",
  "/admin/notifications": "Send Notification",
  "/hr": "HR",
  "/hr/team": "Team",
  "/hr/attendance": "Attendance",
};

function getPageTitle(pathname: string): string {
  if (BREADCRUMBS[pathname]) return BREADCRUMBS[pathname];
  for (const [prefix, label] of Object.entries(BREADCRUMBS)) {
    if (pathname.startsWith(prefix + "/")) return label;
  }
  return "Ananas AI";
}

interface HeaderProps {
  name?: string | null;
  email?: string | null;
  role: Role;
  avatarColor?: string;
  avatarUrl?: string | null;
  userEmail?: string;
}

export function Header({ name, email, role, avatarColor = "#FE5000", avatarUrl, userEmail }: HeaderProps) {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const pageTitle = getPageTitle(pathname);
  const isAdmin = ["super_admin", "executive", "marketing_head", "finance_head", "logistics_head", "cx_head", "commercial_head", "hr_head"].includes(role);

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b bg-card px-6 gap-4">
      <div className="flex items-center gap-2 min-w-0">
        <span className="text-sm font-semibold truncate">{pageTitle}</span>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {/* Dark mode toggle */}
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="flex h-8 w-8 items-center justify-center rounded-lg hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
          title="Toggle theme"
          aria-label="Toggle theme"
        >
          {theme === "dark" ? (
            <Sun className="h-4 w-4" />
          ) : (
            <Moon className="h-4 w-4" />
          )}
        </button>

        {/* Notification bell */}
        <NotificationBell userEmail={userEmail ?? email ?? ""} />

        {/* Divider */}
        <div className="h-6 w-px bg-border mx-1" />

        <UserMenu
          name={name}
          email={email}
          role={role}
          avatarColor={avatarColor}
          avatarUrl={avatarUrl}
          isAdmin={isAdmin}
        />
      </div>
    </header>
  );
}
