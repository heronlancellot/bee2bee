"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { MainLayout } from "@/components/main-layout"
import { ChatInterface } from "@/components/chat-interface"
import { RepoSelectorSidebar } from "@/components/repo-selector-sidebar"
import { Repository, ChatMessage } from "@/types"
import { supabase } from "@/integrations/supabase/client"
import { Loader2 } from "lucide-react"

// Mock data - replace with real API calls
const mockRepositories: Repository[] = [
  {
    id: "1",
    name: "nectar-frontend",
    full_name: "nectardao/nectar-frontend",
    owner: "nectardao",
    description: "Next.js frontend for NectarDAO",
    is_private: false,
    is_favorite: true,
    language: "TypeScript",
    stars: 42,
    indexed_at: new Date().toISOString(),
    complexity_score: 65,
    agent_id: "agent-1",
    branches: ["main", "develop", "feature/chat-ui"],
    default_branch: "main",
  },
  {
    id: "2",
    name: "nectar-agents",
    full_name: "nectardao/nectar-agents",
    owner: "nectardao",
    description: "Fetch.ai agents for NectarDAO",
    is_private: true,
    is_favorite: true,
    language: "Python",
    stars: 28,
    indexed_at: new Date().toISOString(),
    complexity_score: 78,
    agent_id: "agent-2",
    branches: ["main", "develop"],
    default_branch: "main",
  },
  {
    id: "3",
    name: "nectar-backend",
    full_name: "nectardao/nectar-backend",
    owner: "nectardao",
    description: "n8n workflows and API",
    is_private: true,
    is_favorite: false,
    language: "JavaScript",
    stars: 15,
    indexed_at: new Date().toISOString(),
    complexity_score: 52,
    agent_id: "agent-3",
    branches: ["main", "staging", "develop"],
    default_branch: "main",
  },
  {
    id: "4",
    name: "awesome-project",
    full_name: "someuser/awesome-project",
    owner: "someuser",
    description: "An awesome open source project",
    is_private: false,
    is_favorite: false,
    language: "Go",
    stars: 1240,
    indexed_at: new Date().toISOString(),
    complexity_score: 84,
    agent_id: "agent-4",
    branches: ["main", "v2", "experimental"],
    default_branch: "main",
  },
]

export default function ChatPage() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = React.useState(false)
  const [isCheckingAuth, setIsCheckingAuth] = React.useState(true)
  const [repositories] = React.useState<Repository[]>(mockRepositories)
  const [selectedRepos, setSelectedRepos] = React.useState<string[]>(
    mockRepositories.map((repo) => repo.id)
  )
  const [messages, setMessages] = React.useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = React.useState(false)

  React.useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession()

      if (!session?.user) {
        // User is not authenticated, redirect to login
        router.push("/login")
      } else {
        setIsAuthenticated(true)
      }
      setIsCheckingAuth(false)
    }

    checkAuth()

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (!session?.user) {
        router.push("/login")
      } else {
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

  // Show loading state while checking authentication
  if (isCheckingAuth) {
    return (
      <div className="flex min-h-svh flex-col items-center justify-center gap-6 bg-muted p-6">
        <Loader2 className="h-12 w-12 animate-spin text-primary" aria-label="Loading" />
        <p className="text-sm text-muted-foreground">Checking authentication...</p>
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
