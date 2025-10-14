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
  useSidebar,
} from "@/components/ui/sidebar"
import Link from "next/link"
import { useTheme } from "next-themes"
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
  const { state } = useSidebar()

  return (
    <Sidebar collapsible="icon" {...props}>
      {/* Spacer for header */}
      <div className="h-12 shrink-0" />
      <SidebarHeader>
        <TeamSwitcher teams={data.teams} />
      </SidebarHeader>
      <SidebarContent>
        {/* New Chat Button */}
        <SidebarGroup className="px-2 pt-2 pb-0">
          <SidebarMenu>
            <SidebarMenuItem className="list-none overflow-visible">
              <SidebarMenuButton
                asChild
                tooltip="New Chat"
                className="group relative h-8 overflow-hidden bg-[hsl(var(--secondary-accent))] hover:bg-[hsl(var(--secondary-accent))]/80 active:bg-[hsl(var(--secondary-accent))] dark:bg-[hsl(var(--primary))] dark:hover:bg-[hsl(var(--primary))]/90 dark:active:bg-[hsl(var(--primary))] !text-white hover:!text-white active:!text-white transition-all duration-300 shadow-sm hover:shadow-md [&>*]:!text-white [&>*]:hover:!text-white [&>*]:active:!text-white"
              >
                <Link href="/chat" className="relative !text-white hover:!text-white active:!text-white">
                  {/* Glare effect */}
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none">
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-out" />
                  </div>

                  <img
                    src="/custom-icons/chat_ai_01.svg"
                    alt="Chat"
                    className="h-4 w-4 flex-shrink-0 brightness-0 invert transition-all duration-300 group-hover:scale-110"
                  />
                  <span className="text-sm font-medium relative z-10 !text-white">New Chat</span>
                </Link>
              </SidebarMenuButton>
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
