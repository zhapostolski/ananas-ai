"use client";

import Link from "next/link";
import { MessageSquare } from "lucide-react";
import { usePathname } from "next/navigation";

interface ChatButtonProps {
  chatEnabled: boolean;
}

export function FloatingChatButton({ chatEnabled }: ChatButtonProps) {
  const pathname = usePathname();

  if (!chatEnabled || pathname.startsWith("/chat")) return null;

  return (
    <Link
      href="/chat"
      className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full shadow-lg text-white transition-transform hover:scale-105 active:scale-95"
      style={{ backgroundColor: "#FE5000" }}
      title="Open AI Chat"
    >
      <MessageSquare className="h-6 w-6" />
    </Link>
  );
}
