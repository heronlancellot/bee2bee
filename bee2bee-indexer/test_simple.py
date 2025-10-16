"""
Simple test without relative imports.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Now import as absolute
from dotenv import load_dotenv

# Load environment
load_dotenv()


async def test_github_download():
    """Test GitHub client."""
    print("=" * 70)
    print("TEST 1: GitHub Download")
    print("=" * 70)

    from gh_client.client import GitHubClient

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN not set!")
        return None

    print("✅ GitHub token loaded")

    client = GitHubClient(token)
    print("✅ Client initialized")

    # Download bee2bee repo - você pode mudar a branch aqui!
    branch = "dev"  # ou "main", "feature/algo", etc
    print(f"\n📥 Downloading heronlancellot/bee2bee (branch: {branch})...")
    repo_path = await client.download_repo("heronlancellot", "bee2bee", branch)

    print(f"✅ Downloaded to: {repo_path}")

    # Count code files (Python, JS, TS)
    py_files = list(Path(repo_path).rglob("*.py"))
    js_files = list(Path(repo_path).rglob("*.js"))
    ts_files = list(Path(repo_path).rglob("*.ts"))
    tsx_files = list(Path(repo_path).rglob("*.tsx"))

    files = py_files + js_files + ts_files + tsx_files

    print(f"✅ Found {len(files)} code files")
    print(f"   Python: {len(py_files)}, JS: {len(js_files)}, TS: {len(ts_files)}, TSX: {len(tsx_files)}")

    if files:
        print(f"\n   Sample files:")
        for f in files[:5]:
            print(f"   - {f.relative_to(repo_path)}")
    else:
        print("❌ No code files found!")
        return None

    return repo_path, files, client


async def test_parser(files):
    """Test tree-sitter parser."""
    print("\n" + "=" * 70)
    print("TEST 2: Tree-sitter Parser")
    print("=" * 70)

    from parsers.tree_sitter_parser import TreeSitterParser

    parser = TreeSitterParser()
    print("✅ Parser initialized")

    # Pick a file
    test_file = [f for f in files if "session" in str(f).lower() or "api" in str(f).lower()]
    if not test_file:
        test_file = [files[0]]

    test_file = test_file[0]
    print(f"\n📄 Parsing: {test_file.name}")

    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()

    tree = parser.parse(content, test_file.suffix)

    if tree:
        print(f"✅ Parsed!")
        functions = parser.get_functions(tree)
        classes = parser.get_classes(tree)
        print(f"   Functions: {len(functions)}")
        print(f"   Classes: {len(classes)}")

        if functions:
            print(f"\n   Sample functions:")
            for func in functions[:3]:
                name = parser.get_node_name(func)
                print(f"   - {name}")

        return tree, content, test_file
    else:
        print("❌ Parse failed")
        return None, None, None


async def test_chunker(tree, content, file_path, repo_path):
    """Test chunker."""
    print("\n" + "=" * 70)
    print("TEST 3: Function Chunker")
    print("=" * 70)

    from chunkers.function_chunker import FunctionChunker
    from parsers.tree_sitter_parser import TreeSitterParser
    from core.types import Language

    chunker = FunctionChunker()
    parser = TreeSitterParser()
    print("✅ Chunker initialized")

    # Detect language from file extension
    language = parser.get_language(file_path.suffix)

    chunks = chunker.extract_chunks(
        tree=tree,
        content=content,
        repo="heronlancellot/bee2bee",
        file_path=str(file_path.relative_to(repo_path)),
        language=language,
    )

    print(f"\n✅ Extracted {len(chunks)} chunks")

    if chunks:
        print(f"\n   Sample chunks:")
        for chunk in chunks[:3]:
            print(f"\n   - {chunk.name} ({chunk.chunk_type})")
            print(f"     Lines: {chunk.start_line}-{chunk.end_line}")
            if chunk.signature:
                print(f"     Sig: {chunk.signature[:50]}...")

    return chunks


async def test_embedder(chunks):
    """Test embeddings."""
    print("\n" + "=" * 70)
    print("TEST 4: Dual Embedder")
    print("=" * 70)

    from embeddings.dual_embedder import DualEmbedder

    provider = os.getenv("EMBEDDING_PROVIDER", "local")
    openai_key = os.getenv("OPENAI_API_KEY")

    print(f"   Provider: {provider}")

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

    print("✅ Embedder initialized")

    nlp_dim, code_dim = embedder.get_dimensions()
    print(f"   NLP dim: {nlp_dim}, Code dim: {code_dim}")

    if chunks:
        print(f"\n🧪 Embedding first chunk: {chunks[0].name}")

        chunk_dict = {
            "code": chunks[0].code,
            "name": chunks[0].name,
            "chunk_type": chunks[0].chunk_type,
            "signature": chunks[0].signature,
            "docstring": chunks[0].docstring,
            "file_path": chunks[0].file_path,
            "module": chunks[0].module,
        }

        embeddings = embedder.embed_batch([chunk_dict])
        nlp_emb, code_emb = embeddings[0]

        print(f"✅ Generated embeddings!")
        print(f"   NLP: [{nlp_emb[0]:.4f}, {nlp_emb[1]:.4f}, ...] (len={len(nlp_emb)})")
        print(f"   Code: [{code_emb[0]:.4f}, {code_emb[1]:.4f}, ...] (len={len(code_emb)})")


async def main():
    print("🐝 Bee2Bee Indexer - Simple Test")
    print("=" * 70)
    print()

    try:
        # Test 1: GitHub
        result = await test_github_download()
        if not result:
            return

        repo_path, files, client = result

        # Test 2: Parser
        tree, content, test_file = await test_parser(files)
        if not tree:
            return

        # Test 3: Chunker
        chunks = await test_chunker(tree, content, test_file, repo_path)

        # Test 4: Embedder
        await test_embedder(chunks)

        # Cleanup
        print("\n" + "=" * 70)
        print("🧹 Cleanup")
        print("=" * 70)
        await client.cleanup_temp_repo(repo_path)
        await client.close()
        print("✅ Cleaned up")

        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
