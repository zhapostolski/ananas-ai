"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

let sessionId: string | null = null;
function getSessionId(): string {
  if (!sessionId) {
    sessionId = crypto.randomUUID();
  }
  return sessionId;
}

export function usePageTracking(title?: string) {
  const pathname = usePathname();
  const lastPath = useRef<string>("");

  useEffect(() => {
    if (pathname === lastPath.current) return;
    lastPath.current = pathname;

    fetch("/api/tracking/pageview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        page: pathname,
        title: title ?? document.title,
        session_id: getSessionId(),
      }),
    }).catch(() => {
      // Non-fatal
    });
  }, [pathname, title]);
}
