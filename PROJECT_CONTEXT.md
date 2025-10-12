# 📋 **PROJECT CONTEXT DOCUMENT**

---

## 🎯 **PROJECT CORE**

### **Project Name:** NectarDAO

### **Pitch:**
```
AI-powered platform that matches open-source contributors 
with perfect GitHub issues using intelligent agents. 
Each repository gets a dedicated AI agent that understands 
the codebase and answers questions.

Built on Fetch.ai uAgents, powered by MeTTa reasoning.
```

### **Problem:**
```
Contributors:
❌ Waste hours searching for issues matching their skills
❌ Don't understand complex codebases
❌ Can't tell if maintainers will merge their work

Maintainers:
❌ Don't know which issues suit external contributors
❌ Answer same questions repeatedly
❌ Contributors claim issues then disappear
```

### **Solution:**
```
1. Maintainer adds repo → AI analyzes complexity & codebase
2. System creates dedicated Repo Agent
3. Contributor connects GitHub → Profile analyzed
4. AI matches contributor skills with repo needs
5. Contributor chats with Repo Agent for context
6. Claims issue → works → submits PR
7. System updates reputation scores
```

---

## 🤖 **AGENT ARCHITECTURE**

### **Total Agents: 5**

```
LAYER 1: Repository Intelligence
├─ Complexity Analyzer Agent (singleton)
└─ Repo Agent (1 per repository)

LAYER 2: User Intelligence  
└─ Profile Agent (1 per user)

LAYER 3: Global Intelligence
├─ Matcher Agent (singleton)
└─ Verifier Agent (singleton)
```

---

## 🔧 **AGENT SPECIFICATIONS**

### **AGENT #1: COMPLEXITY ANALYZER**

**Type:** Singleton  
**Hosting:** Agentverse

**Purpose:**
- Calculate repository complexity (0-100 score)
- Identify tech stack
- Evaluate documentation quality
- Assess test coverage

**Triggered By:**
- Repo Agent (during onboarding)
- Matcher Agent (for match calculations)
- Manual API call (re-analyze)

**Key Functions:**
```
analyze_repository_complexity()
├─ Input: github_url, repo_metadata
└─ Output: complexity_score, factors, tech_stack, reasoning

calculate_score()
├─ Input: repo_factors
└─ Output: int (0-100)

identify_tech_stack()
├─ Input: languages, dependencies, configs
└─ Output: frameworks, databases, tools
```

**Output Example:**
```json
{
  "complexity_score": 74,
  "factors": {
    "codebase_size": "Large (150k LOC)",
    "primary_language": "Python",
    "dependencies": 127,
    "contributors": 45
  },
  "tech_stack": {
    "languages": {"Python": 60, "JavaScript": 30},
    "frameworks": ["Django", "React"],
    "tools": ["Docker", "Redis"]
  },
  "reasoning": "High complexity due to microservices architecture",
  "tier": "Advanced"
}
```

**MeTTa Usage:**
- Weighted scoring formula
- Pattern detection for frameworks
- Complexity classification

---

### **AGENT #2: REPO AGENT**

**Type:** Dynamic (1 per repository)  
**Hosting:** Agentverse

**Purpose:**
- Index codebase
- Answer contributor questions
- Identify issues suitable for external contributors
- Provide code context

**Triggered By:**
- Repository onboarded (initial analysis)
- Chat message received
- New issue created
- Hourly cron (updates)

**Key Functions:**
```
analyze_repository()
├─ Input: github_url
└─ Output: repo_id, knowledge_graph, embeddings

answer_question()
├─ Input: user_message, chat_history
└─ Output: response, sources, suggested_issues

identify_external_friendly_issues()
├─ Input: list of issues
└─ Output: filtered issues with scores
```

**Example Interaction:**
```
Q: "Where is the authentication logic?"
A: "Authentication is handled in:
    - src/auth/index.ts (main logic, lines 45-120)
    - src/middleware/auth.ts (Express middleware)
    See PR #234 for recent security updates"

Q: "What does Issue #42 actually need?"
A: "Issue #42 requires:
    1. Update src/auth/oauth.py (line 56, fix redirect bug)
    2. Add test in tests/test_oauth.py
    Estimated: 4-6 hours"
```

**Data Sources:**
- GitHub API
- Complexity Analyzer
- PostgreSQL + pgvector

**MeTTa Usage:**
- Issue classification
- Code similarity matching
- Context relevance scoring

---

### **AGENT #3: PROFILE AGENT**

**Type:** Dynamic (1 per user)  
**Hosting:** Agentverse

**Purpose:**
- Analyze GitHub profile
- Extract skills
- Calculate reputation
- Track contribution history

**Triggered By:**
- User connects GitHub
- Chat message to profile
- Issue completed
- Daily cron (sync GitHub activity)

**Key Functions:**
```
analyze_profile()
├─ Input: github_username
└─ Output: skills, patterns, reputation_score

calculate_reputation()
├─ Input: user_activity_history
└─ Output: int (0-100)

update_after_completion()
├─ Input: issue_id, success
└─ Output: new_reputation_score
```

**Output Example:**
```json
{
  "skills": {
    "Python": 80,
    "JavaScript": 60,
    "Go": 30
  },
  "specialties": ["Security", "API Development"],
  "patterns": {
    "bug_fixes": 65,
    "features": 25,
    "documentation": 10
  },
  "reputation": {
    "score": 78,
    "tier": "Gold",
    "completion_rate": 0.92,
    "avg_time_days": 4.2
  },
  "stats": {
    "issues_completed": 15,
    "success_rate": 0.93
  }
}
```

**MeTTa Usage:**
- Reputation calculation
- Skill level assessment
- Growth trajectory prediction

---

### **AGENT #4: MATCHER AGENT**

**Type:** Singleton  
**Hosting:** Agentverse

**Purpose:**
- Match contributors with issues
- Calculate match scores
- Generate personalized feeds
- Optimize success probability

**Triggered By:**
- Hourly cron (refresh feeds)
- New issue created
- User profile updated
- New repo added

**Key Functions:**
```
calculate_match_score()
├─ Input: contributor, issue
└─ Output: float (0-1), reasoning

generate_feed()
├─ Input: user_id
└─ Output: list of matched issues

bulk_match()
├─ Input: none (runs on all users)
└─ Output: updated feeds in DB
```

**Matching Factors:**
```
1. Skill Match (40%)
   └─ Language overlap

2. Pattern Match (30%)
   └─ Similar issues solved

3. Difficulty Fit (20%)
   └─ Appropriate complexity

4. Repo Health (10%)
   └─ Maintainer activity
```

**Output Example:**
```json
{
  "issue_id": "issue-42",
  "match_score": 92,
  "reasoning": {
    "skill_match": "95% (Python expert)",
    "pattern_match": "90% (solved 12 similar OAuth issues)",
    "difficulty": "Perfect (intermediate level)",
    "repo_health": "Excellent (maintainer responds <2 days)"
  },
  "estimated_hours": 6,
  "success_probability": 0.89
}
```

**MeTTa Usage:**
- Multi-factor scoring
- Pattern detection
- Difficulty assessment

---

### **AGENT #5: VERIFIER AGENT**

**Type:** Singleton  
**Hosting:** Agentverse

**Purpose:**
- Verify PR completions
- Update reputation scores
- Track issue status

**Triggered By:**
- GitHub webhook (PR merged)
- Manual verification request

**Key Functions:**
```
verify_completion()
├─ Input: pr_number, repo_id
└─ Output: is_valid, issue_id, claimer_verified

update_reputations()
├─ Input: contributor_id, maintainer_id, success
└─ Output: updated_scores

track_issue_status()
├─ Input: issue_id, status
└─ Output: status_updated
```

**Verification Flow:**
```
1. PR merged event received
2. Extract issue number from PR body
3. Check if issue is claimed
4. Verify PR author == claimer
5. If valid:
   ├─ Update issue status (completed)
   ├─ Update Profile Agents (reputation +10)
   └─ Send notifications
6. If invalid:
   └─ Log for manual review
```

**Fraud Prevention:**
- Cross-check GitHub identity
- Time window validation
- Pattern detection

---

## 📡 **AGENT COMMUNICATION FLOWS**

### **Flow 1: Repository Onboarding**

```
User (Maintainer)
  ↓ POST /api/repos/onboard
n8n
  ↓
Complexity Analyzer Agent
  ├─ Analyze repo
  ├─ Calculate complexity
  └─ Return: {score, tech_stack}
  ↓
Repo Agent (created)
  ├─ Receive complexity data
  ├─ Index codebase
  └─ Create embeddings
  ↓
PostgreSQL
  ↓
Response: "Repo analyzed! Score: 74/100"
```

### **Flow 2: Contributor Profile Creation**

```
User (Contributor)
  ↓ GitHub OAuth
n8n
  ↓
Profile Agent (created)
  ├─ Fetch GitHub data
  ├─ Extract skills
  └─ Calculate reputation
  ↓
PostgreSQL
  ↓
Matcher Agent
  └─ Generate initial feed
  ↓
Response: "Profile created! Found 12 matches"
```

### **Flow 3: Finding Matches**

```
Cron (hourly)
  ↓
Matcher Agent
  ├─ Fetch contributors (DB)
  ├─ Fetch issues (DB)
  └─ For each contributor:
      ├─ Query Profile Agent (skills)
      ├─ For each issue:
      │   ├─ Query Repo Agent (context)
      │   ├─ Query Complexity Analyzer (difficulty)
      │   ├─ Calculate match score (MeTTa)
      │   └─ If score > 70%: add to feed
      └─ Store matches (PostgreSQL)
  ↓
UI shows updated feeds
```

### **Flow 4: Chat with Repo**

```
User
  ↓ WebSocket: "Where is auth logic?"
n8n
  ↓
Repo Agent
  ├─ Search embeddings (pgvector)
  ├─ Query knowledge graph (MeTTa)
  └─ Generate response
  ↓
n8n
  ↓ WebSocket
User sees response with citations
```

### **Flow 5: PR Completion**

```
GitHub (PR merged)
  ↓ Webhook
n8n
  ↓
Verifier Agent
  ├─ Extract issue number
  ├─ Check if claimed
  ├─ Verify PR author == claimer
  └─ Valid? → update statuses
  ↓
Profile Agents (both users)
  ├─ Contributor: reputation +10
  └─ Maintainer: reputation +5
  ↓
Notifications
```

---

## 💾 **DATABASE SCHEMA (PostgreSQL)**

### **Data Stored:**

**User Data:**
- Basic info (GitHub username, email, avatar)
- Skills (languages, percentages)
- Patterns (bug_fixes, features, docs)
- Reputation score & tier
- Agent ID (Agentverse)

**Repository Data:**
- GitHub URL & ID
- Owner reference
- Complexity score
- Tech stack (languages, frameworks)
- Agent ID (Agentverse)
- Analysis timestamps

**Issue Data:**
- GitHub issue number & ID
- Title & description
- Difficulty level
- Estimated hours
- Status (open, claimed, completed)
- Claimer reference
- Timestamps

**Match Data:**
- User-Issue pairs
- Match score (0-100)
- Reasoning (JSON)
- Interaction tracking

**Chat Data:**
- Message history per user-repo
- Role (user, assistant)
- Content & sources
- Timestamps

**Embeddings:**
- Code snippets
- Issue descriptions
- PR content
- Vector data (1536 dimensions)

---

## 🗂️ **AGENTVERSE CONFIGURATION**

### **Agents to Create:**

```
1. complexity-analyzer-agent (singleton)
2. repo-agent-{repo_id} (dynamic)
3. profile-agent-{user_id} (dynamic)
4. matcher-agent (singleton)
5. verifier-agent (singleton)
```

### **Environment Variables:**

```bash
# GitHub
GITHUB_TOKEN=ghp_xxxxx

# Database
DATABASE_URL=postgresql://user:pass@host:5432/nectardao

# AI
OPENAI_API_KEY=sk-xxxxx
METTA_ENDPOINT=https://metta.singularitynet.io

# Platform
API_BASE_URL=https://api.nectardao.xyz
WEBHOOK_SECRET=xxxxx
```

---

## 📁 **PROJECT STRUCTURE**

```
nectardao/
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── repos/
│   │   ├── feed/
│   │   ├── profile/
│   │   └── chat/
│   ├── components/
│   ├── lib/
│   └── package.json
├── backend/
│   ├── api/
│   │   ├── src/
│   │   │   ├── routes/
│   │   │   ├── controllers/
│   │   │   └── middleware/
│   │   └── package.json
│   └── n8n/
│       └── workflows/
├── agents/
│   ├── complexity_analyzer.py
│   ├── repo_agent.py
│   ├── profile_agent.py
│   ├── matcher_agent.py
│   ├── verifier_agent.py
│   └── requirements.txt
├── database/
│   ├── schema.sql
│   └── migrations/
├── docs/
│   ├── PROJECT_CONTEXT.md
│   ├── AGENT_SPECS.md
│   └── API_DOCS.md
├── docker-compose.yml
└── README.md
```

