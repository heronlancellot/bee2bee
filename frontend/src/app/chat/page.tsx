"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { MainLayout } from "@/components/main-layout"
import { ChatInterface } from "@/components/chat-interface"
import { RepoSelectorSidebar } from "@/components/repo-selector-sidebar"
import { Repository, ChatMessage } from "@/types"
import { supabase } from "@/integrations/supabase/client"
import { Loader2 } from "lucide-react"
import { useUserProfile, SelectedRepository } from "@/hooks/useUserProfile"

export default function ChatPage() {
  const router = useRouter()
  const { profile, loading: profileLoading } = useUserProfile()
  const [isAuthenticated, setIsAuthenticated] = React.useState(false)
  const [isCheckingAuth, setIsCheckingAuth] = React.useState(true)
  const [repositories, setRepositories] = React.useState<Repository[]>([])
  const [selectedRepos, setSelectedRepos] = React.useState<string[]>([])
  const [messages, setMessages] = React.useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = React.useState(false)

  // Load repositories from profile
  React.useEffect(() => {
    if (profile && profile.selected_repositories) {
      try {
        const selectedRepos = profile.selected_repositories as unknown as SelectedRepository[];

        // Convert selected repositories to Repository format
        const repos: Repository[] = selectedRepos.map((repo) => ({
          id: repo.id.toString(),
          name: repo.name,
          full_name: repo.full_name,
          owner: repo.owner,
          description: repo.description || "No description",
          is_private: false,
          is_favorite: false,
          language: repo.language || "Unknown",
          stars: repo.stars,
          indexed_at: new Date().toISOString(),
          complexity_score: 50,
          agent_id: `agent-${repo.id}`,
          branches: ["main"],
          default_branch: "main",
        }));

        setRepositories(repos);
        // Select all repos by default
        setSelectedRepos(repos.map(r => r.id));
      } catch (error) {
        console.error("Error loading repositories from profile:", error);
      }
    }
  }, [profile]);

  React.useEffect(() => {
    const checkAuth = async () => {
      try {
        console.log("Chat: Checking authentication...")
        const { data: { session }, error } = await supabase.auth.getSession()

        if (error) {
          console.error("Chat: Auth error:", error)
          router.replace("/login")
          return
        }

        console.log("Chat: Session:", session?.user?.email || "No session")

        if (!session?.user) {
          // User is not authenticated, redirect to login
          console.log("Chat: No user, redirecting to login")
          router.replace("/login")
        } else {
          console.log("Chat: User authenticated")
          setIsAuthenticated(true)
        }
      } catch (err) {
        console.error("Chat: Unexpected error:", err)
        router.replace("/login")
      } finally {
        setIsCheckingAuth(false)
      }
    }

    checkAuth()

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      console.log("Chat: Auth state changed:", event, session?.user?.email || "No session")
      if (!session?.user && event !== 'INITIAL_SESSION') {
        router.replace("/login")
      } else if (session?.user) {
        setIsAuthenticated(true)
      }
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [router])

  const handleRepoToggle = (repoId: string) => {
    setSelectedRepos((prev) =>
      prev.includes(repoId)
        ? prev.filter((id) => id !== repoId)
        : [...prev, repoId]
    )
  }

  const handleFavoriteToggle = (repoId: string) => {
    // TODO: API call to update favorite status
    console.log("Toggle favorite:", repoId)
  }

  const handleDeselectAll = () => {
    setSelectedRepos([])
  }

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Call ASI-1 API via our Next.js API route
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage].map(msg => ({
            role: msg.role,
            content: msg.content
          })),
          repository_ids: selectedRepos,
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()

      // Add AI response
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.message,
        timestamp: new Date().toISOString(),
        // TODO: Add sources when agents return them
        // sources: data.sources || [],
      }

      setMessages((prev) => [...prev, aiMessage])
    } catch (error) {
      console.error("Error sending message:", error)

      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // Show loading state while checking authentication or loading profile
  if (isCheckingAuth || profileLoading) {
    return (
      <div className="flex min-h-svh flex-col items-center justify-center gap-6 bg-muted p-6">
        <Loader2 className="h-12 w-12 animate-spin text-primary" aria-label="Loading" />
        <p className="text-sm text-muted-foreground">
          {isCheckingAuth ? "Checking authentication..." : "Loading your profile..."}
        </p>
      </div>
    )
  }

  // Only render the chat if authenticated
  if (!isAuthenticated) {
    return null
  }

  return (
    <MainLayout>
      <div className="flex flex-1 overflow-hidden min-h-0">
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col overflow-hidden min-h-0">
          <ChatInterface
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            selectedReposCount={selectedRepos.length}
          />
        </div>

        {/* Repository Selector Sidebar */}
        <div className="w-80 overflow-y-auto">
          <RepoSelectorSidebar
            repositories={repositories}
            selectedRepos={selectedRepos}
            onRepoToggle={handleRepoToggle}
            onFavoriteToggle={handleFavoriteToggle}
            onDeselectAll={handleDeselectAll}
          />
        </div>
      </div>
    </MainLayout>
  )
}
