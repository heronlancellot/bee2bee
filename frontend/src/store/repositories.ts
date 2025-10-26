import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Repository } from '@/types'

// Re-export Repository type for convenience
export type { Repository }

interface RepositoryStore {
  repositories: Repository[]
  selectedRepos: string[]

  // Actions
  setRepositories: (repos: Repository[]) => void
  addRepository: (repo: Repository) => void
  removeRepository: (repoId: string) => void
  toggleFavorite: (repoId: string) => void
  toggleSelection: (repoId: string) => void
  selectAllRepositories: () => void
  deselectAllRepositories: () => void
  clearRepositories: () => void
}

export const useRepositoryStore = create<RepositoryStore>()(
  persist(
    (set, get) => ({
      repositories: [],
      selectedRepos: [],

      setRepositories: (repos) => set({
        repositories: repos,
        // Auto-select all repos when setting for the first time
        selectedRepos: get().selectedRepos.length === 0 ? repos.map(r => r.id) : get().selectedRepos
      }),

      addRepository: (repo) => set((state) => ({
        repositories: [...state.repositories, repo],
        selectedRepos: [...state.selectedRepos, repo.id]
      })),

      removeRepository: (repoId) => set((state) => ({
        repositories: state.repositories.filter(r => r.id !== repoId),
        selectedRepos: state.selectedRepos.filter(id => id !== repoId)
      })),

      toggleFavorite: (repoId) => set((state) => ({
        repositories: state.repositories.map(r =>
          r.id === repoId ? { ...r, is_favorite: !r.is_favorite } : r
        )
      })),

      toggleSelection: (repoId) => set((state) => ({
        selectedRepos: state.selectedRepos.includes(repoId)
          ? state.selectedRepos.filter(id => id !== repoId)
          : [...state.selectedRepos, repoId]
      })),

      selectAllRepositories: () => set((state) => ({
        selectedRepos: state.repositories.map(r => r.id)
      })),

      deselectAllRepositories: () => set({ selectedRepos: [] }),

      clearRepositories: () => set({ repositories: [], selectedRepos: [] })
    }),
    {
      name: 'repository-storage',
      partialize: (state) => ({
        repositories: state.repositories,
        selectedRepos: state.selectedRepos,
      }),
    }
  )
)

// Custom hooks for common use cases
export const useFavoriteRepositories = () =>
  useRepositoryStore((state) => state.repositories.filter(r => r.is_favorite))

export const useSelectedRepositoriesData = () =>
  useRepositoryStore((state) =>
    state.repositories.filter(r => state.selectedRepos.includes(r.id))
  )

// Fixed: Use stable selectors to prevent infinite re-renders
export const useRepositoryActions = () => {
  const addRepository = useRepositoryStore((state) => state.addRepository)
  const removeRepository = useRepositoryStore((state) => state.removeRepository)
  const toggleFavorite = useRepositoryStore((state) => state.toggleFavorite)
  const toggleSelection = useRepositoryStore((state) => state.toggleSelection)
  const selectAll = useRepositoryStore((state) => state.selectAllRepositories)
  const deselectAll = useRepositoryStore((state) => state.deselectAllRepositories)
  const clear = useRepositoryStore((state) => state.clearRepositories)

  return {
    addRepository,
    removeRepository,
    toggleFavorite,
    toggleSelection,
    selectAll,
    deselectAll,
    clear,
  }
}
