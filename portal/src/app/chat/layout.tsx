import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { Sidebar } from "@/components/nav/sidebar";
import { Header } from "@/components/nav/header";
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
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar
        role={role}
        userName={session.user.name}
        userEmail={session.user.email}
        avatarColor={avatarColor}
        avatarUrl={avatarUrl}
      />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header
          name={session.user.name}
          email={session.user.email}
          userEmail={session.user.email ?? undefined}
          role={role}
          avatarColor={avatarColor}
          avatarUrl={avatarUrl}
        />
        {children}
      </div>
    </div>
  );
}
