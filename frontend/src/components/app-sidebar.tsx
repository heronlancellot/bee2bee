"use client"

import * as React from "react"
import {
  BookMarked,
  MessageSquare,
  User,
  Settings2,
  Bot,
  Plus,
  LayoutDashboard,
  History,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavProjects } from "@/components/nav-projects"
import { NavUser } from "@/components/nav-user"
import { TeamSwitcher } from "@/components/team-switcher"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
  SidebarGroup,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from "@/components/ui/sidebar"
import Link from "next/link"
// import GlareHover from "@/components/GlareHover" // TODO: missing component

const data = {
  user: {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  teams: [
    {
      name: "NectarDAO",
      logo: Bot,
      plan: "AI-Powered Matching",
    },
  ],
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: LayoutDashboard,
    },
    {
      title: "My Profile",
      url: "/profile",
      icon: User,
      items: [
        {
          title: "Overview",
          url: "/profile",
        },
        {
          title: "Activity",
          url: "/profile/activity",
        },
        {
          title: "Contributions",
          url: "/profile/contributions",
        },
      ],
    },
    {
      title: "Settings",
      url: "/settings",
      icon: Settings2,
      items: [
        {
          title: "Integrations",
          url: "/settings/integrations",
        },
        {
          title: "Preferences",
          url: "/settings/preferences",
        },
      ],
    },
  ],
  projects: [
    {
      name: "My Repositories",
      url: "/repos",
      icon: BookMarked,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <TeamSwitcher teams={data.teams} />
      </SidebarHeader>
      <SidebarContent>
        {/* New Chat Button */}
        <SidebarGroup className="px-2 pt-2 pb-0">
          <SidebarMenu>
            <SidebarMenuItem className="list-none overflow-visible">
              <Link href="/chat" className="block w-full">
                <div className="flex items-center gap-2 bg-[hsl(var(--secondary-accent))] hover:bg-[hsl(var(--secondary-accent))]/90 rounded-md px-2 h-8 transition-all duration-300 shadow-sm hover:shadow-md">
                  <Plus className="h-4 w-4 text-[hsl(var(--secondary-accent-foreground))] flex-shrink-0" />
                  <span className="text-sm text-[hsl(var(--secondary-accent-foreground))] font-medium">New Chat</span>
                </div>
              </Link>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>

        <NavMain items={data.navMain} />
        <NavProjects projects={data.projects} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
