import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { LayoutShell } from "@/components/nav/layout-shell";
import type { Role } from "@/types";
import { getPortalUser } from "@/lib/db-portal";

export default async function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();
  if (!session?.user) redirect("/login");

  const role = ((session.user as { role?: Role }).role ?? "performance_marketer") as Role;
  const portalUser = session.user.email ? getPortalUser(session.user.email) : undefined;
  const avatarColor = portalUser?.avatar_color ?? "#FE5000";
  const avatarUrl = portalUser?.avatar_url ?? null;

  return (
    <LayoutShell
      role={role}
      userName={session.user.name}
      userEmail={session.user.email}
      avatarColor={avatarColor}
      avatarUrl={avatarUrl}
      chatEnabled={!!(portalUser?.chat_enabled)}
    >
      {children}
    </LayoutShell>
  );
}
