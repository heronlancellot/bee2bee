"""
Main indexer orchestrator.
Coordinates parsing, chunking, embedding, and storage.
"""
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from tqdm import tqdm

from .types import CodeChunk, RepoMetadata, SearchResult, IndexingJob
from .config import get_config
from ..gh_client.client import GitHubClient
from ..parsers.tree_sitter_parser import TreeSitterParser
from ..chunkers.function_chunker import FunctionChunker
from ..embeddings.dual_embedder import DualEmbedder
from ..storage.chroma_store import ChromaStore


class RepoIndexer:
    """
    Main class for indexing GitHub repositories.

    Architecture:
    1. Clone/download repo via GitHub API
    2. Parse files with Tree-sitter
    3. Chunk code by functions/classes
    4. Generate dual embeddings (NLP + Code)
    5. Store in ChromaDB
    6. Support incremental updates
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config or get_config()

        # Initialize components
        self.github_client = GitHubClient(self.config.github_token)
        self.parser = TreeSitterParser()
        self.chunker = FunctionChunker()
        self.embedder = DualEmbedder(
            provider=self.config.embedding_provider,
            nlp_model=self.config.embedding_model,
            code_model=self.config.code_embedding_model,
            openai_api_key=self.config.openai_api_key,
        )
        self.storage = ChromaStore(
            path=self.config.chromadb_path,
            embedder=self.embedder,
        )

        # Job tracking
        self.active_jobs: Dict[str, IndexingJob] = {}

    async def index_repository(
        self,
        repo_url: str,
        user_id: str,
        branch: str = "main",
        incremental: bool = False,
    ) -> IndexingJob:
        """
        Index a GitHub repository.

        Args:
            repo_url: GitHub URL (https://github.com/owner/repo)
            user_id: User requesting the indexing
            branch: Git branch to index
            incremental: If True, only update changed files

        Returns:
            IndexingJob with job_id to track progress
        """
        # Parse repo info
        owner, repo_name = self._parse_repo_url(repo_url)
        repo_full_name = f"{owner}/{repo_name}"

        # Check if already indexed
        if not incremental:
            existing = await self._check_existing_index(repo_full_name, user_id)
            if existing:
                return existing

        # Create job
        job = IndexingJob(
            job_id=str(uuid.uuid4()),
            repo=repo_full_name,
            status="pending",
            triggered_by=user_id,
            incremental=incremental,
        )
        self.active_jobs[job.job_id] = job

        # Run indexing in background
        asyncio.create_task(self._run_indexing_job(job, owner, repo_name, branch, user_id))

        return job

    async def _run_indexing_job(
        self,
        job: IndexingJob,
        owner: str,
        repo_name: str,
        branch: str,
        user_id: str,
    ) -> None:
        """Execute the indexing job."""
        try:
            job.status = "running"
            job.started_at = datetime.now()

            repo_full_name = f"{owner}/{repo_name}"

            # Step 1: Download repository
            print(f"📥 Downloading {repo_full_name}...")
            repo_path = await self.github_client.download_repo(owner, repo_name, branch)

            # Step 2: Get file list
            files = list(Path(repo_path).rglob("*"))
            code_files = [f for f in files if self._is_code_file(f)]

            print(f"📂 Found {len(code_files)} code files")
            job.files_processed = 0

            # Step 3: Parse and chunk all files
            all_chunks: List[CodeChunk] = []

            for file_path in tqdm(code_files, desc="Processing files"):
                try:
                    chunks = await self._process_file(
                        file_path, repo_path, repo_full_name, branch
                    )
                    all_chunks.extend(chunks)
                    job.files_processed += 1
                    job.progress = (job.files_processed / len(code_files)) * 0.7  # 70% for parsing
                except Exception as e:
                    job.errors.append(f"Error processing {file_path}: {str(e)}")
                    continue

            print(f"✂️  Created {len(all_chunks)} code chunks")

            # Step 4: Store in ChromaDB (with embeddings)
            print(f"💾 Storing embeddings in ChromaDB...")
            await self.storage.store_chunks(
                chunks=all_chunks,
                repo=repo_full_name,
                user_id=user_id,
                branch=branch,
            )

            job.chunks_indexed = len(all_chunks)
            job.progress = 1.0
            job.status = "completed"
            job.completed_at = datetime.now()

            print(f"✅ Indexing complete! {len(all_chunks)} chunks indexed")

        except Exception as e:
            job.status = "failed"
            job.errors.append(str(e))
            job.completed_at = datetime.now()
            print(f"❌ Indexing failed: {str(e)}")

        finally:
            # Cleanup temp files
            await self.github_client.cleanup_temp_repo(repo_path)

    async def _process_file(
        self,
        file_path: Path,
        repo_root: str,
        repo_full_name: str,
        branch: str,
    ) -> List[CodeChunk]:
        """Parse a single file and extract chunks."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return []

        # Check file size
        if len(content) > self.config.max_file_size_mb * 1024 * 1024:
            return []

        # Relative path from repo root
        rel_path = str(file_path.relative_to(repo_root))

        # Parse with tree-sitter
        tree = self.parser.parse(content, file_path.suffix)
        if not tree:
            return []

        # Extract chunks
        chunks = self.chunker.extract_chunks(
            tree=tree,
            content=content,
            repo=repo_full_name,
            file_path=rel_path,
            language=self.parser.get_language(file_path.suffix),
        )

        return chunks

    async def search(
        self,
        query: str,
        repos: List[str],
        user_id: str,
        n_results: int = 10,
    ) -> List[SearchResult]:
        """
        Search across multiple repositories.

        Args:
            query: Natural language or code query
            repos: List of repo names (owner/name)
            user_id: User making the query
            n_results: Number of results per repo

        Returns:
            List of SearchResults ranked by similarity
        """
        return await self.storage.search(
            query=query,
            repos=repos,
            user_id=user_id,
            n_results=n_results,
        )

    async def get_job_status(self, job_id: str) -> Optional[IndexingJob]:
        """Get the status of an indexing job."""
        return self.active_jobs.get(job_id)

    async def _check_existing_index(self, repo: str, user_id: str) -> Optional[IndexingJob]:
        """Check if repo is already indexed."""
        exists = await self.storage.collection_exists(repo)
        if exists:
            # Add user to indexed_by_users
            await self.storage.add_user_to_repo(repo, user_id)

            # Return fake "completed" job
            return IndexingJob(
                job_id="cached",
                repo=repo,
                status="completed",
                progress=1.0,
                triggered_by=user_id,
                chunks_indexed=await self.storage.get_chunk_count(repo),
            )
        return None

    def _parse_repo_url(self, url: str) -> tuple[str, str]:
        """Parse GitHub URL into (owner, repo)."""
        # https://github.com/owner/repo -> (owner, repo)
        parts = url.rstrip("/").split("/")
        return parts[-2], parts[-1]

    def _is_code_file(self, file_path: Path) -> bool:
        """Check if file is a code file we should index."""
        code_extensions = {
            ".py", ".js", ".ts", ".tsx", ".jsx",
            ".rs", ".go", ".java", ".cpp", ".c", ".h",
            ".rb", ".php", ".swift", ".kt", ".scala",
        }
        return file_path.suffix in code_extensions and file_path.is_file()
