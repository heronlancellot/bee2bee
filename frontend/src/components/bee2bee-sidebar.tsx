"use client"

import * as React from "react"
import {
  Home,
  Target,
  Briefcase,
  Package,
  User,
  Settings,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavRepos } from "@/components/nav-repos"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar"
import { Badge } from "@/components/ui/badge"

// Bee2Bee data structure
const data = {
  user: {
    name: "Lucas Oshan",
    email: "@lucasoshan",
    avatar: "/placeholder-avatar.jpg",
  },
  navMain: [
    {
      title: "Dashboard",
      url: "/",
      icon: Home,
      isActive: true,
    },
    {
      title: "My Feed",
      url: "/feed",
      icon: Target,
    },
    {
      title: "My Bounties",
      url: "/bounties",
      icon: Briefcase,
    },
    {
      title: "Repositories",
      url: "/repositories",
      icon: Package,
    },
    {
      title: "Profile",
      url: "/profile",
      icon: User,
    },
    {
      title: "Settings",
      url: "/settings",
      icon: Settings,
    },
  ],
  repositories: [
    {
      name: "awesome-api",
      url: "#",
      stars: "2.3k",
      online: true,
    },
    {
      name: "react-dashboard",
      url: "#",
      stars: "890",
      online: true,
    },
    {
      name: "cli-tool",
      url: "#",
      stars: "450",
      online: false,
    },
  ],
}

export function Bee2BeeSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg">
                  <img
                    src="/gradient_logo_icon.svg"
                    alt="Bee2Bee"
                    className="size-8"
                  />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-serif font-semibold">
                    Bee<span className="text-primary">2</span>Bee
                  </span>
                  <Badge variant="secondary" className="w-fit text-xs">
                    Beta
                  </Badge>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavRepos repositories={data.repositories} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
