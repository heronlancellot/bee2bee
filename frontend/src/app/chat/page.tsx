"use client"

import * as React from "react"
import { MainLayout } from "@/components/main-layout"
import { ChatInterface } from "@/components/chat-interface"
import { RepoSelectorSidebar } from "@/components/repo-selector-sidebar"
import { Repository, ChatMessage } from "@/types"

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
  const [repositories] = React.useState<Repository[]>(mockRepositories)
  const [selectedRepos, setSelectedRepos] = React.useState<string[]>(
    mockRepositories.map((repo) => repo.id)
  )
  const [messages, setMessages] = React.useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = React.useState(false)

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
      // TODO: Replace with real API call
      // const response = await fetch('/api/chat', {
      //   method: 'POST',
      //   body: JSON.stringify({
      //     message: content,
      //     repository_ids: selectedRepos,
      //   }),
      // })

      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 2000))

      // Mock AI response with rich markdown
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `I found the **authentication logic** in your codebase. Here's what I discovered:

## Overview
The authentication system uses JWT tokens for user verification. Here are the key components:

### Main Features
- Token validation with \`jwt.verify()\`
- Environment-based secret key management
- Error handling for invalid tokens

### Implementation Details
\`\`\`typescript
export async function authenticateUser(token: string) {
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    return decoded
  } catch (error) {
    throw new Error('Invalid token')
  }
}
\`\`\`

### Security Considerations
1. **Secret Management**: Uses environment variables
2. **Token Expiration**: Automatically handled by JWT
3. **Error Handling**: Graceful failure on invalid tokens

> **Note:** Make sure to rotate your JWT_SECRET regularly for better security.`,
        timestamp: new Date().toISOString(),
        sources: [
          {
            file_path: "src/auth/index.ts",
            line_start: 45,
            line_end: 120,
            repository: "nectar-frontend",
            content: `export async function authenticateUser(token: string) {
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    return decoded
  } catch (error) {
    throw new Error('Invalid token')
  }
}`,
          },
        ],
      }

      setMessages((prev) => [...prev, aiMessage])
    } catch (error) {
      console.error("Error sending message:", error)
      // TODO: Show error toast
    } finally {
      setIsLoading(false)
    }
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
