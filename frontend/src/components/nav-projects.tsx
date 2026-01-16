"use client"

import * as React from "react"
import {
  GitBranch,
  Star,
  ChevronRight,
  Folder,
  FolderOpen,
  Lock,
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
import { useRepositoryStore } from "@/store/repositories"

interface FolderRepo {
  id: string
  name: string
  owner: string
  is_private: boolean
}

interface FolderStructure {
  id: string
  name: string
  icon: LucideIcon
  type: "special" | "folder"
  repos: FolderRepo[]
  subfolders?: FolderStructure[]
}

export function NavProjects() {
  // Use a ref to track if we've initialized to prevent loops
  const initializedRef = React.useRef(false)
  const [folderStructure, setFolderStructure] = React.useState<FolderStructure[]>([])

  // Subscribe to repositories with a stable selector
  const repositories = useRepositoryStore((state) => state.repositories)

  // Update folder structure when repositories change
  React.useEffect(() => {
    // Group repositories
    const favoriteRepos = repositories.filter(r => r.is_favorite)
    const otherRepos = repositories.filter(r => !r.is_favorite)

    // Build folder structure dynamically
    const structure: FolderStructure[] = []

    // Add favorites if any
    if (favoriteRepos.length > 0) {
      structure.push({
        id: "fav",
        name: "Favorites",
        icon: Star,
        type: "special" as const,
        repos: favoriteRepos.map(r => ({
          id: r.id,
          name: r.name,
          owner: r.owner,
          is_private: r.is_private,
        }))
      })
    }

    // Add other repos (all non-favorites)
    if (otherRepos.length > 0) {
      structure.push({
        id: "all",
        name: "All Repositories",
        icon: Folder,
        type: "folder" as const,
        repos: otherRepos.map(r => ({
          id: r.id,
          name: r.name,
          owner: r.owner,
          is_private: r.is_private,
        }))
      })
    }

    setFolderStructure(structure)
    initializedRef.current = true
  }, [repositories])

  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel>Repositories</SidebarGroupLabel>
      <SidebarMenu>
        {folderStructure.length > 0 ? (
          folderStructure.map((folder) => (
            <FolderItem key={folder.id} folder={folder} />
          ))
        ) : (
          <div className="px-3 py-4 text-xs text-sidebar-foreground/50">
            No repositories yet
          </div>
        )}
      </SidebarMenu>
    </SidebarGroup>
  )
}

function FolderItem({ folder, level = 0 }: { folder: FolderStructure, level?: number }) {
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
            {folder.repos?.map((repo) => (
              <SidebarMenuSubItem key={repo.id}>
                <SidebarMenuSubButton
                  asChild
                  className="text-xs sidebar-hover-premium group/item"
                  style={{ paddingLeft: `${(level + 1) * 12}px` }}
                >
                  <a
                    href={`https://github.com/${repo.owner}/${repo.name}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 min-w-0"
                  >
                    <GitBranch className="h-3 w-3 shrink-0 text-sidebar-foreground/40 sidebar-icon-glow transition-all duration-300 group-hover/item:text-primary group-hover/item:scale-105" />
                    <span className="truncate text-sidebar-foreground/70 transition-colors duration-300 group-hover/item:text-primary">
                      {repo.owner}/
                    </span>
                    <span className="truncate font-semibold transition-colors duration-300 group-hover/item:text-primary">
                      {repo.name}
                    </span>
                    {repo.is_private && (
                      <Lock className="h-2.5 w-2.5 shrink-0 text-sidebar-foreground/40 transition-all duration-300 group-hover/item:text-primary" />
                    )}
                  </a>
                </SidebarMenuSubButton>
              </SidebarMenuSubItem>
            ))}

            {/* Render subfolders recursively */}
            {folder.subfolders?.map((subfolder) => (
              <FolderItem key={subfolder.id} folder={subfolder} level={level + 1} />
            ))}
          </SidebarMenuSub>
        </CollapsibleContent>
      </SidebarMenuItem>
    </Collapsible>
  )
}

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(' ')
}
