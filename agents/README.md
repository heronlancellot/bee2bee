# 🤖 AI Agents - NectarDAO

Multi-agent system using **MeTTa reasoning** (SingularityNET) + **uAgents** (Fetch.ai) for ETHOnline 2025.

## 🎯 Available Agents

### Repository Analyzer
Analyzes GitHub repositories for complexity, tech stack, and difficulty using MeTTa knowledge graphs.

**Location:** `repository-analyzer/`
**Port:** 8007

## ⚙️ Setup w/ WSL

> **Note:** MeTTa (hyperon) only works on Linux/Mac. Use WSL on Windows.

### 1. Navigate to agent directory

```bash
cd agents/repository-analyzer
```

### 2. Create virtual environment

```bash
# Create venv without pip (WSL Python may not include it)
python3 -m venv venv-wsl --without-pip

# Activate
source venv-wsl/bin/activate

# Install pip manually
curl https://bootstrap.pypa.io/get-pip.py | python
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
# Copy example
cp .env.example .env

# Edit .env and add your Agentverse API key
nano .env
```

Get your API key: https://agentverse.ai/profile/api-keys

### 5. Run agent

```bash
python agent.py
```

Agent will start on `http://localhost:8007` and connect to Agentverse Mailbox.

## 📡 Testing

### Via Agentverse Chat
1. Go to https://agentverse.ai/v1/submit
2. Send message: `ethereum/go-ethereum`
3. Agent analyzes and responds with MeTTa reasoning

### Via API (Frontend)
```bash
curl -X POST http://localhost:3000/api/analyze-repository \
  -H "Content-Type: application/json" \
  -d '{"repository": "facebook/react"}'
```

### Via ASI-1 Chat
Ask: "Analyze the repository facebook/react"

## 🧠 MeTTa Knowledge Graph

The agent uses symbolic reasoning with:
- **Complexity Tiers**: simple → moderate → complex → very-complex
- **Size Categories**: small → medium → large → very-large
- **Difficulty Levels**: beginner → intermediate → advanced → expert
- **Project Types**: backend-api, frontend-app, fullstack-app, ml-project, web3-project
- **Tech Domains**: Maps languages to expertise areas

## 🗂️ Architecture Example

```
repository-analyzer/
├── agent.py              # Main agent (uAgents + Chat Protocol)
├── metta/
│   ├── knowledge.py      # MeTTa knowledge graph rules
│   ├── reporag.py        # RAG for MeTTa queries
│   └── utils.py          # GitHub API + analysis
├── requirements.txt
├── .env
└── README.md
```

## 🔧 Troubleshooting

### "No module named 'hyperon'"
- hyperon only works on Linux/Mac
- Use WSL: `wsl --exec bash -c "cd /mnt/c/path/to/agents/repository-analyzer && source venv-wsl/bin/activate && python agent.py"`

### "pip not found"
```bash
curl https://bootstrap.pypa.io/get-pip.py | python
```

### "Mailbox access token not found"
- Make sure `AGENTVERSE_API_KEY` is set in `.env`
- Get key from https://agentverse.ai/profile/api-keys

### Agent crashes silently
- Check traceback in terminal
- Common: NoneType errors from MeTTa queries (already fixed in latest version)

## 🚀 Development

### Add new MeTTa rules
Edit `metta/knowledge.py`:

```python
metta.space().add_atom(E(S("your-rule"), S("value"), ValueAtom(123)))
```

### Add new analysis functions
Edit `metta/reporag.py` and follow the pattern:

```python
def get_something(self, param: int) -> str:
    try:
        query_str = '!(match &self (rule $var) $var)'
        results = self.metta.run(query_str)
        # Parse results...
    except Exception as e:
        print(f"Error: {e}")
        return "default"
```
