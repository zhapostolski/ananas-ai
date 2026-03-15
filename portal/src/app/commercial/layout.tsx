import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { Sidebar } from "@/components/nav/sidebar";
import { Header } from "@/components/nav/header";
import type { Role } from "@/types";
import { canAccessDepartment } from "@/lib/roles";

export default async function CommercialLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();
  if (!session?.user) redirect("/login");

  const role = ((session.user as { role?: Role }).role ?? "commercial_3p") as Role;

  if (!canAccessDepartment(role, "commercial")) {
    redirect("/marketing");
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar role={role} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header name={session.user.name} email={session.user.email} role={role} />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
