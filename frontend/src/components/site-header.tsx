"use client"

import { useTheme } from "next-themes"
import { Search, Inbox, Moon, Sun, Command, X, Settings } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { SidebarTrigger, useSidebar } from "@/components/ui/sidebar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useRef, useState, useEffect } from "react"
import { SettingsDialog } from "@/components/settings-dialog"

export function SiteHeader() {
  const { theme, resolvedTheme, setTheme } = useTheme()
  const { state } = useSidebar()
  const buttonRef = useRef<HTMLButtonElement>(null)
  const [searchValue, setSearchValue] = useState("")
  const [mounted, setMounted] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const currentTheme = mounted ? (resolvedTheme || theme) : 'light'
  const isCollapsed = state === 'collapsed'

  const logoSrc = currentTheme === 'dark'
    ? (isCollapsed ? '/branding/gradient_logo_icon.svg' : '/branding/gradient_logo_dark_theme_big.svg')
    : (isCollapsed ? '/branding/gradient_logo_icon.svg' : '/branding/gradient_logo_light_theme_big.svg')

  const handleThemeToggle = async () => {
    if (!buttonRef.current) return

    const targetTheme = theme === 'dark' ? 'light' : 'dark'

    // Check if View Transitions API is supported
    if (!(document as any).startViewTransition) {
      setTheme(targetTheme)
      return
    }

    // Get button position for the clip-path animation
    const rect = buttonRef.current.getBoundingClientRect()
    const x = rect.left + rect.width / 2
    const y = rect.top + rect.height / 2
    const endRadius = Math.hypot(
      Math.max(x, window.innerWidth - x),
      Math.max(y, window.innerHeight - y)
    ) * 2

    // Create the transition
    const transition = (document as any).startViewTransition(async () => {
      setTheme(targetTheme)
    })

    try {
      await transition.ready

      // Animate with clip-path from button center
      document.documentElement.animate(
        {
          clipPath: [
            `circle(0px at ${x}px ${y}px)`,
            `circle(${endRadius}px at ${x}px ${y}px)`
          ]
        },
        {
          duration: 800,
          easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
          pseudoElement: '::view-transition-new(root)'
        }
      )
    } catch (e) {
      // Fallback if transition fails
      console.log('Transition failed, falling back')
    }
  }

  return (
    <header className="flex h-12 items-center bg-background dark:bg-[hsl(var(--header-background))] shrink-0 border-b border-border/50 dark:border-transparent w-full relative z-50 dark:shadow-[0_1px_0_0_hsl(var(--primary)/0.15),0_1px_8px_-2px_hsl(var(--primary)/0.2)]">
      {/* Logo Section - Fixed width matching sidebar */}
      <div
        className={`flex items-center h-full border-r border-border/50 dark:border-transparent transition-all duration-200 ease-linear dark:shadow-[1px_0_0_0_hsl(var(--primary)/0.15),1px_0_8px_-2px_hsl(var(--primary)/0.2)] ${isCollapsed ? 'justify-center' : 'px-4'}`}
        style={{
          width: isCollapsed ? 'calc(var(--sidebar-width-icon) + 1rem)' : 'var(--sidebar-width)'
        }}
      >
        <img
          src={logoSrc}
          alt="Bee2Bee"
          className={`transition-all duration-200 ${isCollapsed ? 'size-10' : 'h-6 w-auto'}`}
        />
      </div>

      {/* Main Header Content */}
      <div className="flex items-center justify-between flex-1 h-full">
        {/* Left Section - Sidebar Toggle */}
        <div className="flex items-center px-3">
          <SidebarTrigger className="h-7 w-7 rounded-md transition-all duration-300 hover:bg-transparent [&>svg]:text-muted-foreground [&>svg]:dark:text-primary/60 [&>svg]:hover:text-primary [&>svg]:hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] [&>svg]:dark:hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)] [&>svg]:transition-all [&>svg]:duration-300" />
        </div>

        {/* Right Section - Search + Notifications + Theme */}
        <div className="flex items-center gap-1.5 px-3">
        {/* Search Bar */}
        <div className="relative group">
          <Search className="absolute left-2 top-1/2 h-3 w-3 -translate-y-1/2 text-muted-foreground/70 pointer-events-none transition-colors duration-300 group-focus-within:text-primary" />
          <Input
            type="text"
            placeholder="Search..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="h-7 w-[160px] pl-7 pr-12 text-xs rounded-md bg-muted/40 border-border/50 transition-all duration-300 focus:w-[240px] focus:bg-background focus:border-primary/30 focus:shadow-[0_0_0_3px_hsl(var(--primary)/0.1)] placeholder:text-muted-foreground/50 [&::-webkit-search-cancel-button]:hidden [&::-webkit-search-decoration]:hidden"
          />
          {searchValue ? (
            <button
              onClick={() => setSearchValue("")}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 inline-flex h-4 w-4 items-center justify-center rounded hover:bg-muted transition-colors duration-200"
            >
              <X className="h-2.5 w-2.5 text-muted-foreground hover:text-foreground" />
            </button>
          ) : (
            <kbd className="pointer-events-none absolute right-1.5 top-1/2 -translate-y-1/2 inline-flex h-4 select-none items-center gap-0.5 rounded border bg-background px-1 font-mono text-[9px] font-medium text-muted-foreground/70 shadow-sm">
              <Command className="h-2 w-2" />K
            </kbd>
          )}
        </div>

        {/* Notification Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="relative h-7 w-7 rounded-md transition-all duration-300 hover:bg-transparent group"
            >
              <Inbox className="h-3.5 w-3.5 text-muted-foreground dark:text-primary/60 transition-all duration-300 group-hover:text-primary group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]" />
              <span className="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-primary ring-1.5 ring-background shadow-[0_0_4px_hsl(var(--primary)/0.6)]" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-64">
            <DropdownMenuLabel className="text-xs">Notifications</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-xs py-2">
              <div className="flex flex-col gap-1">
                <p className="font-medium">New repository indexed</p>
                <p className="text-muted-foreground text-[10px]">nectar-frontend is ready</p>
              </div>
            </DropdownMenuItem>
            <DropdownMenuItem className="text-xs py-2">
              <div className="flex flex-col gap-1">
                <p className="font-medium">Agent completed task</p>
                <p className="text-muted-foreground text-[10px]">Code review finished</p>
              </div>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-xs justify-center text-primary">
              View all notifications
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Settings Button */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSettingsOpen(true)}
          className="h-7 w-7 rounded-md transition-all duration-300 hover:bg-transparent group"
        >
          <Settings className="h-3.5 w-3.5 text-muted-foreground dark:text-primary/60 transition-all duration-300 group-hover:text-primary group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]" />
        </Button>

        {/* Theme Toggle */}
        <Button
          ref={buttonRef}
          variant="ghost"
          size="icon"
          onClick={handleThemeToggle}
          className="h-7 w-7 rounded-md transition-all duration-300 hover:bg-transparent group relative overflow-hidden"
        >
          <div className="relative w-3.5 h-3.5">
            <Sun className="absolute inset-0 h-3.5 w-3.5 text-muted-foreground dark:text-primary/60 transition-all duration-500 group-hover:text-primary group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)] rotate-0 scale-100 dark:rotate-90 dark:scale-0" />
            <Moon className="absolute inset-0 h-3.5 w-3.5 text-muted-foreground dark:text-primary/60 transition-all duration-500 group-hover:text-primary group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)] rotate-90 scale-0 dark:rotate-0 dark:scale-100" />
          </div>
        </Button>
        </div>
      </div>

      <SettingsDialog open={settingsOpen} onOpenChange={setSettingsOpen} />
    </header>
  )
}
