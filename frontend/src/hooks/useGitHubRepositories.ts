import { useState, useEffect, useCallback } from 'react';
import {
  fetchAllGitHubRepositories,
  fetchGitHubUser,
  hasGitHubToken,
  type GitHubRepository,
  type GitHubUser,
} from '@/lib/github';

export function useGitHubRepositories() {
  const [repositories, setRepositories] = useState<GitHubRepository[]>([]);
  const [user, setUser] = useState<GitHubUser | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadRepositories = useCallback(async () => {
    if (!hasGitHubToken()) {
      setError('No GitHub token available. Please login with GitHub.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Fetch user profile and repositories in parallel
      const [userProfile, repos] = await Promise.all([
        fetchGitHubUser(),
        fetchAllGitHubRepositories(),
      ]);

      setUser(userProfile);
      setRepositories(repos);

      console.log(`Loaded ${repos.length} repositories from GitHub`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load repositories';
      setError(errorMessage);
      console.error('Error loading GitHub data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-load repositories if token is available
  useEffect(() => {
    if (hasGitHubToken()) {
      loadRepositories();
    }
  }, [loadRepositories]);

  const refetch = useCallback(() => {
    loadRepositories();
  }, [loadRepositories]);

  return {
    repositories,
    user,
    loading,
    error,
    refetch,
    hasToken: hasGitHubToken(),
  };
}
