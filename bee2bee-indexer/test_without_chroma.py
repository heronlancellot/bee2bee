"""
Test the indexer pipeline WITHOUT ChromaDB.
Tests: GitHub download → Parse → Chunk → Embed
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from gh_client.client import GitHubClient
from parsers.tree_sitter_parser import TreeSitterParser
from chunkers.function_chunker import FunctionChunker
from embeddings.dual_embedder import DualEmbedder
from core.types import Language


async def main():
    print("🐝 Bee2Bee Indexer - Partial Test (No ChromaDB)")
    print("=" * 70)
    print()

    # Load env
    from dotenv import load_dotenv
    load_dotenv()

    github_token = os.getenv("GITHUB_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    provider = os.getenv("EMBEDDING_PROVIDER", "local")

    if not github_token:
        print("❌ GITHUB_TOKEN not found in .env!")
        return

    print(f"✅ GitHub token loaded")
    print(f"✅ Embedding provider: {provider}")
    print()

    # ==============================================
    # TEST 1: GitHub Client - Download Repo
    # ==============================================
    print("=" * 70)
    print("TEST 1: GitHub Client - Download Repository")
    print("=" * 70)

    try:
        github_client = GitHubClient(github_token)
        print("✅ GitHub client initialized")

        # Download a small repo
        owner = "heronlancellot"
        repo_name = "bee2bee"
        branch = "dev"

        print(f"\n📥 Downloading {owner}/{repo_name} (branch: {branch})...")
        print("   (This might take a minute for first download)")

        repo_path = await github_client.download_repo(owner, repo_name, branch)

        print(f"✅ Downloaded to: {repo_path}")

        # List files (Python, JS, TS, TSX)
        py_files = list(Path(repo_path).rglob("*.py"))
        js_files = list(Path(repo_path).rglob("*.js"))
        ts_files = list(Path(repo_path).rglob("*.ts"))
        tsx_files = list(Path(repo_path).rglob("*.tsx"))

        files = py_files + js_files + ts_files + tsx_files

        print(f"✅ Found {len(py_files)} Python, {len(js_files)} JS, {len(ts_files)} TS, {len(tsx_files)} TSX files")
        print(f"   Total: {len(files)} files")

        if files:
            print(f"\n   Sample files:")
            for f in files[:5]:
                rel_path = f.relative_to(repo_path)
                print(f"   - {rel_path}")

    except Exception as e:
        print(f"❌ GitHub client failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # ==============================================
    # TEST 2: Tree-sitter Parser
    # ==============================================
    print("\n" + "=" * 70)
    print("TEST 2: Tree-sitter Parser - Parse Code")
    print("=" * 70)

    try:
        parser = TreeSitterParser()
        print("✅ Tree-sitter parser initialized")

        # Pick a test file
        test_file = [f for f in files if "api" in str(f).lower() or "session" in str(f).lower()]
        if not test_file:
            test_file = [files[0]]

        test_file = test_file[0]

        print(f"\n📄 Parsing: {test_file.relative_to(repo_path)}")

        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()

        print(f"   File size: {len(content)} bytes")

        # Detect language
        suffix = test_file.suffix.lower()
        lang_map = {
            ".py": Language.PYTHON,
            ".js": Language.JAVASCRIPT,
            ".ts": Language.TYPESCRIPT,
            ".tsx": Language.TYPESCRIPT,
        }
        test_language = lang_map.get(suffix, Language.PYTHON)
        print(f"   Language: {test_language}")

        # Parse
        tree = parser.parse(content, test_file.suffix)

        if tree:
            print(f"✅ Parsed successfully!")
            print(f"   Root node type: {tree.root_node.type}")
            print(f"   Root node children: {tree.root_node.child_count}")

            # Find functions
            functions = parser.get_functions(tree)
            classes = parser.get_classes(tree)

            print(f"\n   Found {len(functions)} functions")
            print(f"   Found {len(classes)} classes")

            if functions:
                print(f"\n   Sample functions:")
                for func in functions[:3]:
                    name = parser.get_node_name(func)
                    print(f"   - {name} (lines {func.start_point.row}-{func.end_point.row})")

        else:
            print("❌ Failed to parse")
            return

    except Exception as e:
        print(f"❌ Parser failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # ==============================================
    # TEST 3: Function Chunker
    # ==============================================
    print("\n" + "=" * 70)
    print("TEST 3: Function Chunker - Extract Chunks")
    print("=" * 70)

    try:
        chunker = FunctionChunker()
        print("✅ Function chunker initialized")

        # Extract chunks from the parsed file
        chunks = chunker.extract_chunks(
            tree=tree,
            content=content,
            repo=f"{owner}/{repo_name}",
            file_path=str(test_file.relative_to(repo_path)),
            language=test_language,
        )

        print(f"\n✅ Extracted {len(chunks)} chunks")

        if chunks:
            print(f"\n   Sample chunks:")
            for chunk in chunks[:3]:
                print(f"\n   Chunk: {chunk.name}")
                print(f"   - Type: {chunk.chunk_type}")
                print(f"   - Lines: {chunk.start_line}-{chunk.end_line} ({chunk.lines_of_code} LOC)")
                if chunk.signature:
                    print(f"   - Signature: {chunk.signature[:60]}...")
                if chunk.docstring:
                    print(f"   - Docstring: {chunk.docstring[:60]}...")

    except Exception as e:
        print(f"❌ Chunker failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # ==============================================
    # TEST 4: Dual Embedder
    # ==============================================
    print("\n" + "=" * 70)
    print("TEST 4: Dual Embedder - Generate Embeddings")
    print("=" * 70)

    try:
        # Use correct models based on provider
        if provider == "openai":
            nlp_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
            code_model = nlp_model  # OpenAI uses same model for both
        else:
            nlp_model = "sentence-transformers/all-MiniLM-L6-v2"
            code_model = "jinaai/jina-embeddings-v2-base-code"

        embedder = DualEmbedder(
            provider=provider,
            nlp_model=nlp_model,
            code_model=code_model,
            openai_api_key=openai_key,
        )
        print(f"✅ Dual embedder initialized (provider: {provider})")

        # Get embedding dimensions
        nlp_dim, code_dim = embedder.get_dimensions()
        print(f"   NLP embedding dim: {nlp_dim}")
        print(f"   Code embedding dim: {code_dim}")

        # Test with first chunk
        if chunks:
            test_chunk = chunks[0]

            print(f"\n🧪 Testing with chunk: {test_chunk.name}")

            # Prepare chunk dict
            chunk_dict = {
                "code": test_chunk.code,
                "name": test_chunk.name,
                "chunk_type": test_chunk.chunk_type,
                "signature": test_chunk.signature,
                "docstring": test_chunk.docstring,
                "file_path": test_chunk.file_path,
                "module": test_chunk.module,
            }

            print(f"   Generating embeddings...")

            # Generate embeddings
            embeddings = embedder.embed_batch([chunk_dict])

            nlp_emb, code_emb = embeddings[0]

            print(f"✅ Embeddings generated!")
            print(f"   NLP embedding: [{nlp_emb[0]:.4f}, {nlp_emb[1]:.4f}, ..., {nlp_emb[-1]:.4f}] (len={len(nlp_emb)})")
            print(f"   Code embedding: [{code_emb[0]:.4f}, {code_emb[1]:.4f}, ..., {code_emb[-1]:.4f}] (len={len(code_emb)})")

            # Test query embedding
            print(f"\n🔍 Testing query embedding...")
            query = "function that makes HTTP requests"
            query_nlp, query_code = embedder.embed_query(query)

            print(f"✅ Query embeddings generated!")
            print(f"   Query: '{query}'")
            print(f"   NLP: [{query_nlp[0]:.4f}, {query_nlp[1]:.4f}, ...] (len={len(query_nlp)})")
            print(f"   Code: [{query_code[0]:.4f}, {query_code[1]:.4f}, ...] (len={len(query_code)})")

    except Exception as e:
        print(f"❌ Embedder failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # ==============================================
    # TEST 5: Process Multiple Files
    # ==============================================
    print("\n" + "=" * 70)
    print("TEST 5: Full Pipeline - Process Multiple Files")
    print("=" * 70)

    try:
        print(f"\n🔄 Processing first 5 files...")

        all_chunks = []

        for i, file in enumerate(files[:5], 1):
            print(f"\n   [{i}/5] {file.relative_to(repo_path)}")

            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Detect language
                suffix = file.suffix.lower()
                lang_map = {
                    ".py": Language.PYTHON,
                    ".js": Language.JAVASCRIPT,
                    ".ts": Language.TYPESCRIPT,
                    ".tsx": Language.TYPESCRIPT,
                }
                language = lang_map.get(suffix, Language.PYTHON)

                # Parse
                tree = parser.parse(content, file.suffix)
                if not tree:
                    print(f"       ⚠️  Could not parse")
                    continue

                # Chunk
                chunks = chunker.extract_chunks(
                    tree=tree,
                    content=content,
                    repo=f"{owner}/{repo_name}",
                    file_path=str(file.relative_to(repo_path)),
                    language=language,
                )

                print(f"       ✅ Extracted {len(chunks)} chunks")
                all_chunks.extend(chunks)

            except Exception as e:
                print(f"       ❌ Error: {e}")
                continue

        print(f"\n✅ Total chunks from 5 files: {len(all_chunks)}")

        if all_chunks:
            print(f"\n   Generating embeddings for all chunks...")
            chunk_dicts = [
                {
                    "code": c.code,
                    "name": c.name,
                    "chunk_type": c.chunk_type,
                    "signature": c.signature,
                    "docstring": c.docstring,
                    "file_path": c.file_path,
                    "module": c.module,
                }
                for c in all_chunks
            ]

            embeddings = embedder.embed_batch(chunk_dicts)

            print(f"✅ Generated {len(embeddings)} embeddings!")
            print(f"   Average NLP dim: {nlp_dim}")
            print(f"   Average Code dim: {code_dim}")

    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # ==============================================
    # CLEANUP
    # ==============================================
    print("\n" + "=" * 70)
    print("🧹 Cleanup")
    print("=" * 70)

    try:
        await github_client.cleanup_temp_repo(repo_path)
        await github_client.close()
        print("✅ Temp files cleaned up")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

    # ==============================================
    # SUMMARY
    # ==============================================
    print("\n" + "=" * 70)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 70)
    print()
    print("✅ GitHub Client: Working")
    print("✅ Tree-sitter Parser: Working")
    print("✅ Function Chunker: Working")
    print("✅ Dual Embedder: Working")
    print("✅ Full Pipeline: Working")
    print()
    print("📝 Next steps:")
    print("   1. Install and start ChromaDB")
    print("   2. Test full indexing with storage")
    print("   3. Test search functionality")
    print()


if __name__ == "__main__":
    asyncio.run(main())
