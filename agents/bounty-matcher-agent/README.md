# 🎯 Bounty Matcher Agent

AI agent that matches developers with perfect bounties/issues using **MeTTa reasoning** from SingularityNET and **uAgents** from Fetch.ai.

## 🚀 Features

- ✅ **Intelligent Matching**: Uses MeTTa reasoning to match developers with bounties
- ✅ **Multi-Factor Analysis**: Considers skills, experience, complexity, preferences
- ✅ **Confidence Scoring**: Provides detailed confidence scores and reasoning
- ✅ **GitHub Integration**: Fetches real issues from GitHub repositories
- ✅ **Chat Interface**: Interact via Agentverse Mailbox
- ✅ **Autonomous Agent**: Can be deployed to Agentverse for 24/7 operation

## 🧠 MeTTa Knowledge Graph

The agent uses MeTTa to reason about:

- **Skill Levels**: Beginner, Intermediate, Advanced, Expert (based on years)
- **Bounty Tiers**: Micro, Small, Medium, Large, XLarge (based on value)
- **Complexity Levels**: Trivial, Easy, Moderate, Hard, Very Hard (0-10 scale)
- **Time Estimates**: Quick, Short, Medium, Long, Very Long (in hours)
- **Language-Skill Mapping**: Maps languages to skill domains
- **Confidence Levels**: Low, Medium, High, Perfect (based on match score)

## 📊 Matching Algorithm

The agent calculates match confidence using multiple factors:

1. **Skill Match (40%)**: Exact skill matches vs required
2. **Experience Match (20%)**: User's level vs issue complexity
3. **Complexity Match (15%)**: User's avg vs issue complexity
4. **Bounty Preference (15%)**: Value within user's range
5. **Time Match (10%)**: Estimated hours vs user capacity

**Total Score**: 0-100, categorized as:
- 95-100: Perfect Match 🟢
- 80-94: High Confidence 🟢
- 60-79: Medium Confidence 🟡
- 40-59: Consider 🟡
- 0-39: Not Recommended 🔴

## 🛠️ Setup

### Prerequisites

- **WSL/Linux/MacOS** (MeTTa doesn't support Windows natively)
- Python 3.10+
- Agentverse API Key

### Installation

1. Navigate to agent directory:
```bash
cd agents/bounty-matcher-agent
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

The agent will start and connect to Agentverse Mailbox.

### Chat Interface

Send messages in JSON format:

```json
{
  "skills": ["Python", "JavaScript", "React"],
  "years_experience": 3,
  "preferences": {
    "min_bounty": 50,
    "max_bounty": 200,
    "max_hours_per_week": 20
  }
}
```

### Example Response

```markdown
# 🎯 Top Bounty Matches for You

**Your Profile:** Python, JavaScript, React
**Experience:** Advanced

## 1. Fix async rendering bug in React components

**Repository:** facebook/react
💰 **Bounty:** $75
⏱️ **Estimated Time:** ~6 hours
🎯 **Complexity:** 6/10
🟢 **Match Confidence:** 89% (high)

**Why This Matches:**
  • Skill match: 3/3 skills (100%)
  • Experience: advanced vs required advanced
  • Complexity: issue=6/10, user avg=5.5/10
  • Bounty $75 in preferred range
  • Time estimate 6h within capacity

**Required Skills:** React, JavaScript, TypeScript
**Labels:** bug, good first issue, React
🔗 [View Issue](https://github.com/facebook/react/issues/12345)

**Recommendation:** HIGHLY RECOMMENDED

---

_🧠 Analysis powered by MeTTa reasoning engine_
```

## 🏗️ Architecture

```
bounty-matcher-agent/
├── agent.py              # Main agent (uAgents + Chat Protocol)
├── metta/
│   ├── knowledge.py      # MeTTa knowledge graph for bounty matching
│   ├── bountyrag.py      # RAG for match calculations
│   └── utils.py          # GitHub API + matching functions
├── requirements.txt
├── .env.example
└── README.md
```

## 🔗 Integration with Smart Agents

This agent can be integrated with your smart-agents orchestrator:

1. **Protocol-based Communication**: Uses uAgents protocols
2. **Consensus Layer Compatible**: Can be queried in parallel
3. **MeTTa Reasoning**: Provides explainable AI matching
4. **Autonomous Operation**: Runs independently, can be deployed to Agentverse

## 🧪 Testing

Try different profiles:

1. **Beginner Python Dev**:
```json
{
  "skills": ["Python"],
  "years_experience": 0.5,
  "preferences": {"min_bounty": 25, "max_bounty": 100}
}
```

2. **Full-Stack Senior**:
```json
{
  "skills": ["Python", "JavaScript", "TypeScript", "React", "Django"],
  "years_experience": 7,
  "preferences": {"min_bounty": 200, "max_bounty": 1000}
}
```

3. **Mobile Developer**:
```json
{
  "skills": ["Swift", "Kotlin", "React Native"],
  "years_experience": 3,
  "preferences": {"max_hours_per_week": 15}
}
```

## 📝 Notes

- **Rate Limits**: GitHub API has 60 requests/hour without auth
- **MeTTa**: Runs locally, no external API needed
- **Agentverse**: Requires API key for mailbox communication
- **Real Bounties**: Currently uses GitHub issues with "good first issue" label
- **Future**: Can integrate with bounty platforms (Gitcoin, OpenQ, etc.)

## 🔮 Future Enhancements

- [ ] Integration with actual bounty platforms
- [ ] Historical performance tracking
- [ ] Machine learning for match refinement
- [ ] Multi-repo aggregation
- [ ] Real-time notifications
- [ ] Team matching (multi-developer bounties)
- [ ] Skill development recommendations

## 🌟 Integration Example

```python
# In your smart-agents orchestrator:
from uagents import Agent, Context

async def query_bounty_matcher(ctx: Context, user_profile: dict):
    """Query the bounty matcher agent"""
    await ctx.send(
        "agent1q...bounty_matcher_address",  # Agent address
        json.dumps(user_profile)
    )
```

## 📚 Learn More

- [uAgents Documentation](https://docs.fetch.ai/uagents)
- [MeTTa/Hyperon Docs](https://github.com/trueagi-io/hyperon-experimental)
- [Agentverse](https://agentverse.ai)

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**License**: MIT
