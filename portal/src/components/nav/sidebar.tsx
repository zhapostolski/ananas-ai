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
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";
import type { Role } from "@/types";
import { canAccessDepartment, canAccessMarketingModule, isAdminRole, canInvite, canSendNotifications } from "@/lib/roles";
import { UserAvatar } from "@/components/nav/user-menu";

interface NavChild {
  label: string;
  href: string;
  icon: React.ReactNode;
  module?: string;
}

interface NavGroup {
  id: string;
  label: string;
  icon: React.ReactNode;
  href: string;
  requiredDept?: string;
  children?: NavChild[];
}

const NAV: NavGroup[] = [
  {
    id: "marketing",
    label: "Marketing",
    icon: <Megaphone className="h-4 w-4" />,
    href: "/marketing/overview",
    children: [
      { label: "Overview", href: "/marketing/overview", icon: <LayoutDashboard className="h-3.5 w-3.5" />, module: "overview" },
      { label: "Performance", href: "/marketing/performance", icon: <BarChart2 className="h-3.5 w-3.5" />, module: "performance" },
      { label: "CRM & Lifecycle", href: "/marketing/crm", icon: <Mail className="h-3.5 w-3.5" />, module: "crm" },
      { label: "Reputation", href: "/marketing/reputation", icon: <Star className="h-3.5 w-3.5" />, module: "reputation" },
      { label: "Influencers", href: "/marketing/influencers", icon: <Users className="h-3.5 w-3.5" />, module: "influencers" },
      { label: "Marketing Ops", href: "/marketing/ops", icon: <Settings className="h-3.5 w-3.5" />, module: "ops" },
    ],
  },
  {
    id: "finance",
    label: "Finance",
    icon: <DollarSign className="h-4 w-4" />,
    href: "/finance",
  },
  {
    id: "logistics",
    label: "Logistics",
    icon: <Truck className="h-4 w-4" />,
    href: "/logistics",
  },
  {
    id: "executive",
    label: "Executive",
    icon: <Briefcase className="h-4 w-4" />,
    href: "/executive",
  },
  {
    id: "customer_experience",
    label: "Customer Experience",
    icon: <HeartHandshake className="h-4 w-4" />,
    href: "/customer-experience",
    children: [
      { label: "Reputation & Reviews", href: "/customer-experience/reputation", icon: <Star className="h-3.5 w-3.5" /> },
      { label: "Support Insights", href: "/customer-experience/support", icon: <Users className="h-3.5 w-3.5" /> },
    ],
  },
  {
    id: "hr",
    label: "HR",
    icon: <UserCircle className="h-4 w-4" />,
    href: "/hr",
    children: [
      { label: "Team", href: "/hr/team", icon: <Users className="h-3.5 w-3.5" /> },
      { label: "Attendance", href: "/hr/attendance", icon: <CalendarDays className="h-3.5 w-3.5" /> },
    ],
  },
];

interface SidebarProps {
  role: Role;
  userName?: string | null;
  userEmail?: string | null;
  avatarColor?: string;
  avatarUrl?: string | null;
}

export function Sidebar({ role, userName, userEmail, avatarColor = "#FE5000", avatarUrl }: SidebarProps) {
  const pathname = usePathname();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    marketing: pathname.startsWith("/marketing"),
    customer_experience: pathname.startsWith("/customer-experience"),
  });

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
    <aside className="flex h-full w-60 flex-col" style={{ backgroundColor: "#111827" }}>
      {/* Logo */}
      <div className="flex h-14 items-center border-b px-4" style={{ borderBottomColor: "#1f2937" }}>
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
                <span className="flex-1 text-left">{group.label}</span>
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
                        {child.label}
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
      <div className="border-t px-2 py-3 space-y-0.5" style={{ borderColor: "#1f2937" }}>
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
              Admin
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
                  Users
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
                    Invite User
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
                    Send Notification
                  </Link>
                )}
              </div>
            )}
          </div>
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
          Settings
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
          <span className="truncate">{userName ?? userEmail ?? "Profile"}</span>
        </Link>
      </div>
    </aside>
  );
}
