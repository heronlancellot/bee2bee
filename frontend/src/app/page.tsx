"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { supabase } from "@/integrations/supabase/client"
import { Loader2 } from "lucide-react"

export default function Page() {
  const router = useRouter()

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession()

      if (session?.user) {
        // User is authenticated, redirect to chat
        router.push("/chat")
      } else {
        // User is not authenticated, redirect to login
        router.push("/login")
      }
    }

    checkAuth()
  }, [router])

  // Show loading state while checking auth
  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-6 bg-muted p-6">
      <Loader2 className="h-12 w-12 animate-spin text-primary" aria-label="Loading" />
      <p className="text-sm text-muted-foreground">Loading...</p>
    </div>
  )
}
