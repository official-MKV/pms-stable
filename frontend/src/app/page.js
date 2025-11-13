'use client'

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "../lib/auth-context"
import { Loader2, Building2 } from "lucide-react"

export default function Home() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading) {
      if (user) {
        router.push('/dashboard')
      } else {
        router.push('/login')
      }
    }
  }, [user, loading, router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center space-y-4">
        <div className="flex justify-center mb-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Building2 className="h-8 w-8" />
          </div>
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">
          Nigcomsat PMS
        </h1>
        <p className="text-muted-foreground">
          Performance Management System
        </p>
        <div className="flex items-center justify-center pt-4">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
          <span className="ml-2 text-sm text-muted-foreground">Loading...</span>
        </div>
      </div>
    </div>
  )
}
