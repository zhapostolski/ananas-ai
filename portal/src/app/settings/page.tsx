import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Sidebar } from "@/components/nav/sidebar";
import { Header } from "@/components/nav/header";
import { Badge } from "@/components/ui/badge";
import { ROLE_LABELS } from "@/lib/roles";
import type { Role } from "@/types";

export default async function SettingsPage() {
  const session = await auth();
  if (!session?.user) redirect("/login");

  const role = ((session.user as { role?: Role }).role ?? "performance_marketer") as Role;

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar role={role} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header name={session.user.name} email={session.user.email} role={role} />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-lg space-y-6">
            <div>
              <h1 className="text-2xl font-bold">Settings</h1>
              <p className="text-sm text-muted-foreground">Account and platform settings</p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Your Account</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Name</span>
                  <span className="text-sm font-medium">{session.user.name}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Email</span>
                  <span className="text-sm font-medium">{session.user.email}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Role</span>
                  <Badge variant="outline">{ROLE_LABELS[role]}</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
