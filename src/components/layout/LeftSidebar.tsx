"use client"

import * as React from "react"
import { useTheme } from "next-themes"
import {
  Home,
  Target,
  Briefcase,
  Package,
  User,
  Settings,
  Brain,
  HelpCircle,
  BookOpen,
  Moon,
  Sun,
  Plus,
  Star,
  Circle,
} from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { cn } from "@/lib/utils"

type NavItem = {
  title: string
  icon: React.ComponentType<{ className?: string }>
  href: string
  active?: boolean
}

type Repository = {
  name: string
  stars: string
  online: boolean
  selected?: boolean
}

const navItems: NavItem[] = [
  { title: "Dashboard", icon: Home, href: "/", active: true },
  { title: "My Feed", icon: Target, href: "/feed" },
  { title: "My Bounties", icon: Briefcase, href: "/bounties" },
  { title: "Repositories", icon: Package, href: "/repositories" },
  { title: "Profile", icon: User, href: "/profile" },
  { title: "Settings", icon: Settings, href: "/settings" },
]

const mockRepos: Repository[] = [
  { name: "awesome-api", stars: "2.3k", online: true, selected: true },
  { name: "react-dashboard", stars: "890", online: true, selected: false },
  { name: "cli-tool", stars: "450", online: false, selected: true },
]

export function LeftSidebar() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <Sidebar>
      {/* HEADER */}
      <SidebarHeader className="border-b">
        <div className="flex items-center gap-2 px-2 py-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Brain className="h-5 w-5" />
          </div>
          <div className="flex items-center gap-2">
            <span className="font-serif text-lg font-semibold">RepoMind</span>
            <Badge variant="secondary" className="text-xs">
              Beta
            </Badge>
          </div>
        </div>

        {/* USER PROFILE */}
        <div className="px-2 pb-3">
          <div className="flex items-center gap-3">
            <Avatar className="h-12 w-12">
              <AvatarImage src="/placeholder-avatar.jpg" alt="Lucas Oshan" />
              <AvatarFallback className="bg-primary text-primary-foreground">
                LO
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 space-y-1">
              <p className="text-sm font-medium leading-none">Lucas Oshan</p>
              <p className="text-xs text-muted-foreground">@lucasoshan</p>
            </div>
          </div>
          <div className="mt-3">
            <Badge variant="outline" className="gap-1 border-yellow-500/50 text-yellow-600 dark:text-yellow-400">
              <Star className="h-3 w-3 fill-current" />
              Gold • 82
            </Badge>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        {/* NAVIGATION */}
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => {
                const Icon = item.icon
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton
                      asChild
                      isActive={item.active}
                    >
                      <a href={item.href}>
                        <Icon className="h-4 w-4" />
                        <span>{item.title}</span>
                      </a>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* REPOSITORIES SECTION */}
        <SidebarGroup>
          <SidebarGroupLabel className="flex items-center justify-between">
            <span>Active Repos</span>
            <Badge variant="secondary" className="h-5 rounded-full px-2 text-xs">
              {mockRepos.filter((r) => r.selected).length}
            </Badge>
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mockRepos.map((repo) => (
                <SidebarMenuItem key={repo.name}>
                  <div
                    className={cn(
                      "flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors hover:bg-sidebar-accent",
                      repo.selected && "bg-sidebar-accent/50"
                    )}
                  >
                    <input
                      type="checkbox"
                      checked={repo.selected}
                      className="h-3 w-3 rounded border-border"
                      readOnly
                    />
                    <div className="flex-1 overflow-hidden">
                      <div className="flex items-center gap-2">
                        <span className="truncate text-xs font-medium">{repo.name}</span>
                        <Circle
                          className={cn(
                            "h-2 w-2 fill-current",
                            repo.online ? "text-green-500" : "text-gray-400"
                          )}
                        />
                      </div>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Star className="h-3 w-3" />
                        <span>{repo.stars}</span>
                      </div>
                    </div>
                  </div>
                </SidebarMenuItem>
              ))}
              <SidebarMenuItem>
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start gap-2 px-2 text-xs"
                >
                  <Plus className="h-4 w-4" />
                  Add Repository
                </Button>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      {/* FOOTER */}
      <SidebarFooter className="border-t">
        <div className="flex items-center justify-between px-2 py-2 text-xs">
          <div className="flex gap-3">
            <a
              href="/help"
              className="flex items-center gap-1 text-muted-foreground transition-colors hover:text-foreground"
            >
              <HelpCircle className="h-3 w-3" />
              Help
            </a>
            <a
              href="/docs"
              className="flex items-center gap-1 text-muted-foreground transition-colors hover:text-foreground"
            >
              <BookOpen className="h-3 w-3" />
              Docs
            </a>
          </div>
          <div className="flex items-center gap-2">
            {mounted && (
              <>
                <Sun className="h-3 w-3 text-muted-foreground" />
                <Switch
                  checked={theme === "dark"}
                  onCheckedChange={(checked) => setTheme(checked ? "dark" : "light")}
                  className="scale-75"
                />
                <Moon className="h-3 w-3 text-muted-foreground" />
              </>
            )}
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
