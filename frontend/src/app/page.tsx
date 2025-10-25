"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { supabase } from "@/integrations/supabase/client"
import { Loader2 } from "lucide-react"

export default function Page() {
  const router = useRouter()
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        console.log("Root: Checking authentication...")
        const { data: { session }, error } = await supabase.auth.getSession()

        if (error) {
          console.error("Root: Auth error:", error)
          router.replace("/login")
          return
        }

        console.log("Root: Session:", session?.user?.email || "No session")

        if (session?.user) {
          // User is authenticated, redirect to chat
          router.replace("/chat")
        } else {
          // User is not authenticated, redirect to login
          router.replace("/login")
        }
      } catch (err) {
        console.error("Root: Unexpected error:", err)
        router.replace("/login")
      } finally {
        setChecking(false)
      }
    }

    checkAuth()
  }, [router])

  // Show loading state while checking auth
  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-6 bg-muted p-6">
      <Loader2 className="h-12 w-12 animate-spin text-primary" aria-label="Loading" />
      <p className="text-sm text-muted-foreground">
        {checking ? "Checking authentication..." : "Redirecting..."}
      </p>
    </div>
  )
}
