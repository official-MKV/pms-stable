'use client'

import { SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/dashboard/app-sidebar"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { AuthGuard } from "@/lib/auth-context"
import { useRouter } from "next/navigation"

export default function DashboardLayout({ children }) {
  const router = useRouter()

  return (
    <AuthGuard
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center space-y-4">
            <h1 className="text-2xl font-bold">Authentication Required</h1>
            <p className="text-muted-foreground">Please log in to access the dashboard.</p>
            <button
              onClick={() => router.push('/login')}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Go to Login
            </button>
          </div>
        </div>
      }
    >
      <SidebarProvider>
        <div className="flex min-h-screen w-full">
          <AppSidebar />
          <div className="flex-1 flex flex-col">
            <DashboardHeader />
            <main className="flex-1 p-6 bg-gray-50/50">
              {children}
            </main>
          </div>
        </div>
      </SidebarProvider>
    </AuthGuard>
  )
}