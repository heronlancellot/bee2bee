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
- **✅ Feature 1.2: Documentation Scoring** (0-100 quality score)
  - Checks: README (30pts), LICENSE (10pts), CONTRIBUTING (15pts), CHANGELOG (10pts)
  - Bonus: /docs/ folder (15pts), CODE_OF_CONDUCT (5pts), SECURITY.md (5pts), .github/ (10pts)
  - Ratings: Excellent (80+), Good (60+), Fair (40+), Poor (<40)
  - Tested: ethereum/go-ethereum → 95/100 (Excellent)
  - Tested: heronlancellot/hackglobal-2025 → 30/100 (Poor) ✓

## 2025-10-12
- Initial version with MeTTa reasoning
- GitHub API integration
- Agentverse Mailbox connection
- Project type detection (web3, ml, fullstack, etc)

## TODO
- Add tree-sitter for real complexity analysis
- Vector embeddings + pgvector
