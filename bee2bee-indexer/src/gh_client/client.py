"""
GitHub API client for downloading and managing repositories.
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional
import httpx
from github import Github


class GitHubClient:
    """Client for interacting with GitHub API."""

    def __init__(self, token: str):
        self.token = token
        self.client = Github(token)
        self.http_client = httpx.AsyncClient(
            headers={"Authorization": f"token {token}"},
            timeout=120.0,  # Increase timeout for slow connections
        )

    async def download_repo(self, owner: str, name: str, branch: str = "main") -> Path:
        """
        Download a repository to a temporary directory.
        Uses git clone for better WSL compatibility.

        Args:
            owner: Repository owner
            name: Repository name
            branch: Branch to download

        Returns:
            Path to the downloaded repository
        """
        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp(prefix=f"{owner}_{name}_"))
        repo_dir = temp_dir / name

        # Use git clone (more reliable in WSL)
        import subprocess

        url = f"https://github.com/{owner}/{name}.git"

        try:
            # Clone with shallow depth for speed
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, url, str(repo_dir)],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")

            return repo_dir

        except Exception as e:
            # Fallback to tarball method if git fails
            print(f"   ⚠️  Git clone failed, trying tarball download: {e}")
            return await self._download_repo_tarball(owner, name, branch, temp_dir)

    async def _download_repo_tarball(self, owner: str, name: str, branch: str, temp_dir: Path) -> Path:
        """Fallback method using GitHub API tarball download."""
        url = f"https://api.github.com/repos/{owner}/{name}/tarball/{branch}"

        async with self.http_client.stream("GET", url) as response:
            response.raise_for_status()

            tarball_path = temp_dir / "repo.tar.gz"
            with open(tarball_path, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)

        # Extract tarball
        import tarfile

        with tarfile.open(tarball_path, "r:gz") as tar:
            tar.extractall(temp_dir)

        # Remove tarball
        tarball_path.unlink()

        # Find extracted directory (GitHub adds a prefix)
        extracted = [d for d in temp_dir.iterdir() if d.is_dir()][0]

        return extracted

    async def get_latest_commit(self, owner: str, name: str, branch: str = "main") -> dict:
        """Get the latest commit SHA for a branch."""
        repo = self.client.get_repo(f"{owner}/{name}")
        commit = repo.get_commit(branch)

        return {
            "sha": commit.sha,
            "message": commit.commit.message,
            "author": commit.commit.author.name,
            "date": commit.commit.author.date.isoformat(),
        }

    async def get_changed_files(
        self, owner: str, name: str, base_sha: str, head_sha: str
    ) -> dict:
        """
        Get files changed between two commits.

        Returns:
            {
                "added": [...],
                "modified": [...],
                "removed": [...]
            }
        """
        repo = self.client.get_repo(f"{owner}/{name}")
        comparison = repo.compare(base_sha, head_sha)

        changes = {"added": [], "modified": [], "removed": []}

        for file in comparison.files:
            if file.status == "added":
                changes["added"].append(file.filename)
            elif file.status == "modified":
                changes["modified"].append(file.filename)
            elif file.status == "removed":
                changes["removed"].append(file.filename)

        return changes

    async def get_file_content(self, owner: str, name: str, file_path: str, branch: str = "main") -> str:
        """Get content of a single file."""
        url = f"https://api.github.com/repos/{owner}/{name}/contents/{file_path}?ref={branch}"

        response = await self.http_client.get(url)
        response.raise_for_status()

        data = response.json()

        # Decode base64 content
        import base64

        content = base64.b64decode(data["content"]).decode("utf-8")
        return content

    async def cleanup_temp_repo(self, repo_path: Path) -> None:
        """Remove temporary repository directory."""
        if repo_path.exists():
            shutil.rmtree(repo_path.parent)  # Remove parent temp dir

    async def close(self) -> None:
        """Close HTTP client."""
        await self.http_client.aclose()
