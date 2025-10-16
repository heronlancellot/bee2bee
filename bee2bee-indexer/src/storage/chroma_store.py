"""
ChromaDB storage layer with multi-tenant support.
"""
from datetime import datetime
from typing import List, Optional
import chromadb
from chromadb.config import Settings

from ..core.types import CodeChunk, SearchResult, RepoMetadata


class ChromaStore:
    """ChromaDB storage with dual embeddings."""

    def __init__(self, path: str, embedder):
        self.embedder = embedder

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=False,
            ),
        )

    async def store_chunks(
        self,
        chunks: List[CodeChunk],
        repo: str,
        user_id: str,
        branch: str = "main",
    ) -> None:
        """
        Store chunks in ChromaDB with dual embeddings.

        Args:
            chunks: List of code chunks
            repo: Repository name (owner/name)
            user_id: User who triggered indexing
            branch: Git branch
        """
        if not chunks:
            return

        # Collection name: github_owner_repo_main
        collection_name = self._get_collection_name(repo, branch)

        # Get or create collection
        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "repo": repo,
                "branch": branch,
                "indexed_by_users": [user_id],
                "total_chunks": 0,
                "last_updated": datetime.now().isoformat(),
            },
        )

        # Generate embeddings in batches
        batch_size = 50  # Adjust based on memory
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            print(f"Generating embeddings for batch {i // batch_size + 1}...")

            # Prepare data for embedding
            chunk_dicts = [
                {
                    "code": chunk.code,
                    "name": chunk.name,
                    "chunk_type": chunk.chunk_type,
                    "signature": chunk.signature,
                    "docstring": chunk.docstring,
                    "file_path": chunk.file_path,
                    "module": chunk.module,
                }
                for chunk in batch
            ]

            # Generate dual embeddings
            embeddings = self.embedder.embed_batch(chunk_dicts)

            # Prepare for ChromaDB
            ids = [chunk.id for chunk in batch]
            nlp_embeddings = [emb[0] for emb in embeddings]
            code_embeddings = [emb[1] for emb in embeddings]

            # Metadata
            metadatas = [chunk.model_dump(exclude={"code"}) for chunk in batch]

            # Add to collection
            # ChromaDB doesn't support named vectors natively yet
            # Workaround: Store code in metadata, use composite embedding
            # For now, we'll use NLP embeddings as primary
            collection.add(
                ids=ids,
                embeddings=nlp_embeddings,  # Primary search
                documents=[chunk.code for chunk in batch],
                metadatas=metadatas,
            )

        # Update metadata
        collection.modify(
            metadata={
                "repo": repo,
                "branch": branch,
                "indexed_by_users": [user_id],
                "total_chunks": len(chunks),
                "last_updated": datetime.now().isoformat(),
            }
        )

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
            repos: List of repo names
            user_id: User making the query
            n_results: Results per repo

        Returns:
            Ranked search results
        """
        all_results = []

        # Generate query embedding
        nlp_emb, code_emb = self.embedder.embed_query(query)

        for repo in repos:
            collection_name = self._get_collection_name(repo, "main")

            try:
                collection = self.client.get_collection(collection_name)
            except Exception:
                # Collection doesn't exist
                continue

            # Check user access
            metadata = collection.metadata
            if user_id not in metadata.get("indexed_by_users", []):
                continue

            # Search
            results = collection.query(
                query_embeddings=[nlp_emb],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )

            # Convert to SearchResult objects
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                # Reconstruct CodeChunk
                chunk = CodeChunk(
                    id=meta["id"],
                    code=doc,
                    repo=meta["repo"],
                    file_path=meta["file_path"],
                    language=meta["language"],
                    chunk_type=meta["chunk_type"],
                    name=meta["name"],
                    signature=meta.get("signature"),
                    docstring=meta.get("docstring"),
                    start_line=meta["start_line"],
                    end_line=meta["end_line"],
                    start_byte=meta["start_byte"],
                    end_byte=meta["end_byte"],
                    lines_of_code=meta["lines_of_code"],
                    parent_class=meta.get("parent_class"),
                    module=meta.get("module"),
                    imports=meta.get("imports", []),
                    complexity=meta.get("complexity"),
                )

                # Convert distance to similarity score
                score = 1.0 / (1.0 + dist)

                all_results.append(
                    SearchResult(
                        chunk=chunk,
                        score=score,
                        distance=dist,
                        file_url=f"https://github.com/{repo}/blob/main/{meta['file_path']}#L{meta['start_line']}-L{meta['end_line']}",
                    )
                )

        # Sort by score
        all_results.sort(key=lambda x: x.score, reverse=True)

        return all_results[:n_results]

    async def collection_exists(self, repo: str, branch: str = "main") -> bool:
        """Check if a repo is already indexed."""
        collection_name = self._get_collection_name(repo, branch)

        try:
            self.client.get_collection(collection_name)
            return True
        except Exception:
            return False

    async def add_user_to_repo(self, repo: str, user_id: str, branch: str = "main") -> None:
        """Add a user to the indexed_by_users list."""
        collection_name = self._get_collection_name(repo, branch)

        try:
            collection = self.client.get_collection(collection_name)
            metadata = collection.metadata

            users = metadata.get("indexed_by_users", [])
            if user_id not in users:
                users.append(user_id)

                collection.modify(metadata={**metadata, "indexed_by_users": users})
        except Exception:
            pass

    async def get_chunk_count(self, repo: str, branch: str = "main") -> int:
        """Get number of chunks indexed for a repo."""
        collection_name = self._get_collection_name(repo, branch)

        try:
            collection = self.client.get_collection(collection_name)
            return collection.metadata.get("total_chunks", 0)
        except Exception:
            return 0

    def _get_collection_name(self, repo: str, branch: str) -> str:
        """Generate collection name from repo and branch."""
        # github_owner_repo_main
        return f"github_{repo.replace('/', '_')}_{branch}"
