"""
Basic usage example for Bee2Bee Indexer.

This example shows how to:
1. Initialize the indexer
2. Index a GitHub repository
3. Search for code
4. Handle results
"""
import asyncio
from bee2bee_indexer.core.indexer import RepoIndexer


async def main():
    print("🐝 Bee2Bee Indexer - Basic Usage Example\n")

    # Initialize indexer (reads from .env)
    indexer = RepoIndexer()

    # ==============================================
    # Example 1: Index a repository
    # ==============================================
    print("📚 Example 1: Indexing a repository\n")

    repo_url = "https://github.com/fastapi/fastapi"
    user_id = "user_123"

    print(f"Starting indexing job for: {repo_url}")
    job = await indexer.index_repository(
        repo_url=repo_url, user_id=user_id, branch="main", incremental=False
    )

    print(f"Job ID: {job.job_id}")
    print(f"Status: {job.status}\n")

    # Poll for job completion
    while job.status == "running" or job.status == "pending":
        await asyncio.sleep(2)
        job = await indexer.get_job_status(job.job_id)
        print(f"Progress: {job.progress * 100:.1f}% - Files: {job.files_processed}")

    if job.status == "completed":
        print(f"\n✅ Indexing complete!")
        print(f"   Chunks indexed: {job.chunks_indexed}")
        print(f"   Files processed: {job.files_processed}")
    else:
        print(f"\n❌ Indexing failed!")
        print(f"   Errors: {job.errors}")
        return

    # ==============================================
    # Example 2: Search for code
    # ==============================================
    print("\n\n🔍 Example 2: Searching for code\n")

    queries = [
        "How to create a FastAPI endpoint with path parameters?",
        "async function that handles websocket connections",
        "dependency injection in FastAPI",
    ]

    for query in queries:
        print(f"\n💬 Query: {query}")
        print("─" * 60)

        results = await indexer.search(
            query=query, repos=["fastapi/fastapi"], user_id=user_id, n_results=3
        )

        if not results:
            print("   No results found")
            continue

        for i, result in enumerate(results, 1):
            chunk = result.chunk
            print(f"\n   Result {i} (score: {result.score:.3f})")
            print(f"   📄 File: {chunk.file_path}")
            print(f"   🔧 {chunk.chunk_type}: {chunk.name}")
            print(f"   📍 Lines: {chunk.start_line}-{chunk.end_line}")
            print(f"   🌐 Language: {chunk.language}")

            # Show code preview (first 5 lines)
            code_lines = chunk.code.split("\n")[:5]
            print(f"\n   Code preview:")
            for line in code_lines:
                print(f"      {line}")
            if len(chunk.code.split("\n")) > 5:
                print(f"      ... ({len(chunk.code.split('\n')) - 5} more lines)")

    # ==============================================
    # Example 3: Multi-repo search
    # ==============================================
    print("\n\n🌐 Example 3: Search across multiple repositories\n")

    # First, index another repo
    print("Adding another repository...")
    job2 = await indexer.index_repository(
        repo_url="https://github.com/tiangolo/sqlmodel", user_id=user_id
    )

    # Wait for completion (simplified for example)
    while job2.status in ["running", "pending"]:
        await asyncio.sleep(2)
        job2 = await indexer.get_job_status(job2.job_id)

    if job2.status == "completed":
        print(f"✅ Second repo indexed: {job2.chunks_indexed} chunks\n")

        # Search across both repos
        query = "database models with relationships"
        print(f"💬 Query: {query}")
        print("─" * 60)

        results = await indexer.search(
            query=query,
            repos=["fastapi/fastapi", "tiangolo/sqlmodel"],
            user_id=user_id,
            n_results=5,
        )

        for i, result in enumerate(results, 1):
            chunk = result.chunk
            print(f"\n   Result {i} from {chunk.repo}")
            print(f"   📄 {chunk.file_path} - {chunk.chunk_type}: {chunk.name}")
            print(f"   📊 Score: {result.score:.3f}")

    print("\n\n🎉 Done!")


if __name__ == "__main__":
    asyncio.run(main())
