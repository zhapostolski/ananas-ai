import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { LayoutShell } from "@/components/nav/layout-shell";
import { getPortalUser } from "@/lib/db-portal";
import type { Role } from "@/types";

export default async function ChatLayout({ children }: { children: React.ReactNode }) {
  const session = await auth();
  if (!session?.user) redirect("/login");

  const email = (session.user as { email?: string })?.email;
  const portalUser = email ? getPortalUser(email) : undefined;

  if (!portalUser?.chat_enabled) {
    redirect("/marketing/overview");
  }

  const role = ((session.user as { role?: Role }).role ?? "performance_marketer") as Role;
  const avatarColor = portalUser.avatar_color ?? "#FE5000";
  const avatarUrl = portalUser.avatar_url ?? null;

  return (
    <LayoutShell
      role={role}
      userName={session.user.name}
      userEmail={session.user.email}
      avatarColor={avatarColor}
      avatarUrl={avatarUrl}
      chatEnabled={true}
      showPageTracker={false}
      showFloatingChat={false}
      mainClassName="flex flex-1 overflow-hidden"
    >
      {children}
    </LayoutShell>
  );
}
