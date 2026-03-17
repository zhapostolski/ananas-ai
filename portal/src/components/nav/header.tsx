"use client";

import { usePathname } from "next/navigation";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { UserMenu } from "@/components/nav/user-menu";
import { NotificationBell } from "@/components/nav/notification-bell";
import { LanguageSwitcher } from "@/components/nav/language-switcher";
import { useT } from "@/lib/i18n";
import type { Role } from "@/types";

const BREADCRUMB_KEYS: Record<string, keyof ReturnType<typeof useT>> = {
  "/marketing/overview": "page_overview",
  "/marketing/performance": "page_performance",
  "/marketing/crm": "page_crm",
  "/marketing/reputation": "page_reputation",
  "/marketing/influencers": "page_influencers",
  "/marketing/ops": "page_marketing_ops",
  "/finance": "page_finance",
  "/logistics": "page_logistics",
  "/executive": "page_executive",
  "/customer-experience": "page_customer_experience",
  "/customer-experience/reputation": "page_reputation_reviews",
  "/customer-experience/support": "page_support_insights",
  "/profile": "page_profile",
  "/settings": "page_settings",
  "/admin/users": "page_user_management",
  "/admin/users/invite": "page_invite_user",
  "/admin/notifications": "page_send_notification",
  "/hr": "page_hr",
  "/hr/team": "page_team",
  "/hr/attendance": "page_attendance",
};

function getPageTitleKey(pathname: string): keyof ReturnType<typeof useT> | null {
  if (BREADCRUMB_KEYS[pathname]) return BREADCRUMB_KEYS[pathname];
  for (const [prefix, key] of Object.entries(BREADCRUMB_KEYS)) {
    if (pathname.startsWith(prefix + "/")) return key;
  }
  return null;
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
  const t = useT();

  const titleKey = getPageTitleKey(pathname);
  const pageTitle = titleKey ? t[titleKey] : "Ananas AI";

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
          title={t.toggle_theme}
          aria-label={t.toggle_theme}
        >
          {theme === "dark" ? (
            <Sun className="h-4 w-4" />
          ) : (
            <Moon className="h-4 w-4" />
          )}
        </button>

        {/* Notification bell */}
        <NotificationBell userEmail={userEmail ?? email ?? ""} />

        {/* Language switcher */}
        <LanguageSwitcher />

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
