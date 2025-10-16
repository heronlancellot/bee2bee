"""
Configuration management for the indexer.
"""
import os
from pathlib import Path
from typing import Literal, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class IndexerConfig(BaseSettings):
    """Configuration for the Bee2Bee Indexer."""

    # GitHub
    github_token: str = Field(..., env="GITHUB_TOKEN")

    # OpenAI (optional)
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")

    # ChromaDB
    chromadb_path: str = Field("./chromadb_data", env="CHROMADB_PATH")
    chromadb_host: str = Field("localhost", env="CHROMADB_HOST")
    chromadb_port: int = Field(8000, env="CHROMADB_PORT")

    # Embeddings
    embedding_provider: Literal["local", "openai"] = Field("local", env="EMBEDDING_PROVIDER")
    embedding_model: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL"
    )
    code_embedding_model: str = Field(
        "jinaai/jina-embeddings-v2-base-code", env="CODE_EMBEDDING_MODEL"
    )

    # Indexing
    chunk_strategy: Literal["symbols", "lines"] = Field("symbols", env="CHUNK_STRATEGY")
    batch_size: int = Field(100, env="BATCH_SIZE")
    max_file_size_mb: int = Field(5, env="MAX_FILE_SIZE_MB")

    # Cache
    cache_dir: str = Field("./.cache", env="CACHE_DIR")
    cache_ttl_hours: int = Field(24, env="CACHE_TTL_HOURS")

    # Temp directories
    temp_repo_dir: str = Field("./temp_repos", env="TEMP_REPO_DIR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        Path(self.chromadb_path).mkdir(parents=True, exist_ok=True)
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        Path(self.temp_repo_dir).mkdir(parents=True, exist_ok=True)


# Global config instance
_config: Optional[IndexerConfig] = None


def get_config() -> IndexerConfig:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = IndexerConfig()
        _config.ensure_directories()
    return _config


def reset_config() -> None:
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None
