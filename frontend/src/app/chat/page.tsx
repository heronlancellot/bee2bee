"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { MainLayout } from "@/components/main-layout";
import { ChatInterface } from "@/components/chat-interface";
import { RepoSelectorSidebar } from "@/components/repo-selector-sidebar";
import { Repository, ChatMessage } from "@/types";
import { supabase } from "@/integrations/supabase/client";
import { Loader2 } from "lucide-react";
import { useUserProfile, SelectedRepository } from "@/hooks/useUserProfile";
import { useRepositoryStore } from "@/store/repositories";

export default function ChatPage() {
  const router = useRouter();
  const { profile, loading: profileLoading } = useUserProfile();

  // Store state - only subscribe to what we need
  const repositories = useRepositoryStore((state) => state.repositories);
  const selectedRepos = useRepositoryStore((state) => state.selectedRepos);

  const [isAuthenticated, setIsAuthenticated] = React.useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = React.useState(true);
  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);

  // Load repositories from profile into the store (only once)
  React.useEffect(() => {
    // DEV BYPASS: Load mock repositories in development mode
    if (process.env.NEXT_PUBLIC_DEV_BYPASS_AUTH === 'true') {
      if (repositories.length > 0) return; // Already initialized
      const mockRepos: Repository[] = [
        {
          id: '1',
          name: 'bee2bee',
          full_name: 'heronlancellot/bee2bee',
          owner: 'heronlancellot',
          description: 'AI-powered developer matching platform',
          is_private: false,
          is_favorite: true,
          language: 'TypeScript',
          stars: 42,
          indexed_at: new Date().toISOString(),
          complexity_score: 75,
          agent_id: 'agent-1',
          branches: ['main', 'dev'],
          default_branch: 'main',
        },
        {
          id: '2',
          name: 'portfolio',
          full_name: 'heronlancellot/portfolio',
          owner: 'heronlancellot',
          description: 'Personal portfolio website',
          is_private: false,
          is_favorite: false,
          language: 'React',
          stars: 15,
          indexed_at: new Date().toISOString(),
          complexity_score: 45,
          agent_id: 'agent-2',
          branches: ['main'],
          default_branch: 'main',
        },
        {
          id: '3',
          name: 'api-server',
          full_name: 'heronlancellot/api-server',
          owner: 'heronlancellot',
          description: 'REST API backend service',
          is_private: true,
          is_favorite: false,
          language: 'Node.js',
          stars: 8,
          indexed_at: new Date().toISOString(),
          complexity_score: 60,
          agent_id: 'agent-3',
          branches: ['main', 'staging'],
          default_branch: 'main',
        },
      ];

      useRepositoryStore.getState().setRepositories(mockRepos);
      return;
    }

    // Production: load from profile
    if (!profile?.selected_repositories || repositories.length > 0) return;

    try {
      const selectedReposFromProfile =
        profile.selected_repositories as unknown as SelectedRepository[];

      const repos: Repository[] = selectedReposFromProfile.map((repo) => ({
        id: repo.id.toString(),
        name: repo.name,
        full_name: repo.full_name,
        owner: repo.owner,
        description: repo.description || null,
        is_private: false,
        is_favorite: false,
        language: repo.language || null,
        stars: repo.stars,
        indexed_at: new Date().toISOString(),
        complexity_score: 50,
        agent_id: `agent-${repo.id}`,
        branches: ["main"],
        default_branch: "main",
      }));

      useRepositoryStore.getState().setRepositories(repos);
    } catch (error) {
      console.error("Error loading repositories from profile:", error);
    }
  }, [profile, repositories.length]);

  React.useEffect(() => {
    const checkAuth = async () => {
      try {
        // DEV BYPASS: Skip authentication in development mode
        if (process.env.NEXT_PUBLIC_DEV_BYPASS_AUTH === "true") {
          console.log("Chat: 🔓 DEV MODE - Bypassing authentication");
          setIsAuthenticated(true);
          setIsCheckingAuth(false);
          return;
        }

        console.log("Chat: Checking authentication...");
        const {
          data: { session },
          error,
        } = await supabase.auth.getSession();

        if (error) {
          console.error("Chat: Auth error:", error);
          router.replace("/login");
          return;
        }

        console.log("Chat: Session:", session?.user?.email || "No session");

        if (!session?.user) {
          // User is not authenticated, redirect to login
          console.log("Chat: No user, redirecting to login");
          router.replace("/login");
        } else {
          console.log("Chat: User authenticated");
          setIsAuthenticated(true);
        }
      } catch (err) {
        console.error("Chat: Unexpected error:", err);
        router.replace("/login");
      } finally {
        setIsCheckingAuth(false);
      }
    };

    checkAuth();

    // Listen for auth state changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      // Skip auth listener in dev bypass mode
      if (process.env.NEXT_PUBLIC_DEV_BYPASS_AUTH === "true") return;

      console.log(
        "Chat: Auth state changed:",
        event,
        session?.user?.email || "No session",
      );
      if (!session?.user && event !== "INITIAL_SESSION") {
        router.replace("/login");
      } else if (session?.user) {
        setIsAuthenticated(true);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [router]);

  // Repository handlers - use stable callbacks
  const handleRepoToggle = React.useCallback((repoId: string) => {
    useRepositoryStore.getState().toggleSelection(repoId);
  }, []);

  const handleFavoriteToggle = React.useCallback((repoId: string) => {
    useRepositoryStore.getState().toggleFavorite(repoId);
  }, []);

  const handleDeselectAll = React.useCallback(() => {
    useRepositoryStore.getState().deselectAllRepositories();
  }, []);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call ASI-1 API via our Next.js API route
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: [...messages, userMessage].map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
          repository_ids: selectedRepos,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();

      // Add AI response
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.message,
        timestamp: new Date().toISOString(),
        // TODO: Add sources when agents return them
        // sources: data.sources || [],
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Error sending message:", error);

      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "Sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading state while checking authentication or loading profile
  if (isCheckingAuth || profileLoading) {
    return (
      <div className="flex min-h-svh flex-col items-center justify-center gap-6 bg-muted p-6">
        <Loader2
          className="h-12 w-12 animate-spin text-primary"
          aria-label="Loading"
        />
        <p className="text-sm text-muted-foreground">
          {isCheckingAuth
            ? "Checking authentication..."
            : "Loading your profile..."}
        </p>
      </div>
    );
  }

  // Only render the chat if authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <MainLayout>
      <div className="flex min-h-0 flex-1 overflow-hidden">
        {/* Main Chat Area */}
        <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
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
  );
}
