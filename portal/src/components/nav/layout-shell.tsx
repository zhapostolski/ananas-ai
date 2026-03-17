"use client";

import { useState, useEffect } from "react";
import { Sidebar } from "@/components/nav/sidebar";
import { Header } from "@/components/nav/header";
import { FloatingChatButton } from "@/components/nav/chat-button";
import { PageTracker } from "@/components/page-tracker";
import type { Role } from "@/types";

interface LayoutShellProps {
  children: React.ReactNode;
  role: Role;
  userName?: string | null;
  userEmail?: string | null;
  avatarColor?: string;
  avatarUrl?: string | null;
  chatEnabled?: boolean;
  showPageTracker?: boolean;
  showFloatingChat?: boolean;
  /** Override the main content area class (e.g. for chat which needs no padding) */
  mainClassName?: string;
}

export function LayoutShell({
  children,
  role,
  userName,
  userEmail,
  avatarColor = "#FE5000",
  avatarUrl,
  chatEnabled,
  showPageTracker = true,
  showFloatingChat = true,
  mainClassName = "flex-1 overflow-y-auto p-4 md:p-6",
}: LayoutShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Close sidebar on route change (navigation)
  useEffect(() => {
    setSidebarOpen(false);
  }, []);

  // Close sidebar on Escape key
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setSidebarOpen(false);
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  // Prevent body scroll when mobile sidebar is open
  useEffect(() => {
    if (sidebarOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [sidebarOpen]);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <Sidebar
        role={role}
        userName={userName}
        userEmail={userEmail}
        avatarColor={avatarColor}
        avatarUrl={avatarUrl}
        chatEnabled={chatEnabled}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex flex-1 flex-col overflow-hidden min-w-0">
        <Header
          name={userName}
          email={userEmail}
          role={role}
          avatarColor={avatarColor}
          avatarUrl={avatarUrl}
          userEmail={userEmail ?? undefined}
          onMenuToggle={() => setSidebarOpen((v) => !v)}
        />
        {showPageTracker && <PageTracker />}
        <main className={mainClassName}>
          {children}
        </main>
      </div>

      {showFloatingChat && (
        <FloatingChatButton chatEnabled={!!chatEnabled} />
      )}
    </div>
  );
}
