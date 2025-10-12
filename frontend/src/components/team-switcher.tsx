"use client"

import * as React from "react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import { CaretSortIcon, PlusIcon } from "@radix-ui/react-icons"

export function TeamSwitcher({
  teams,
}: {
  teams: {
    name: string
    logo: React.ElementType
    plan: string
  }[]
}) {
  const { isMobile } = useSidebar()
  const [activeTeam, setActiveTeam] = React.useState(teams[0])

  if (!activeTeam) {
    return null
  }

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="group/team transition-all duration-300 hover:bg-muted/50 data-[state=open]:bg-muted border border-transparent hover:border-border"
            >
              <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground transition-all duration-300 group-hover/team:scale-105">
                <activeTeam.logo className="size-4" />
              </div>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold transition-colors duration-300 group-hover/team:text-foreground">
                  {activeTeam.name}
                </span>
                <span className="truncate text-xs transition-colors duration-300 group-hover/team:text-foreground/70">{activeTeam.plan}</span>
              </div>
              <CaretSortIcon className="ml-auto" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-[--radix-dropdown-menu-trigger-width] min-w-48 rounded-lg border shadow-lg p-1"
            align="start"
            side={isMobile ? "bottom" : "right"}
            sideOffset={4}
          >
            <DropdownMenuLabel className="text-[10px] font-semibold text-muted-foreground px-2 py-1">
              TEAMS
            </DropdownMenuLabel>
            {teams.map((team, index) => (
              <DropdownMenuItem
                key={team.name}
                onClick={() => setActiveTeam(team)}
                className="group/item cursor-pointer gap-2 px-2 py-1.5 rounded-md text-xs transition-all duration-200"
              >
                <div className="flex size-5 items-center justify-center rounded-md border bg-muted/50 transition-all duration-200 group-hover/item:scale-105 dark:group-hover/item:border-primary dark:group-hover/item:bg-primary/10">
                  <team.logo className="size-3 shrink-0 transition-colors duration-200 dark:group-hover/item:text-primary" />
                </div>
                <span className="flex-1 font-medium">{team.name}</span>
                <DropdownMenuShortcut className="text-[9px] opacity-40">⌘{index + 1}</DropdownMenuShortcut>
              </DropdownMenuItem>
            ))}
            <DropdownMenuSeparator className="my-1" />
            <DropdownMenuItem className="group/item cursor-pointer gap-2 px-2 py-1.5 rounded-md text-xs transition-all duration-300 bg-transparent hover:bg-transparent">
              <div className="flex size-5 items-center justify-center rounded-md border border-dashed border-muted-foreground/30 transition-all duration-300 group-hover/item:border-foreground dark:group-hover/item:border-primary">
                <PlusIcon className="size-3 text-muted-foreground transition-colors duration-300 group-hover/item:text-foreground dark:group-hover/item:text-primary" />
              </div>
              <span className="flex-1 font-medium text-muted-foreground transition-colors duration-300 group-hover/item:text-foreground dark:group-hover/item:text-primary">Add team</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
