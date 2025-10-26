/* eslint-disable @next/next/no-img-element */
"use client";

import * as React from "react";
import { BookMarked, User, Bot } from "lucide-react";

import { NavMain } from "@/components/nav-main";
import { NavProjects } from "@/components/nav-projects";
import { TeamSwitcher } from "@/components/team-switcher";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarRail,
  SidebarGroup,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  useSidebar,
} from "@/components/ui/sidebar";
import Link from "next/link";
import { useUserProfile } from "@/hooks/useUserProfile";
import { useAuth } from "@/integrations/supabase/hooks/useAuth";

const navMainData = [
  // {
  //   title: "Dashboard",
  //   url: "/dashboard",
  //   icon: LayoutDashboard,
  // },
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
];

const projectsData = [
  {
    name: "My Repositories",
    url: "/repos",
    icon: BookMarked,
  },
];

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { state } = useSidebar();
  const { profile } = useUserProfile();
  const { user } = useAuth();

  // Build teams data from profile
  const teamsData = [
    {
      name:
        profile?.github_username || user?.user_metadata?.user_name || "User",
      logo: Bot,
      plan: "AI-Powered Matching",
    },
  ];

  const isExpanded = state === "expanded";

  return (
    <Sidebar collapsible="icon" {...props}>
      {/* Spacer for header */}
      <div className="h-12 shrink-0" />

      {/* Fixed Header Section */}
      <SidebarHeader className="shrink-0">
        <TeamSwitcher teams={teamsData} />

        {/* New Chat Button - Fixed */}
        <SidebarGroup className="p-0">
          <SidebarMenu>
            <SidebarMenuItem className="w-full list-none overflow-visible">
              <SidebarMenuButton
                asChild
                tooltip="New Chat"
                className="group relative h-8 w-full overflow-hidden bg-[hsl(var(--secondary-accent))] !p-0 !text-white shadow-sm transition-all duration-300 hover:bg-[hsl(var(--secondary-accent))]/80 hover:!text-white hover:shadow-md active:bg-[hsl(var(--secondary-accent))] active:!text-white dark:bg-[hsl(var(--primary))] dark:hover:bg-[hsl(var(--primary))]/90 dark:active:bg-[hsl(var(--primary))] [&>*]:!text-white [&>*]:hover:!text-white [&>*]:active:!text-white"
              >
                <Link
                  href="/chat"
                  className={`relative flex w-full items-center gap-2 !p-0 !text-white hover:!text-white active:!text-white ${isExpanded ? "justify-center" : ""}`}
                >
                  {/* Glare effect */}
                  <div className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-500 group-hover:opacity-100">
                    <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-700 ease-out group-hover:translate-x-full" />
                  </div>

                  <img
                    src="/custom-icons/chat_ai_01.svg"
                    alt="Chat"
                    className="h-4 w-4 flex-shrink-0 brightness-0 invert transition-all duration-300 group-hover:scale-110"
                  />
                  <span className="relative z-10 text-sm font-medium !text-white">
                    New Chat
                  </span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>
      </SidebarHeader>

      {/* Scrollable Content */}
      <SidebarContent>
        <NavMain items={navMainData} />
        <NavProjects projects={projectsData} />
      </SidebarContent>

      <SidebarRail />
    </Sidebar>
  );
}
