"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart2,
  Mail,
  Star,
  Settings,
  Users,
  ShoppingBag,
  DollarSign,
  Truck,
  LayoutDashboard,
  TrendingUp,
  Megaphone,
  ChevronDown,
  ChevronRight,
  Briefcase,
  HeartHandshake,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";
import type { Role } from "@/types";
import { canAccessDepartment } from "@/lib/roles";

interface NavGroup {
  id: string;
  label: string;
  icon: React.ReactNode;
  href: string;
  requiredDept?: string;
  children?: { label: string; href: string; icon: React.ReactNode }[];
}

const NAV: NavGroup[] = [
  {
    id: "marketing",
    label: "Marketing",
    icon: <Megaphone className="h-4 w-4" />,
    href: "/marketing",
    children: [
      { label: "Performance & Paid Media", href: "/marketing/performance", icon: <BarChart2 className="h-3.5 w-3.5" /> },
      { label: "CRM & Lifecycle", href: "/marketing/crm", icon: <Mail className="h-3.5 w-3.5" /> },
      { label: "Reputation", href: "/marketing/reputation", icon: <Star className="h-3.5 w-3.5" /> },
      { label: "Marketing Ops", href: "/marketing/ops", icon: <Settings className="h-3.5 w-3.5" /> },
      { label: "Influencers", href: "/marketing/influencers", icon: <Users className="h-3.5 w-3.5" /> },
      { label: "Cross-Channel Brief", href: "/marketing/brief", icon: <LayoutDashboard className="h-3.5 w-3.5" /> },
    ],
  },
  {
    id: "commercial",
    label: "Commercial",
    icon: <ShoppingBag className="h-4 w-4" />,
    href: "/commercial",
    children: [
      { label: "Category Growth", href: "/commercial/categories", icon: <TrendingUp className="h-3.5 w-3.5" /> },
      { label: "Supplier Intelligence", href: "/commercial/suppliers", icon: <Users className="h-3.5 w-3.5" /> },
      { label: "Product Feed", href: "/commercial/products", icon: <ShoppingBag className="h-3.5 w-3.5" /> },
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
];

interface SidebarProps {
  role: Role;
}

export function Sidebar({ role }: SidebarProps) {
  const pathname = usePathname();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    marketing: pathname.startsWith("/marketing"),
    commercial: pathname.startsWith("/commercial"),
  });

  const visibleGroups = NAV.filter((g) =>
    canAccessDepartment(role, g.id as Parameters<typeof canAccessDepartment>[1])
  );

  return (
    <aside className="flex h-full w-60 flex-col border-r bg-background">
      {/* Logo */}
      <div className="flex h-14 items-center border-b px-4">
        <Link href="/" className="flex items-center gap-2 font-bold text-lg text-primary">
          <span className="text-2xl">🍍</span>
          <span>Ananas AI</span>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-0.5">
        {visibleGroups.map((group) => {
          const isExpanded = expanded[group.id];
          const isActive = pathname.startsWith(group.href);

          return (
            <div key={group.id}>
              <button
                onClick={() =>
                  setExpanded((prev) => ({ ...prev, [group.id]: !prev[group.id] }))
                }
                className={cn(
                  "flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                {group.icon}
                <span className="flex-1 text-left">{group.label}</span>
                {group.children &&
                  (isExpanded ? (
                    <ChevronDown className="h-3.5 w-3.5" />
                  ) : (
                    <ChevronRight className="h-3.5 w-3.5" />
                  ))}
              </button>

              {group.children && isExpanded && (
                <div className="ml-4 mt-0.5 space-y-0.5">
                  {group.children.map((child) => (
                    <Link
                      key={child.href}
                      href={child.href}
                      className={cn(
                        "flex items-center gap-2 rounded-md px-3 py-1.5 text-xs transition-colors",
                        pathname === child.href
                          ? "bg-primary/10 text-primary font-medium"
                          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                      )}
                    >
                      {child.icon}
                      {child.label}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </nav>

      {/* Settings at bottom */}
      <div className="border-t p-2">
        <Link
          href="/settings"
          className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground"
        >
          <Settings className="h-4 w-4" />
          Settings
        </Link>
      </div>
    </aside>
  );
}
