"""
Core types and data models for the indexer.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ChunkType(str, Enum):
    """Type of code chunk."""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    COMMENT = "comment"
    FILE = "file"


class Language(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    GO = "go"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    UNKNOWN = "unknown"


class CodeChunk(BaseModel):
    """Represents a chunk of code (function, class, etc)."""

    id: str = Field(..., description="Unique identifier for the chunk")
    code: str = Field(..., description="The actual code content")

    # Metadata
    repo: str = Field(..., description="Repository full name (owner/name)")
    file_path: str = Field(..., description="Path to file within repo")
    language: Language = Field(..., description="Programming language")
    chunk_type: ChunkType = Field(..., description="Type of code chunk")

    # Code structure
    name: str = Field(..., description="Function/class name")
    signature: Optional[str] = Field(None, description="Function signature")
    docstring: Optional[str] = Field(None, description="Documentation string")

    # Location
    start_line: int = Field(..., description="Starting line number")
    end_line: int = Field(..., description="Ending line number")
    start_byte: int = Field(..., description="Starting byte offset")
    end_byte: int = Field(..., description="Ending byte offset")

    # Context
    parent_class: Optional[str] = Field(None, description="Parent class if method")
    module: Optional[str] = Field(None, description="Module name")
    imports: List[str] = Field(default_factory=list, description="Import statements")

    # Metrics
    complexity: Optional[int] = Field(None, description="Cyclomatic complexity")
    lines_of_code: int = Field(..., description="Number of lines")

    class Config:
        use_enum_values = True


class RepoMetadata(BaseModel):
    """Metadata about an indexed repository."""

    repo_full_name: str = Field(..., description="owner/name")
    branch: str = Field(default="main", description="Git branch")
    commit_sha: str = Field(..., description="Latest commit SHA")

    # Stats
    total_files: int = Field(..., description="Number of files indexed")
    total_chunks: int = Field(..., description="Number of chunks created")
    languages: List[Language] = Field(..., description="Languages detected")

    # Timestamps
    indexed_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

    # Multi-tenant
    indexed_by_users: List[str] = Field(default_factory=list, description="User IDs with access")

    class Config:
        use_enum_values = True


class SearchResult(BaseModel):
    """Result from semantic search."""

    chunk: CodeChunk
    score: float = Field(..., description="Similarity score (0-1)")
    distance: float = Field(..., description="Vector distance")

    # Context
    surrounding_code: Optional[str] = Field(None, description="Code around the match")
    file_url: Optional[str] = Field(None, description="GitHub URL to file")


class IndexingJob(BaseModel):
    """Represents an indexing job."""

    job_id: str
    repo: str
    status: str = Field(..., description="pending, running, completed, failed")
    progress: float = Field(default=0.0, description="Progress percentage")

    # Results
    chunks_indexed: int = Field(default=0)
    files_processed: int = Field(default=0)
    errors: List[str] = Field(default_factory=list)

    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Metadata
    triggered_by: str = Field(..., description="User ID or 'webhook'")
    incremental: bool = Field(default=False, description="Is incremental update")
