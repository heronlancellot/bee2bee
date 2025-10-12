"use client"

import { Star, Circle, Plus } from "lucide-react"

import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

export function NavRepos({
  repositories,
}: {
  repositories: {
    name: string
    url: string
    stars: string
    online: boolean
  }[]
}) {
  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <div className="flex items-center justify-between px-2">
        <SidebarGroupLabel>Active Repos</SidebarGroupLabel>
        <Badge variant="secondary" className="h-5 rounded-full px-2 text-xs">
          {repositories.length}
        </Badge>
      </div>
      <SidebarMenu>
        {repositories.map((repo) => (
          <SidebarMenuItem key={repo.name}>
            <SidebarMenuButton asChild>
              <a href={repo.url} className="flex items-center gap-2">
                <div className="flex flex-1 flex-col gap-0.5 overflow-hidden">
                  <div className="flex items-center gap-2">
                    <span className="truncate text-xs font-medium">{repo.name}</span>
                    <Circle
                      className={cn(
                        "h-2 w-2 shrink-0 fill-current",
                        repo.online ? "text-green-500" : "text-gray-400"
                      )}
                    />
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Star className="h-3 w-3" />
                    <span>{repo.stars}</span>
                  </div>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}
        <SidebarMenuItem>
          <SidebarMenuButton className="text-sidebar-foreground/70">
            <Plus className="h-4 w-4 text-sidebar-foreground/70" />
            <span>Add Repository</span>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarGroup>
  )
}
