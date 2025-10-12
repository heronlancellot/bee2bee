"use client"

import * as React from "react"
import Link from "next/link"
import {
  GitBranch,
  Star,
  ChevronRight,
  User,
  BookMarked,
  Folder,
  FolderOpen,
  type LucideIcon,
} from "lucide-react"

import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"

// Mock folder structure with repositories
const mockFolderStructure = [
  {
    id: "fav",
    name: "Favorites",
    icon: Star,
    type: "special" as const,
    repos: [
      { id: "1", name: "repomind-ui" },
      { id: "2", name: "agent-orchestrator" },
    ]
  },
  {
    id: "work",
    name: "Work",
    icon: Folder,
    type: "folder" as const,
    repos: [
      { id: "3", name: "blockchain-integration" },
      { id: "4", name: "profile-analyzer" },
    ],
    subfolders: [
      {
        id: "work-client",
        name: "Client Projects",
        repos: [
          { id: "5", name: "ecommerce-platform" },
        ]
      }
    ]
  },
  {
    id: "personal",
    name: "Personal",
    icon: Folder,
    type: "folder" as const,
    repos: [
      { id: "6", name: "portfolio-site" },
      { id: "7", name: "side-project" },
    ]
  }
]

export function NavProjects({
  projects,
}: {
  projects: {
    name: string
    url: string
    icon: LucideIcon
  }[]
}) {
  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel>Projects</SidebarGroupLabel>
      <SidebarMenu>
        {mockFolderStructure.map((folder) => (
          <FolderItem key={folder.id} folder={folder} />
        ))}
      </SidebarMenu>
    </SidebarGroup>
  )
}

function FolderItem({ folder, level = 0 }: { folder: any, level?: number }) {
  const [isOpen, setIsOpen] = React.useState(folder.id === "fav")
  const Icon = folder.type === "special" ? folder.icon : isOpen ? FolderOpen : Folder
  const isFavorite = folder.type === "special"

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen} asChild>
      <SidebarMenuItem>
        <CollapsibleTrigger asChild>
          <SidebarMenuButton
            tooltip={folder.name}
            className="text-xs font-medium sidebar-hover-premium group"
            style={{ paddingLeft: `${level * 12 + 8}px` }}
          >
            <Icon
              className={cn(
                "h-3 w-3 sidebar-icon-glow transition-all duration-300 group-hover:scale-105",
                isFavorite && "fill-primary text-primary"
              )}
            />
            <span>{folder.name}</span>
            {folder.repos && (
              <span className="ml-auto text-[10px] text-sidebar-foreground/50 transition-colors duration-300 group-hover:text-accent">
                {folder.repos.length}
              </span>
            )}
            <ChevronRight
              className={cn(
                "ml-1 h-3 w-3 transition-all duration-300 group-hover:translate-x-0.5",
                isOpen && "rotate-90"
              )}
            />
          </SidebarMenuButton>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <SidebarMenuSub>
            {/* Render repos */}
            {folder.repos?.map((repo: any) => (
              <SidebarMenuSubItem key={repo.id}>
                <SidebarMenuSubButton
                  asChild
                  className="text-xs sidebar-hover-premium group/item"
                  style={{ paddingLeft: `${(level + 1) * 12}px` }}
                >
                  <Link href={`/repos/${repo.id}`}>
                    <GitBranch className="h-3 w-3 text-sidebar-foreground/40 sidebar-icon-glow transition-all duration-300 group-hover/item:text-primary group-hover/item:scale-105" />
                    <span className="truncate transition-colors duration-300">
                      {repo.name}
                    </span>
                  </Link>
                </SidebarMenuSubButton>
              </SidebarMenuSubItem>
            ))}

            {/* Render subfolders recursively */}
            {folder.subfolders?.map((subfolder: any) => (
              <FolderItem key={subfolder.id} folder={subfolder} level={level + 1} />
            ))}
          </SidebarMenuSub>
        </CollapsibleContent>
      </SidebarMenuItem>
    </Collapsible>
  )
}

function cn(...classes: any[]) {
  return classes.filter(Boolean).join(' ')
}
