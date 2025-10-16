"""
Bee2Bee Indexer - Code indexing library for AI agents.
"""
from .core.indexer import RepoIndexer
from .core.types import CodeChunk, SearchResult, IndexingJob
from .core.config import IndexerConfig, get_config

__version__ = "0.1.0"

__all__ = [
    "RepoIndexer",
    "CodeChunk",
    "SearchResult",
    "IndexingJob",
    "IndexerConfig",
    "get_config",
]
