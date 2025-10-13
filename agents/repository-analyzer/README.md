# 📦 Repository Analyzer Agent

AI agent that analyzes GitHub repositories using **MeTTa reasoning** from SingularityNET and **uAgents** from Fetch.ai.

## 🎯 Features

- ✅ **Repository Analysis**: Fetches and analyzes GitHub repos via API
- ✅ **MeTTa Reasoning**: Uses symbolic AI to classify complexity, difficulty, and project type
- ✅ **File Structure Analysis**: Detects frameworks, languages, and project patterns
- ✅ **Chat Interface**: Interact via Agentverse Mailbox
- ✅ **Tech Stack Detection**: Identifies languages, frameworks, and domains

## 🧠 MeTTa Knowledge Graph

The agent uses MeTTa to reason about:

- **Complexity Tiers**: Simple, Moderate, Complex, Very Complex (based on LOC)
- **Repository Size**: Small, Medium, Large, Very Large (based on file count)
- **Difficulty Levels**: Beginner, Intermediate, Advanced, Expert
- **Project Types**: Backend API, Frontend App, Fullstack, ML, Web3
- **Tech Domains**: Maps languages to expertise domains

## 🚀 Setup

### Prerequisites

- **WSL/Linux/MacOS** (MeTTa/hyperon doesn't support Windows natively)
- Python 3.10+
- Agentverse API Key

### Installation

1. Clone and navigate:
```bash
cd agents/repository-analyzer
```

2. Create virtual environment:
```bash
python3 -m venv venv-wsl
source venv-wsl/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your AGENTVERSE_API_KEY
```

## 📡 Usage

### Run Agent

```bash
python agent.py
```

The agent will start and connect to Agentverse Mailbox.

### Chat Interface

Send messages in this format:

```
owner/repo
```

Examples:
- `facebook/react`
- `vercel/next.js`
- `openai/gpt-4`
- `analyze microsoft/typescript`

### Example Response

```markdown
# 📦 Repository: facebook/react

**Description:** The library for web and native user interfaces

📊 **Stats:**
- ⭐ Stars: 230,000
- 🍴 Forks: 47,000
- 🐛 Open Issues: 1,200
- 📁 Files: 2,456
- 💾 Size: 45,000 KB

💻 **Languages:**
- JavaScript: 98.5%
- HTML: 1.0%
- CSS: 0.5%

🔧 **Complexity:** Very Complex
🎯 **Difficulty:** Expert
🏗️ **Project Type:** Frontend App

🧠 **Tech Domains:**
- Frontend Fullstack

📂 **File Types:**
- .js: 1,850 files
- .json: 250 files
- .md: 120 files

🧠 **MeTTa Reasoning:**
- Complexity: very-complex (~450,000 LOC)
- Repository size: very-large (2,456 files)
- Project type: frontend-app
- Tech domain: JavaScript → frontend-fullstack
- Difficulty: expert (score: 90/100)

🔗 [View Repository](https://github.com/facebook/react)

_🔬 Analysis powered by MeTTa reasoning engine_
```

## 🔗 Agent Address

After starting, the agent will print:

```
Agent address: agent1q...
Inspector URL: https://agentverse.ai/inspect/...
```

Use this address to chat with the agent via Agentverse.

## 🏗️ Architecture

```
repository-analyzer/
├── agent.py              # Main agent (uAgents + Chat Protocol)
├── metta/
│   ├── knowledge.py      # MeTTa knowledge graph
│   ├── reporag.py        # RAG for MeTTa queries
│   └── utils.py          # GitHub API + analysis functions
├── requirements.txt
├── .env.example
└── README.md
```

## 🧪 Testing

Try these repos:

1. **Simple**: `torvalds/linux` (C, systems)
2. **Frontend**: `vuejs/vue` (JavaScript, UI)
3. **Fullstack**: `vercel/next.js` (TypeScript, fullstack)
4. **ML**: `tensorflow/tensorflow` (Python, ML)
5. **Web3**: `ethereum/go-ethereum` (Go, blockchain)

## 📝 Notes

- **Rate Limits**: GitHub API has 60 requests/hour without auth, 5000 with token
- **MeTTa**: Runs locally, no external API needed
- **Agentverse**: Requires API key for mailbox communication

## 🔮 Future Enhancements

- [ ] Vector search with embeddings (pgvector)
- [ ] Code search functionality (ripgrep/ugrep)
- [ ] Issue analysis and matching
- [ ] Contributor recommendations
- [ ] Detailed complexity metrics

## 📚 Learn More

- [uAgents Documentation](https://docs.fetch.ai/uagents)
- [MeTTa/Hyperon Docs](https://github.com/trueagi-io/hyperon-experimental)
- [Agentverse](https://agentverse.ai)
