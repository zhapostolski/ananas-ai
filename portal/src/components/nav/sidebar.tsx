"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart2,
  Mail,
  Star,
  Settings,
  Users,
  DollarSign,
  Truck,
  LayoutDashboard,
  Megaphone,
  ChevronDown,
  ChevronRight,
  Briefcase,
  HeartHandshake,
  Shield,
  UserCircle,
  CalendarDays,
  MessageSquare,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState, useEffect } from "react";
import type { Role } from "@/types";
import { canAccessDepartment, canAccessMarketingModule, isAdminRole, canInvite, canSendNotifications } from "@/lib/roles";
import { UserAvatar } from "@/components/nav/user-menu";
import { useT } from "@/lib/i18n";

interface NavChild {
  labelKey: string;
  href: string;
  icon: React.ReactNode;
  module?: string;
}

interface NavGroup {
  id: string;
  labelKey: string;
  icon: React.ReactNode;
  href: string;
  requiredDept?: string;
  children?: NavChild[];
}

const NAV: NavGroup[] = [
  {
    id: "marketing",
    labelKey: "nav_marketing",
    icon: <Megaphone className="h-4 w-4" />,
    href: "/marketing/overview",
    children: [
      { labelKey: "nav_overview", href: "/marketing/overview", icon: <LayoutDashboard className="h-3.5 w-3.5" />, module: "overview" },
      { labelKey: "nav_performance", href: "/marketing/performance", icon: <BarChart2 className="h-3.5 w-3.5" />, module: "performance" },
      { labelKey: "nav_crm", href: "/marketing/crm", icon: <Mail className="h-3.5 w-3.5" />, module: "crm" },
      { labelKey: "nav_reputation", href: "/marketing/reputation", icon: <Star className="h-3.5 w-3.5" />, module: "reputation" },
      { labelKey: "nav_influencers", href: "/marketing/influencers", icon: <Users className="h-3.5 w-3.5" />, module: "influencers" },
      { labelKey: "nav_marketing_ops", href: "/marketing/ops", icon: <Settings className="h-3.5 w-3.5" />, module: "ops" },
    ],
  },
  {
    id: "finance",
    labelKey: "nav_finance",
    icon: <DollarSign className="h-4 w-4" />,
    href: "/finance",
  },
  {
    id: "logistics",
    labelKey: "nav_logistics",
    icon: <Truck className="h-4 w-4" />,
    href: "/logistics",
  },
  {
    id: "executive",
    labelKey: "nav_executive",
    icon: <Briefcase className="h-4 w-4" />,
    href: "/executive",
  },
  {
    id: "customer_experience",
    labelKey: "nav_customer_experience",
    icon: <HeartHandshake className="h-4 w-4" />,
    href: "/customer-experience",
    children: [
      { labelKey: "nav_reputation_reviews", href: "/customer-experience/reputation", icon: <Star className="h-3.5 w-3.5" /> },
      { labelKey: "nav_support_insights", href: "/customer-experience/support", icon: <Users className="h-3.5 w-3.5" /> },
    ],
  },
  {
    id: "hr",
    labelKey: "nav_hr",
    icon: <UserCircle className="h-4 w-4" />,
    href: "/hr",
    children: [
      { labelKey: "nav_team", href: "/hr/team", icon: <Users className="h-3.5 w-3.5" /> },
      { labelKey: "nav_attendance", href: "/hr/attendance", icon: <CalendarDays className="h-3.5 w-3.5" /> },
    ],
  },
];

interface SidebarProps {
  role: Role;
  userName?: string | null;
  userEmail?: string | null;
  avatarColor?: string;
  avatarUrl?: string | null;
  chatEnabled?: boolean;
  // Mobile overlay control
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({
  role,
  userName,
  userEmail,
  avatarColor = "#FE5000",
  avatarUrl,
  chatEnabled,
  isOpen = false,
  onClose,
}: SidebarProps) {
  const pathname = usePathname();
  const t = useT();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    marketing: pathname.startsWith("/marketing"),
    customer_experience: pathname.startsWith("/customer-experience"),
  });

  // Close sidebar on navigation (mobile)
  useEffect(() => {
    onClose?.();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  const isAdmin = isAdminRole(role);
  const showInvite = canInvite(role);
  const showSendNotif = canSendNotifications(role);

  const visibleGroups = NAV.filter((g) =>
    canAccessDepartment(role, g.id as Parameters<typeof canAccessDepartment>[1])
  );

  function filterChildren(group: NavGroup): NavChild[] {
    if (!group.children) return [];
    if (group.id !== "marketing") return group.children;
    return group.children.filter((c) =>
      !c.module || canAccessMarketingModule(role, c.module)
    );
  }

  return (
    <aside
      className={cn(
        // Base styles
        "flex h-full flex-col",
        // Desktop: always visible, static in flow
        "lg:relative lg:w-60 lg:translate-x-0 lg:flex",
        // Mobile/tablet: fixed overlay, controlled by isOpen
        "fixed inset-y-0 left-0 z-50 w-72 transition-transform duration-300 ease-in-out",
        isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}
      style={{ backgroundColor: "#111827" }}
    >
      {/* Logo row with close button on mobile */}
      <div className="flex h-14 items-center justify-between border-b px-4 shrink-0" style={{ borderBottomColor: "#1f2937" }}>
        <Link href="/marketing/overview" className="flex items-center gap-2">
          <img
            src="/ananas-logo.png"
            alt="ananas"
            width={100}
            height={38}
            style={{ objectFit: "contain" }}
          />
          <span className="text-xs font-semibold tracking-wide uppercase" style={{ color: "#FE5000" }}>
            AI
          </span>
        </Link>
        {/* Close button — only visible on mobile when open */}
        <button
          onClick={onClose}
          className="lg:hidden flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
          aria-label="Close navigation"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-0.5">
        {visibleGroups.map((group) => {
          const isExpanded = expanded[group.id];
          const isActive =
            pathname === group.href ||
            pathname.startsWith(group.href.split("/").slice(0, 2).join("/") + "/") ||
            (group.id === "marketing" && pathname.startsWith("/marketing"));
          const children = filterChildren(group);

          return (
            <div key={group.id}>
              <button
                onClick={() =>
                  setExpanded((prev) => ({ ...prev, [group.id]: !prev[group.id] }))
                }
                className={cn(
                  "flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "text-white"
                    : "text-gray-400 hover:text-white hover:bg-white/5"
                )}
                style={isActive && !group.children ? { backgroundColor: "#FE5000" } : {}}
              >
                {group.icon}
                <span className="flex-1 text-left">{t[group.labelKey as keyof typeof t] ?? group.labelKey}</span>
                {children.length > 0 &&
                  (isExpanded ? (
                    <ChevronDown className="h-3.5 w-3.5" />
                  ) : (
                    <ChevronRight className="h-3.5 w-3.5" />
                  ))}
              </button>

              {children.length > 0 && isExpanded && (
                <div className="ml-3 mt-0.5 space-y-0.5 border-l pl-3" style={{ borderColor: "#1f2937" }}>
                  {children.map((child) => {
                    const childActive =
                      pathname === child.href || pathname.startsWith(child.href + "/");
                    return (
                      <Link
                        key={child.href}
                        href={child.href}
                        className={cn(
                          "flex items-center gap-2 rounded-md px-3 py-1.5 text-xs transition-colors",
                          childActive
                            ? "font-semibold text-white"
                            : "text-gray-400 hover:text-white hover:bg-white/5"
                        )}
                        style={
                          childActive
                            ? { backgroundColor: "#FE5000", color: "white" }
                            : {}
                        }
                      >
                        {child.icon}
                        {t[child.labelKey as keyof typeof t] ?? child.labelKey}
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </nav>

      {/* Bottom: Admin + User */}
      <div className="border-t px-2 py-3 space-y-0.5 shrink-0" style={{ borderColor: "#1f2937" }}>
        {isAdmin && (
          <div>
            <Link
              href="/admin/users"
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                pathname.startsWith("/admin")
                  ? "text-white"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              )}
              style={pathname.startsWith("/admin") ? { backgroundColor: "#FE5000" } : {}}
            >
              <Shield className="h-4 w-4" />
              {t.nav_admin}
            </Link>
            {pathname.startsWith("/admin") && (
              <div className="ml-3 mt-0.5 space-y-0.5 border-l pl-3" style={{ borderColor: "#1f2937" }}>
                <Link
                  href="/admin/users"
                  className={cn(
                    "flex items-center gap-2 rounded-md px-3 py-1.5 text-xs transition-colors",
                    pathname === "/admin/users" || pathname.startsWith("/admin/users/")
                      ? "font-semibold text-white"
                      : "text-gray-400 hover:text-white hover:bg-white/5"
                  )}
                >
                  {t.nav_users}
                </Link>
                {showInvite && (
                  <Link
                    href="/admin/users/invite"
                    className={cn(
                      "flex items-center gap-2 rounded-md px-3 py-1.5 text-xs transition-colors",
                      pathname === "/admin/users/invite"
                        ? "font-semibold text-white"
                        : "text-gray-400 hover:text-white hover:bg-white/5"
                    )}
                  >
                    {t.nav_invite_user}
                  </Link>
                )}
                {showSendNotif && (
                  <Link
                    href="/admin/notifications"
                    className={cn(
                      "flex items-center gap-2 rounded-md px-3 py-1.5 text-xs transition-colors",
                      pathname === "/admin/notifications"
                        ? "font-semibold text-white"
                        : "text-gray-400 hover:text-white hover:bg-white/5"
                    )}
                  >
                    {t.nav_send_notification}
                  </Link>
                )}
              </div>
            )}
          </div>
        )}

        {chatEnabled && (
          <Link
            href="/chat"
            className={cn(
              "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
              pathname.startsWith("/chat")
                ? "text-white"
                : "text-gray-400 hover:text-white hover:bg-white/5"
            )}
            style={pathname.startsWith("/chat") ? { backgroundColor: "#FE5000" } : {}}
          >
            <MessageSquare className="h-4 w-4" />
            {t.nav_ai_chat}
          </Link>
        )}

        <Link
          href="/settings"
          className={cn(
            "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
            pathname === "/settings"
              ? "text-white"
              : "text-gray-400 hover:text-white hover:bg-white/5"
          )}
          style={pathname === "/settings" ? { backgroundColor: "#FE5000" } : {}}
        >
          <Settings className="h-4 w-4" />
          {t.nav_settings}
        </Link>

        {/* User avatar at bottom */}
        <Link
          href="/profile"
          className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
        >
          <UserAvatar
            name={userName}
            email={userEmail}
            avatarColor={avatarColor}
            avatarUrl={avatarUrl}
            size="sm"
          />
          <span className="truncate">{userName ?? userEmail ?? t.nav_profile}</span>
        </Link>
      </div>
    </aside>
  );
}
