# Changelog

## 2025-10-13
- Fixed MeTTa parsing (was showing tuples like "(Simple 1000)")
- Complexity now correctly classifies: ethereum/go-ethereum → Very Complex ✓
- Tested: ethereum/go-ethereum (~2.3M LOC, 2304 files) → Expert, Very Large
- **✅ Feature 1.1: Improved LOC calculation** (file-based estimation using extension averages)
  - Old method: KB × 10 = 7,640 LOC (overestimated)
  - New method: File-based = 5,120 LOC
  - GitHub real: 5,233 LOC
  - Accuracy: 98% (only 2% difference!)

## 2025-10-12
- Initial version with MeTTa reasoning
- GitHub API integration
- Agentverse Mailbox connection
- Project type detection (web3, ml, fullstack, etc)

## TODO
- Add tree-sitter for real complexity analysis
- Vector embeddings + pgvector
