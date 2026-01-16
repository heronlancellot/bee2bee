"use client"

import * as React from "react"
import { Star, GitBranch, Lock, Globe, Search, ChevronDown, X, Filter, FilterX, BookPlus } from "lucide-react"
import { Repository } from "@/types"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface RepoSelectorSidebarProps {
  repositories: Repository[]
  selectedRepos: string[]
  onRepoToggle: (repoId: string) => void
  onFavoriteToggle: (repoId: string) => void
  onDeselectAll: () => void
}

export function RepoSelectorSidebar({
  repositories,
  selectedRepos,
  onRepoToggle,
  onFavoriteToggle,
  onDeselectAll,
}: RepoSelectorSidebarProps) {
  const [search, setSearch] = React.useState("")
  const [showFavorites, setShowFavorites] = React.useState(true)
  const [showPrivate, setShowPrivate] = React.useState(true)
  const [showPublic, setShowPublic] = React.useState(true)
  const [showOnlySelected, setShowOnlySelected] = React.useState(false)

  const favorites = repositories.filter((r) => r.is_favorite)
  const privateRepos = repositories.filter((r) => r.is_private && !r.is_favorite)
  const publicRepos = repositories.filter((r) => !r.is_private && !r.is_favorite)

  const filteredFavorites = favorites.filter((r) =>
    r.full_name.toLowerCase().includes(search.toLowerCase()) &&
    (!showOnlySelected || selectedRepos.includes(r.id))
  )
  const filteredPrivate = privateRepos.filter((r) =>
    r.full_name.toLowerCase().includes(search.toLowerCase()) &&
    (!showOnlySelected || selectedRepos.includes(r.id))
  )
  const filteredPublic = publicRepos.filter((r) =>
    r.full_name.toLowerCase().includes(search.toLowerCase()) &&
    (!showOnlySelected || selectedRepos.includes(r.id))
  )

  return (
    <aside
      className="flex h-full flex-col border-l bg-sidebar"
      role="complementary"
      aria-label="Repository selector"
    >
      {/* Search and Add Repo Button */}
      <div className="p-3 pt-4">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search
              className="pointer-events-none absolute left-2.5 top-2 h-3.5 w-3.5 text-sidebar-foreground/40"
              aria-hidden="true"
            />
            <Input
              type="search"
              placeholder="Search..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-8 border-sidebar-border/50 bg-sidebar/50 pl-8 pr-8 text-xs text-sidebar-foreground placeholder:text-sidebar-foreground/50 focus-visible:ring-1 focus-visible:ring-primary"
              aria-label="Search repositories"
            />
            {search && (
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-0.5 top-0.5 h-7 w-7 p-0 hover:bg-sidebar-accent"
                onClick={() => setSearch("")}
                aria-label="Clear search"
              >
                <X className="h-3 w-3" />
              </Button>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => console.log('Add new repo')}
            className="h-8 w-8 p-0 shrink-0 hover:bg-sidebar-accent transition-colors border border-sidebar-border/50 bg-sidebar/50"
            aria-label="Add new repository"
            title="Add new repository to index"
          >
            <BookPlus className="h-3.5 w-3.5 text-sidebar-foreground/70 transition-all duration-300 hover:text-primary hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]" />
          </Button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="px-3 pb-3">
        <div className="flex items-center justify-between gap-2 px-2 py-1.5 rounded-md bg-sidebar-accent/30 border border-sidebar-border/30">
          <div className="flex items-center gap-1.5">
            <Checkbox
              id="select-all"
              checked={selectedRepos.length === repositories.length}
              onCheckedChange={(checked) => {
                if (checked) {
                  // Select all
                  const allIds = repositories.map((r) => r.id)
                  allIds.forEach((id) => {
                    if (!selectedRepos.includes(id)) {
                      onRepoToggle(id)
                    }
                  })
                } else {
                  // Deselect all
                  onDeselectAll()
                }
              }}
              className="data-[state=checked]:bg-primary data-[state=checked]:border-primary h-3 w-3 rounded-[3px]"
            />
            <label
              htmlFor="select-all"
              className="text-[11px] text-sidebar-foreground/70 cursor-pointer select-none"
            >
              All ({selectedRepos.length}/{repositories.length})
            </label>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowOnlySelected(!showOnlySelected)}
            className={cn(
              "h-5 w-5 p-0 hover:bg-sidebar-accent/50 transition-colors rounded-[4px]",
              showOnlySelected ? "text-primary hover:text-primary" : "text-sidebar-foreground/50 hover:text-primary"
            )}
            aria-label={showOnlySelected ? "Show all repos" : "Show selected only"}
          >
            {showOnlySelected ? (
              <FilterX className="h-3 w-3" />
            ) : (
              <Filter className="h-3 w-3" />
            )}
          </Button>
        </div>
      </div>

      {/* Repository Lists */}
      <nav className="flex-1 overflow-y-auto px-2" aria-label="Repository list">
        {/* No results message */}
        {filteredFavorites.length === 0 &&
          filteredPrivate.length === 0 &&
          filteredPublic.length === 0 && (
            <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
              <Search className="h-12 w-12 text-sidebar-foreground/20 mb-3" />
              <p className="text-sm text-sidebar-foreground/70">
                No repositories found
              </p>
              {search && (
                <Button
                  variant="link"
                  size="sm"
                  onClick={() => setSearch("")}
                  className="mt-2"
                >
                  Clear search
                </Button>
              )}
            </div>
          )}

        {/* Favorites */}
        {filteredFavorites.length > 0 && (
          <Collapsible open={showFavorites} onOpenChange={setShowFavorites}>
            <CollapsibleTrigger asChild>
              <Button
                variant="ghost"
                className="group w-full justify-between px-2 py-1.5 h-auto text-xs font-medium text-sidebar-foreground/70 hover:bg-transparent hover:text-sidebar-foreground transition-all duration-300"
                aria-expanded={showFavorites}
                aria-controls="favorites-list"
              >
                <div className="flex items-center gap-1.5">
                  <Star className="h-3 w-3 fill-primary text-primary transition-all duration-300 group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]" aria-hidden="true" />
                  <span className="transition-all duration-300 group-hover:text-primary dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.3)]">FAVORITES</span>
                  <span className="text-sidebar-foreground/50">
                    {filteredFavorites.length}
                  </span>
                </div>
                <ChevronDown
                  className={cn(
                    "h-3 w-3 transition-all duration-300 group-hover:text-primary dark:group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)]",
                    showFavorites && "rotate-180"
                  )}
                  aria-hidden="true"
                />
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent id="favorites-list" className="space-y-1 py-1">
              {filteredFavorites.map((repo) => (
                <RepoItem
                  key={repo.id}
                  repo={repo}
                  isSelected={selectedRepos.includes(repo.id)}
                  onToggle={() => onRepoToggle(repo.id)}
                  onFavoriteToggle={() => onFavoriteToggle(repo.id)}
                />
              ))}
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Private Repos */}
        {filteredPrivate.length > 0 && (
          <Collapsible open={showPrivate} onOpenChange={setShowPrivate} className="mt-3">
            <CollapsibleTrigger asChild>
              <Button
                variant="ghost"
                className="group w-full justify-between px-2 py-1.5 h-auto text-xs font-medium text-sidebar-foreground/70 hover:bg-transparent hover:text-sidebar-foreground transition-all duration-300"
                aria-expanded={showPrivate}
                aria-controls="private-list"
              >
                <div className="flex items-center gap-1.5">
                  <Lock className="h-3 w-3 transition-all duration-300 group-hover:text-primary group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]" aria-hidden="true" />
                  <span className="transition-all duration-300 group-hover:text-primary dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.3)]">PRIVATE</span>
                  <span className="text-sidebar-foreground/50">
                    {filteredPrivate.length}
                  </span>
                </div>
                <ChevronDown
                  className={cn(
                    "h-3 w-3 transition-all duration-300 group-hover:text-primary dark:group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)]",
                    showPrivate && "rotate-180"
                  )}
                  aria-hidden="true"
                />
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent id="private-list" className="space-y-1 py-1">
              {filteredPrivate.map((repo) => (
                <RepoItem
                  key={repo.id}
                  repo={repo}
                  isSelected={selectedRepos.includes(repo.id)}
                  onToggle={() => onRepoToggle(repo.id)}
                  onFavoriteToggle={() => onFavoriteToggle(repo.id)}
                />
              ))}
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Public Repos */}
        {filteredPublic.length > 0 && (
          <Collapsible open={showPublic} onOpenChange={setShowPublic} className="mt-3">
            <CollapsibleTrigger asChild>
              <Button
                variant="ghost"
                className="group w-full justify-between px-2 py-1.5 h-auto text-xs font-medium text-sidebar-foreground/70 hover:bg-transparent hover:text-sidebar-foreground transition-all duration-300"
                aria-expanded={showPublic}
                aria-controls="public-list"
              >
                <div className="flex items-center gap-1.5">
                  <Globe className="h-3 w-3 transition-all duration-300 group-hover:text-primary group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]" aria-hidden="true" />
                  <span className="transition-all duration-300 group-hover:text-primary dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.3)]">PUBLIC</span>
                  <span className="text-sidebar-foreground/50">
                    {filteredPublic.length}
                  </span>
                </div>
                <ChevronDown
                  className={cn(
                    "h-3 w-3 transition-all duration-300 group-hover:text-primary dark:group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)]",
                    showPublic && "rotate-180"
                  )}
                  aria-hidden="true"
                />
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent id="public-list" className="space-y-1 py-1">
              {filteredPublic.map((repo) => (
                <RepoItem
                  key={repo.id}
                  repo={repo}
                  isSelected={selectedRepos.includes(repo.id)}
                  onToggle={() => onRepoToggle(repo.id)}
                  onFavoriteToggle={() => onFavoriteToggle(repo.id)}
                />
              ))}
            </CollapsibleContent>
          </Collapsible>
        )}
      </nav>

      {/* Footer Info */}
      <footer className="shrink-0 border-t border-sidebar-border p-4 bg-sidebar">
        <p className="text-xs text-sidebar-foreground/70" role="status" aria-live="polite">
          {selectedRepos.length > 0
            ? `AI will search across ${selectedRepos.length} ${
                selectedRepos.length === 1 ? "repository" : "repositories"
              }`
            : "Select repositories to query with AI"}
        </p>
      </footer>
    </aside>
  )
}

interface RepoItemProps {
  repo: Repository
  isSelected: boolean
  onToggle: () => void
  onFavoriteToggle: () => void
}

function RepoItem({
  repo,
  isSelected,
  onToggle,
  onFavoriteToggle,
}: RepoItemProps) {
  return (
    <article className="px-1">
      <div
        className={cn(
          "group relative flex items-center rounded-lg transition-all duration-200 cursor-pointer border gap-2 p-1.5",
          "hover:bg-sidebar-accent/30 hover:border-primary/50",
          "focus-within:ring-2 focus-within:ring-primary/20",
          isSelected
            ? "bg-primary/5 border-primary/60 shadow-sm"
            : "border-sidebar-border/40 bg-sidebar/50 hover:shadow-sm"
        )}
        onClick={onToggle}
        role="button"
        tabIndex={0}
        aria-pressed={isSelected}
        aria-label={`${isSelected ? 'Deselect' : 'Select'} repository ${repo.full_name}`}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            onToggle()
          }
        }}
      >
        <Checkbox
          checked={isSelected}
          onCheckedChange={onToggle}
          className="shrink-0 data-[state=checked]:bg-primary data-[state=checked]:border-primary transition-all duration-200 h-3 w-3"
          onClick={(e) => e.stopPropagation()}
          aria-label={`Toggle ${repo.full_name}`}
        />
        <div className="flex min-w-0 flex-1 items-center justify-between gap-2">
          <div className="min-w-0 flex-1 flex items-center gap-1">
            <GitBranch
              className="h-3 w-3 shrink-0 text-sidebar-foreground/40 transition-all duration-300 group-hover:text-primary group-hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)] dark:group-hover:drop-shadow-[0_0_6px_hsl(var(--primary)/0.5)]"
              aria-hidden="true"
            />
            <p className="truncate text-xs text-sidebar-foreground/70 transition-colors duration-300 group-hover:text-primary">
              {repo.owner}/
            </p>
            <p className="truncate text-xs font-semibold text-sidebar-foreground transition-colors duration-300 group-hover:text-primary">
              {repo.name}
            </p>
            {repo.is_private && (
              <Lock
                className="h-2.5 w-2.5 shrink-0 text-sidebar-foreground/40 transition-all duration-300 group-hover:text-primary group-hover:drop-shadow-[0_0_3px_hsl(var(--primary)/0.3)]"
                aria-label="Private repository"
              />
            )}
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onFavoriteToggle()
            }}
            className={cn(
              "shrink-0 p-0.5 rounded transition-all duration-300",
              "focus:outline-none focus:ring-1 focus:ring-primary",
              repo.is_favorite ? "opacity-100" : "opacity-0 group-hover:opacity-100"
            )}
            aria-label={repo.is_favorite ? "Remove from favorites" : "Add to favorites"}
          >
            <Star
              className={cn(
                "h-3 w-3 transition-all duration-300",
                repo.is_favorite
                  ? "fill-primary text-primary drop-shadow-[0_0_4px_hsl(var(--primary)/0.5)]"
                  : "text-sidebar-foreground/40 hover:text-primary hover:drop-shadow-[0_0_4px_hsl(var(--primary)/0.4)]"
              )}
            />
          </button>
        </div>
      </div>
    </article>
  )
}
