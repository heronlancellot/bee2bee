/**
 * GitHub API Helper
 * Handles GitHub API interactions using OAuth provider tokens
 */

export interface GitHubRepository {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  private: boolean;
  html_url: string;
  language: string | null;
  stargazers_count: number;
  default_branch: string;
  updated_at: string;
  owner: {
    login: string;
    avatar_url: string;
  };
}

export interface GitHubUser {
  id: number;
  login: string;
  name: string | null;
  email: string | null;
  avatar_url: string;
  bio: string | null;
  public_repos: number;
  followers: number;
  following: number;
}

/**
 * Get GitHub access token from localStorage
 */
export function getGitHubToken(): string | null {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem('oauth_provider_token');
}

/**
 * Fetch authenticated user's GitHub profile
 */
export async function fetchGitHubUser(): Promise<GitHubUser | null> {
  const token = getGitHubToken();

  if (!token) {
    console.error('No GitHub token found');
    return null;
  }

  try {
    const response = await fetch('https://api.github.com/user', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github.v3+json',
      },
    });

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching GitHub user:', error);
    return null;
  }
}

/**
 * Fetch user's GitHub repositories
 * @param sort - Sort order: 'created', 'updated', 'pushed', 'full_name'
 * @param perPage - Number of repositories per page (max 100)
 * @param page - Page number
 */
export async function fetchGitHubRepositories(
  sort: 'created' | 'updated' | 'pushed' | 'full_name' = 'updated',
  perPage: number = 100,
  page: number = 1
): Promise<GitHubRepository[]> {
  const token = getGitHubToken();

  if (!token) {
    console.error('No GitHub token found');
    return [];
  }

  try {
    const response = await fetch(
      `https://api.github.com/user/repos?sort=${sort}&per_page=${perPage}&page=${page}&affiliation=owner,collaborator,organization_member`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/vnd.github.v3+json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching GitHub repositories:', error);
    return [];
  }
}

/**
 * Fetch all repositories (handles pagination)
 */
export async function fetchAllGitHubRepositories(): Promise<GitHubRepository[]> {
  const token = getGitHubToken();

  if (!token) {
    console.error('No GitHub token found');
    return [];
  }

  const allRepos: GitHubRepository[] = [];
  let page = 1;
  let hasMore = true;

  try {
    while (hasMore) {
      const repos = await fetchGitHubRepositories('updated', 100, page);

      if (repos.length === 0) {
        hasMore = false;
      } else {
        allRepos.push(...repos);
        page++;

        // GitHub API typically limits to 100 items per page
        // If we get less than 100, we've reached the end
        if (repos.length < 100) {
          hasMore = false;
        }
      }
    }

    return allRepos;
  } catch (error) {
    console.error('Error fetching all repositories:', error);
    return allRepos; // Return what we have so far
  }
}

/**
 * Fetch a specific repository by owner and name
 */
export async function fetchGitHubRepository(
  owner: string,
  repo: string
): Promise<GitHubRepository | null> {
  const token = getGitHubToken();

  if (!token) {
    console.error('No GitHub token found');
    return null;
  }

  try {
    const response = await fetch(
      `https://api.github.com/repos/${owner}/${repo}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/vnd.github.v3+json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching GitHub repository:', error);
    return null;
  }
}

/**
 * Check if GitHub token is available
 */
export function hasGitHubToken(): boolean {
  return !!getGitHubToken();
}

/**
 * Clear GitHub tokens from localStorage
 */
export function clearGitHubTokens(): void {
  if (typeof window === 'undefined') return;

  window.localStorage.removeItem('oauth_provider_token');
  window.localStorage.removeItem('oauth_provider_refresh_token');
  console.log('GitHub tokens cleared');
}
