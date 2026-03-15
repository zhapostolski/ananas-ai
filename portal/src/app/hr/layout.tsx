import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { Sidebar } from "@/components/nav/sidebar";
import { Header } from "@/components/nav/header";
import type { Role } from "@/types";
import { canAccessDepartment } from "@/lib/roles";
import { getPortalUser } from "@/lib/db-portal";
import { PageTracker } from "@/components/page-tracker";

export default async function HrLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();
  if (!session?.user) redirect("/login");

  const role = ((session.user as { role?: Role }).role ?? "performance_marketer") as Role;

  if (!canAccessDepartment(role, "hr")) {
    redirect("/marketing/overview");
  }

  const portalUser = session.user.email ? getPortalUser(session.user.email) : undefined;
  const avatarColor = portalUser?.avatar_color ?? "#FE5000";
  const avatarUrl = portalUser?.avatar_url ?? null;

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
        <PageTracker />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
