"use client"

import * as React from "react"
import { Send, Loader2, Code2, FileText, ChevronDown, MessageSquare, Bot, Target, Search, Users, Sparkles, Zap, Paperclip, Mic, Command, ChevronRight, User, Copy, RotateCw, ThumbsUp, ThumbsDown } from "lucide-react"
import { Conversation, ConversationContent, ConversationScrollButton } from "@/components/ai/conversation"
import { Message, MessageContent, MessageAvatar } from "@/components/ai/message"
import { Response } from "@/components/ai/response"
import { ShimmeringText } from "@/components/ai/shimmering-text"
import { Loader } from "@/components/ai/loader"
import { Actions, Action } from "@/components/ai/actions"
import { ChatMessage, CodeSource } from "@/types"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface ChatInterfaceProps {
  messages: ChatMessage[]
  isLoading: boolean
  onSendMessage: (message: string) => void
  selectedReposCount: number
}

// Mock conversation history
const mockConversations = [
  { id: "1", title: "Authentication logic discussion", timestamp: "2 hours ago", preview: "Where is the authentication logic?" },
  { id: "2", title: "API endpoints overview", timestamp: "Yesterday", preview: "Explain how the API endpoints work" },
  { id: "3", title: "Database schema review", timestamp: "2 days ago", preview: "Show me the database schema" },
  { id: "4", title: "Security audit", timestamp: "1 week ago", preview: "Find security vulnerabilities" },
]

// Available commands
const availableCommands = [
  { command: "/analyze-repo", description: "Analyze repository complexity and tech stack", icon: Bot },
  { command: "/match-me", description: "Find issues matching your skills", icon: Target },
  { command: "/search", description: "Search across selected repositories", icon: Search },
  { command: "/team-solve", description: "Collaborate with multiple agents", icon: Users },
  { command: "/review", description: "Get AI code review for a PR", icon: Sparkles },
  { command: "/swarm", description: "Deploy agent swarm for complex problems", icon: Zap },
]

// Smart suggestions
const smartSuggestions = [
  "I want to analyze the complexity of this repository",
  "Help me find issues that match my skill level",
  "Search for authentication logic across repos",
  "How can I collaborate with agents to solve this?",
  "Review this pull request for security issues",
  "Explain how the payment flow works",
]

export function ChatInterface({
  messages,
  isLoading,
  onSendMessage,
  selectedReposCount,
}: ChatInterfaceProps) {
  const [input, setInput] = React.useState("")
  const [currentConversation, setCurrentConversation] = React.useState(mockConversations[0])
  const [showCommands, setShowCommands] = React.useState(false)
  const [filteredCommands, setFilteredCommands] = React.useState(availableCommands)
  const textareaRef = React.useRef<HTMLTextAreaElement>(null)
  const suggestionsRef = React.useRef<HTMLDivElement>(null)
  const [streamingText, setStreamingText] = React.useState("")
  const [isStreaming, setIsStreaming] = React.useState(false)

  // Check if chat is empty (no messages)
  const isEmpty = messages.length === 0

  // Simulate streaming effect for the last AI message
  React.useEffect(() => {
    const lastMessage = messages[messages.length - 1]
    if (lastMessage && lastMessage.role === 'assistant' && !isStreaming) {
      setIsStreaming(true)
      setStreamingText("")

      const fullText = lastMessage.content
      let currentIndex = 0

      const interval = setInterval(() => {
        if (currentIndex < fullText.length) {
          setStreamingText(fullText.substring(0, currentIndex + 1))
          currentIndex++
        } else {
          setIsStreaming(false)
          clearInterval(interval)
        }
      }, 20) // Velocidade do streaming (20ms por caractere)

      return () => clearInterval(interval)
    }
  }, [messages])

  const scrollSuggestions = () => {
    if (suggestionsRef.current) {
      suggestionsRef.current.scrollBy({ left: 200, behavior: 'smooth' })
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    setInput(value)

    // Check if user is typing a command
    const lastWord = value.split(/\s/).pop() || ""
    if (lastWord.startsWith("/")) {
      setShowCommands(true)
      const query = lastWord.slice(1).toLowerCase()
      const filtered = availableCommands.filter(cmd =>
        cmd.command.toLowerCase().includes(query) ||
        cmd.description.toLowerCase().includes(query)
      )
      setFilteredCommands(filtered)
    } else {
      setShowCommands(false)
    }
  }

  const selectCommand = (command: string) => {
    // Replace the last word (command) with the selected command
    const words = input.split(/\s/)
    words[words.length - 1] = command + " "
    setInput(words.join(" "))
    setShowCommands(false)
    textareaRef.current?.focus()
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading || selectedReposCount === 0) return

    onSendMessage(input)
    setInput("")
    setShowCommands(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
    if (e.key === "Escape") {
      setShowCommands(false)
    }
  }

  return (
    <div className="flex flex-1 flex-col relative overflow-hidden min-h-0">
      {/* Floating Conversation Selector */}
      <div className="absolute top-3 left-4 z-10">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="group h-6 flex items-center gap-1.5 px-2 rounded-md bg-background/80 backdrop-blur-sm border border-border/40 shadow-sm transition-all duration-300 hover:bg-background hover:border-primary/30 hover:shadow-[0_0_0_3px_hsl(var(--primary)/0.1)]">
              <span className="text-xs font-medium text-muted-foreground truncate max-w-[200px] transition-colors duration-300 group-hover:text-primary">
                {currentConversation.title}
              </span>
              <ChevronDown className="h-3 w-3 text-muted-foreground shrink-0 transition-all duration-300 group-hover:text-primary group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-[420px]">
            <DropdownMenuLabel className="text-[10px] uppercase tracking-wider text-muted-foreground/70">Recent Conversations</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {mockConversations.map((conv) => (
              <DropdownMenuItem
                key={conv.id}
                onClick={() => setCurrentConversation(conv)}
                className="flex flex-col items-start gap-0.5 py-2 px-2 cursor-pointer rounded-md"
              >
                <div className="flex items-center justify-between w-full gap-2">
                  <span className="text-xs font-medium truncate">{conv.title}</span>
                  <span className="text-[9px] text-muted-foreground/70 shrink-0">{conv.timestamp}</span>
                </div>
                <span className="text-[10px] text-muted-foreground/70 line-clamp-1 w-full">{conv.preview}</span>
              </DropdownMenuItem>
            ))}
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-xs text-primary cursor-pointer py-1.5 px-2 justify-center font-medium">
              Start new conversation
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Messages Area or Empty State with Centered Chat */}
      {isEmpty ? (
        <div className="flex-1 flex flex-col items-center justify-center p-6 transition-all duration-500 ease-in-out">
          <div className="max-w-2xl w-full transition-all duration-500 ease-in-out">
            {/* Empty State Content */}
            <div className="text-center space-y-8 mb-8 transition-all duration-500 ease-in-out animate-in fade-in slide-in-from-bottom-4">
              {/* Greeting */}
              <div className="space-y-3">
                <h1 className="text-3xl font-semibold text-foreground">
                  {getGreeting()}, Judha
                </h1>
                <h2 className="text-xl text-foreground">
                  How Can I <span className="text-primary">Assist You Today?</span>
                </h2>
              </div>

              {/* Helper Text */}
              {selectedReposCount === 0 && (
                <p className="text-sm text-muted-foreground">
                  Select repositories from the right sidebar to start chatting with AI
                </p>
              )}
            </div>

            {/* Floating Chat Input */}
            <div className="relative">
              {/* Smart Suggestions - Above Input */}
              {!input && selectedReposCount > 0 && (
                <div className="mb-3 overflow-visible">
                  <div className="flex items-center gap-2 overflow-visible">
                    <div
                      ref={suggestionsRef}
                      className="flex gap-2 overflow-x-auto scrollbar-none flex-1 overflow-y-visible py-1"
                      style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
                    >
                      {smartSuggestions.map((suggestion, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => {
                            setInput(suggestion)
                            textareaRef.current?.focus()
                          }}
                          className="shrink-0 px-3 py-1.5 rounded-full bg-muted/30 backdrop-blur-sm border border-border/30 text-xs font-medium text-muted-foreground transition-all duration-300 hover:bg-muted/50 hover:border-primary/20 hover:text-primary hover:shadow-[0_0_4px_hsl(var(--primary)/0.15)]"
                          style={{
                            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
                          }}
                        >
                          "{suggestion}"
                        </button>
                      ))}
                    </div>
                    <button
                      type="button"
                      onClick={scrollSuggestions}
                      className="shrink-0 h-7 w-7 rounded-full bg-muted/30 backdrop-blur-sm border border-border/30 flex items-center justify-center transition-all duration-300 hover:bg-muted/50 hover:border-primary/20 group"
                      style={{
                        boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
                      }}
                    >
                      <ChevronRight className="h-3 w-3 text-muted-foreground transition-all duration-300 group-hover:text-primary group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.3)]" />
                    </button>
                  </div>
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div className="relative">
                  {/* Command Palette */}
                  {showCommands && filteredCommands.length > 0 && (
                    <div className="absolute bottom-full left-0 right-0 mb-2 rounded-lg border bg-popover shadow-lg animate-in fade-in-0 zoom-in-95 slide-in-from-bottom-2">
                      <div className="p-2 max-h-[280px] overflow-y-auto">
                        <div className="text-[10px] uppercase tracking-wider text-muted-foreground/70 px-2 py-1 mb-1">
                          Available Commands
                        </div>
                        {filteredCommands.map((cmd) => {
                          const Icon = cmd.icon
                          return (
                            <button
                              key={cmd.command}
                              type="button"
                              onClick={() => selectCommand(cmd.command)}
                              className="w-full flex items-start gap-3 px-2 py-2 rounded-md hover:bg-muted/50 transition-colors duration-200 text-left group"
                            >
                              <div className="mt-0.5 shrink-0">
                                <Icon className="h-4 w-4 text-primary transition-all duration-300 group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-foreground">{cmd.command}</p>
                                <p className="text-xs text-muted-foreground line-clamp-1">{cmd.description}</p>
                              </div>
                            </button>
                          )
                        })}
                      </div>
                    </div>
                  )}

                  <div className="relative">
                    <Textarea
                      ref={textareaRef}
                      value={input}
                      onChange={handleInputChange}
                      onKeyDown={handleKeyDown}
                      placeholder={
                        selectedReposCount === 0
                          ? "Select repositories to start chatting..."
                          : "Ask anything about your code..."
                      }
                      disabled={isLoading || selectedReposCount === 0}
                      className="min-h-[100px] resize-none pr-2 pb-10"
                    />

                    {/* Action Badges - Inside Textarea */}
                    <div className="absolute bottom-2 left-2 right-2 flex items-center justify-between pointer-events-none">
                      <div className="flex items-center gap-1.5 pointer-events-auto">
                        {/* Attach Files/Repos */}
                        <button
                          type="button"
                          disabled={isLoading || selectedReposCount === 0}
                          className="group flex items-center gap-1 px-2 py-1 rounded-md bg-background hover:bg-muted text-muted-foreground hover:text-foreground transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_1px_3px_rgba(0,0,0,0.12)] dark:shadow-[0_1px_3px_rgba(0,0,0,0.3)]"
                          title="Attach file or repository"
                        >
                          <Paperclip className="h-3 w-3 dark:text-primary/60 group-hover:text-primary transition-colors duration-200" />
                          <span className="text-[11px] font-medium">Attach</span>
                        </button>

                        {/* Quick Commands */}
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <button
                              type="button"
                              disabled={isLoading || selectedReposCount === 0}
                              className="group flex items-center gap-1 px-2 py-1 rounded-md bg-background hover:bg-muted text-muted-foreground hover:text-foreground transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_1px_3px_rgba(0,0,0,0.12)] dark:shadow-[0_1px_3px_rgba(0,0,0,0.3)]"
                              title="Quick commands"
                            >
                              <Command className="h-3 w-3 dark:text-primary/60 group-hover:text-primary transition-colors duration-200" />
                              <span className="text-[11px] font-medium">Commands</span>
                            </button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent side="top" align="start" className="w-64">
                            <DropdownMenuLabel className="text-[10px] uppercase tracking-wider text-muted-foreground/70">Quick Commands</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            {availableCommands.slice(0, 4).map((cmd) => {
                              const Icon = cmd.icon
                              return (
                                <DropdownMenuItem
                                  key={cmd.command}
                                  onClick={() => {
                                    setInput(cmd.command + " ")
                                    textareaRef.current?.focus()
                                  }}
                                  className="flex items-center gap-2 cursor-pointer text-xs py-1.5"
                                >
                                  <Icon className="h-3 w-3 text-primary" />
                                  <span>{cmd.command}</span>
                                </DropdownMenuItem>
                              )
                            })}
                          </DropdownMenuContent>
                        </DropdownMenu>

                        {/* Voice Input */}
                        <button
                          type="button"
                          disabled={isLoading || selectedReposCount === 0}
                          className="group flex items-center gap-1 px-2 py-1 rounded-md bg-background hover:bg-muted text-muted-foreground hover:text-foreground transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_1px_3px_rgba(0,0,0,0.12)] dark:shadow-[0_1px_3px_rgba(0,0,0,0.3)]"
                          title="Voice input"
                        >
                          <Mic className="h-3 w-3 dark:text-primary/60 group-hover:text-primary transition-colors duration-200" />
                          <span className="text-[11px] font-medium">Voice</span>
                        </button>
                      </div>

                      {/* Send Button */}
                      <div className="pointer-events-auto">
                        <Button
                          type="submit"
                          size="icon"
                          disabled={!input.trim() || isLoading || selectedReposCount === 0}
                          className="h-7 w-7 rounded-md bg-primary hover:bg-primary/90 text-primary-foreground transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed shadow-[0_1px_3px_rgba(0,0,0,0.12)] dark:shadow-[0_1px_3px_rgba(0,0,0,0.3)]"
                          aria-label="Send message"
                        >
                          {isLoading ? (
                            <Loader2 className="h-3 w-3 animate-spin" />
                          ) : (
                            <Send className="h-3 w-3" />
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Messages Area with Auto-Scroll */}
          <Conversation className="flex-1 pt-12 transition-all duration-500 ease-in-out animate-in fade-in slide-in-from-top-4">
            <ConversationContent className="space-y-6">
              {messages.map((message, index) => {
                const isLastMessage = index === messages.length - 1
                const displayContent = (message.role === 'assistant' && isLastMessage && isStreaming)
                  ? streamingText
                  : message.content

                return (
                  <Message key={message.id} from={message.role}>
                    {message.role === 'assistant' && (
                      <MessageAvatar
                        src='/avatars/bot.jpg'
                        name='AI'
                      />
                    )}
                    <div className="flex flex-col max-w-[80%]">
                      <MessageContent className="relative">
                        {message.role === 'assistant' ? (
                          <Response className="text-sm">{displayContent}</Response>
                        ) : (
                          <p className="whitespace-pre-wrap">{message.content}</p>
                        )}

                        {/* Code Sources - só mostra quando terminar o streaming */}
                        {message.sources && message.sources.length > 0 && (!isLastMessage || !isStreaming) && (
                          <div className="space-y-2 pt-2 mt-2 border-t border-border/50">
                            <p className="text-xs font-medium opacity-70">Sources:</p>
                            <div className="space-y-2">
                              {message.sources.map((source, idx) => (
                                <CodeSourceCard key={idx} source={source} />
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Actions absolutamente posicionados no canto inferior direito do balão */}
                        {message.role === 'assistant' && (!isLastMessage || !isStreaming) && (
                          <Actions className="absolute -bottom-6 right-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                            <Action
                              tooltip="Copy message"
                              onClick={() => navigator.clipboard.writeText(message.content)}
                            >
                              <Copy size={12} />
                            </Action>
                            <Action
                              tooltip="Regenerate"
                              onClick={() => console.log('Regenerate')}
                            >
                              <RotateCw size={12} />
                            </Action>
                            <Action
                              tooltip="Good response"
                              onClick={() => console.log('Thumbs up')}
                            >
                              <ThumbsUp size={12} />
                            </Action>
                            <Action
                              tooltip="Bad response"
                              onClick={() => console.log('Thumbs down')}
                            >
                              <ThumbsDown size={12} />
                            </Action>
                          </Actions>
                        )}
                      </MessageContent>
                    </div>
                    {message.role === 'user' && (
                      <MessageAvatar
                        src='/avatars/user.jpg'
                        name='You'
                      />
                    )}
                  </Message>
                )
              })}
              {isLoading && <LoadingMessage />}
            </ConversationContent>
            <ConversationScrollButton />
          </Conversation>

          {/* Input Area - Bottom when messages exist */}
          <div className="border-t bg-background p-4 relative flex-shrink-0">
            <form onSubmit={handleSubmit}>
              <div className="relative">
                {/* Command Palette */}
                {showCommands && filteredCommands.length > 0 && (
                  <div className="absolute bottom-full left-0 right-0 mb-2 rounded-lg border bg-popover shadow-lg animate-in fade-in-0 zoom-in-95 slide-in-from-bottom-2">
                    <div className="p-2 max-h-[280px] overflow-y-auto">
                      <div className="text-[10px] uppercase tracking-wider text-muted-foreground/70 px-2 py-1 mb-1">
                        Available Commands
                      </div>
                      {filteredCommands.map((cmd) => {
                        const Icon = cmd.icon
                        return (
                          <button
                            key={cmd.command}
                            type="button"
                            onClick={() => selectCommand(cmd.command)}
                            className="w-full flex items-start gap-3 px-2 py-2 rounded-md hover:bg-muted/50 transition-colors duration-200 text-left group"
                          >
                            <div className="mt-0.5 shrink-0">
                              <Icon className="h-4 w-4 text-primary transition-all duration-300 group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-foreground">{cmd.command}</p>
                              <p className="text-xs text-muted-foreground line-clamp-1">{cmd.description}</p>
                            </div>
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )}

                <div className="relative">
                  <Textarea
                    ref={textareaRef}
                    value={input}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    placeholder={
                      selectedReposCount === 0
                        ? "Select repositories to start chatting..."
                        : "Ask anything about your code..."
                    }
                    disabled={isLoading || selectedReposCount === 0}
                    className="min-h-[100px] resize-none pr-2 pb-10"
                  />

                  {/* Action Badges - Inside Textarea */}
                  <div className="absolute bottom-2 left-2 right-2 flex items-center justify-between pointer-events-none">
                    <div className="flex items-center gap-1.5 pointer-events-auto">
                      {/* Attach Files/Repos */}
                      <button
                        type="button"
                        disabled={isLoading || selectedReposCount === 0}
                        className="group flex items-center gap-1 px-2 py-1 rounded-md bg-background hover:bg-muted text-muted-foreground hover:text-foreground transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_1px_3px_rgba(0,0,0,0.12)] dark:shadow-[0_1px_3px_rgba(0,0,0,0.3)]"
                        title="Attach file or repository"
                      >
                        <Paperclip className="h-3 w-3 dark:text-primary/60 group-hover:text-primary transition-colors duration-200" />
                        <span className="text-[11px] font-medium">Attach</span>
                      </button>

                      {/* Quick Commands */}
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <button
                            type="button"
                            disabled={isLoading || selectedReposCount === 0}
                            className="group flex items-center gap-1 px-2 py-1 rounded-md bg-background hover:bg-muted text-muted-foreground hover:text-foreground transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_1px_3px_rgba(0,0,0,0.12)] dark:shadow-[0_1px_3px_rgba(0,0,0,0.3)]"
                            title="Quick commands"
                          >
                            <Command className="h-3 w-3 dark:text-primary/60 group-hover:text-primary transition-colors duration-200" />
                            <span className="text-[11px] font-medium">Commands</span>
                          </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent side="top" align="start" className="w-64">
                          <DropdownMenuLabel className="text-[10px] uppercase tracking-wider text-muted-foreground/70">Quick Commands</DropdownMenuLabel>
                          <DropdownMenuSeparator />
                          {availableCommands.slice(0, 4).map((cmd) => {
                            const Icon = cmd.icon
                            return (
                              <DropdownMenuItem
                                key={cmd.command}
                                onClick={() => {
                                  setInput(cmd.command + " ")
                                  textareaRef.current?.focus()
                                }}
                                className="flex items-center gap-2 cursor-pointer text-xs py-1.5"
                              >
                                <Icon className="h-3 w-3 text-primary" />
                                <span>{cmd.command}</span>
                              </DropdownMenuItem>
                            )
                          })}
                        </DropdownMenuContent>
                      </DropdownMenu>

                      {/* Voice Input */}
                      <button
                        type="button"
                        disabled={isLoading || selectedReposCount === 0}
                        className="group flex items-center gap-1 px-2 py-1 rounded-md bg-background hover:bg-muted text-muted-foreground hover:text-foreground transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_1px_3px_rgba(0,0,0,0.12)] dark:shadow-[0_1px_3px_rgba(0,0,0,0.3)]"
                        title="Voice input"
                      >
                        <Mic className="h-3 w-3 dark:text-primary/60 group-hover:text-primary transition-colors duration-200" />
                        <span className="text-[11px] font-medium">Voice</span>
                      </button>
                    </div>

                    {/* Send/Stop Button */}
                    <div className="pointer-events-auto">
                      {(isStreaming || isLoading) ? (
                        <Button
                          type="button"
                          size="icon"
                          onClick={() => {
                            setIsStreaming(false)
                            console.log('Stop generation')
                          }}
                          className="h-7 w-7 rounded-md bg-primary hover:bg-primary/90 text-primary-foreground transition-all duration-200 shadow-[0_1px_3px_rgba(0,0,0,0.12)] dark:shadow-[0_1px_3px_rgba(0,0,0,0.3)]"
                          aria-label="Stop generating"
                        >
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                            <rect x="6" y="6" width="12" height="12" />
                          </svg>
                        </Button>
                      ) : (
                        <Button
                          type="submit"
                          size="icon"
                          disabled={!input.trim() || selectedReposCount === 0}
                          className="h-7 w-7 rounded-md bg-primary hover:bg-primary/90 text-primary-foreground transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed shadow-[0_1px_3px_rgba(0,0,0,0.12)] dark:shadow-[0_1px_3px_rgba(0,0,0,0.3)]"
                          aria-label="Send message"
                        >
                          <Send className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}


// Helper function to get greeting based on time
function getGreeting() {
  const hour = new Date().getHours()
  if (hour < 12) return "Good Morning"
  if (hour < 18) return "Good Afternoon"
  return "Good Evening"
}

// Quick action buttons
const quickActions = [
  { icon: Bot, label: "Analyze Repo" },
  { icon: Search, label: "Search Code" },
  { icon: Sparkles, label: "Review PR" },
]


function CodeSourceCard({ source }: { source: CodeSource }) {
  return (
    <Card className="bg-background/50">
      <CardHeader className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <Code2 className="h-4 w-4" />
            <div className="space-y-0.5">
              <p className="text-sm font-medium">{source.file_path}</p>
              <p className="text-xs text-muted-foreground">
                Lines {source.line_start}-{source.line_end} • {source.repository}
              </p>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-3 pt-0">
        <pre className="overflow-x-auto rounded-md bg-muted p-2 text-xs">
          <code>{source.content}</code>
        </pre>
      </CardContent>
    </Card>
  )
}

function LoadingMessage() {
  return (
    <div className="flex items-center gap-2 px-4">
      <Loader size={16} className="text-primary" />
      <ShimmeringText
        text="AI is thinking..."
        duration={1.2}
        wave={true}
        shimmeringColor="hsl(var(--primary))"
        color="hsl(var(--muted-foreground))"
        className="text-sm"
      />
    </div>
  )
}
