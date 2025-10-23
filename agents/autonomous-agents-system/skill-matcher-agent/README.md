# 🎯 Intelligent Skill Matcher Agent

AI agent that performs **intelligent skill matching** using **MeTTa reasoning** and **natural language processing**.

## 🧠 Intelligence Features

- ✅ **Natural Language Processing**: Understands user messages without requiring JSON
- ✅ **MeTTa Reasoning**: Uses symbolic AI for skill relationship analysis
- ✅ **Skill Extraction**: Automatically detects skills from text
- ✅ **Intelligent Matching**: Finds exact matches, alternatives, prerequisites, and domain relationships
- ✅ **Confidence Scoring**: Provides AI-powered confidence levels
- ✅ **Dual Interface**: Both ChatMessage and REST API support

## 🎯 How It Works

### Natural Language Understanding
Instead of expecting structured JSON, the agent can now understand messages like:
- "I know Python and React"
- "Find me JavaScript projects"
- "Match me with backend development tasks"

### MeTTa Knowledge Graph
The agent uses MeTTa to reason about:
- **Language Domains**: Maps skills to expertise areas (frontend, backend, mobile, etc.)
- **Skill Relationships**: Prerequisites, alternatives, and related skills
- **Difficulty Tiers**: Beginner, intermediate, advanced, expert
- **Match Confidence**: Intelligent scoring based on relationship quality

### Intelligent Matching
1. **Exact Matches**: Direct skill matches (100% confidence)
2. **Alternatives**: Similar skills (70% confidence)
3. **Prerequisites**: Required foundational skills (30% confidence)
4. **Domain Matches**: Same expertise domain (50% confidence)

## 🚀 Setup

### Prerequisites
- **WSL/Linux/MacOS** (MeTTa/hyperon doesn't support Windows natively)
- Python 3.10+
- Agentverse API Key

### Installation

1. Navigate to the agent directory:
```bash
cd agents/autonomous-agents-system/skill-matcher-agent
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
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

The agent will start on port 8010 and connect to Agentverse Mailbox.

### Chat Interface
Send natural language messages:
- "I know Python and React, find me suitable projects"
- "Match me with JavaScript bounties"
- "I have backend experience, what can I work on?"

### REST API
The agent also exposes a REST endpoint for orchestrator integration:
```bash
POST http://localhost:8010/api/query
Content-Type: application/json

{
  "user_skills": ["Python", "React"],
  "required_skills": ["JavaScript", "FastAPI"]
}
```

## 🧠 Example Response

```markdown
🎯 **Intelligent Skill Match Analysis**

**Match Score:** 75%
**Confidence:** 82%

✅ **Exact Matches (1):**
React

🔄 **Related Skills (1):**
  • You have Python (alternative to FastAPI)

📚 **Prerequisites Met (1):**
  • You have Python (prerequisite for FastAPI)

🌐 **Domain Expertise (1):**
  • You have React (same domain as JavaScript - frontend-fullstack)

❌ **Missing Skills (1):**
  • JavaScript

💡 **AI Recommendation:** RECOMMENDED - Good match with some learning opportunities

🧠 **MeTTa Reasoning:** Analyzed 2 user skills against 2 requirements using symbolic AI
```

## 🏗️ Architecture

```
skill-matcher-agent/
├── agent.py              # Main intelligent agent
├── metta/
│   ├── knowledge.py      # MeTTa knowledge graph
│   └── skillrag.py       # Skill matching RAG system
├── requirements.txt
└── README.md
```

## 🔗 Integration

### With Orchestrator
The orchestrator can now send natural language queries or structured data:

```python
# Natural language (new!)
query = "I know Python and React, find me suitable projects"

# Structured data (still supported)
query = {
    "user_skills": ["Python", "React"],
    "required_skills": ["JavaScript", "FastAPI"]
}
```

### With Frontend
The frontend can send user messages directly:
```javascript
const response = await fetch('/api/smart-agents', {
  method: 'POST',
  body: JSON.stringify({
    message: "I know Python and React, what can I work on?"
  })
});
```

## 🧪 Testing

Try these natural language queries:
1. "I know Python and Django, find me backend projects"
2. "Match me with React development tasks"
3. "I have JavaScript experience, what frontend work is available?"
4. "Find me projects that match my Go and Rust skills"

## 🔮 Future Enhancements

- [ ] Machine learning skill extraction
- [ ] Learning path recommendations
- [ ] Skill gap analysis with learning suggestions
- [ ] Integration with GitHub skill detection
- [ ] Advanced confidence scoring with user feedback

## 📚 Learn More

- [uAgents Documentation](https://docs.fetch.ai/uagents)
- [MeTTa/Hyperon Docs](https://github.com/trueagi-io/hyperon-experimental)
- [Agentverse](https://agentverse.ai)

---

**🧙‍♂️ This agent now thinks like a human expert, not just a data processor!** ⚔️🔥
