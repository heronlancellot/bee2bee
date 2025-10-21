# orchestrator-agent/agent.py
"""
Orchestrator Agent - Coordinates all autonomous agents
Provides REST endpoint for frontend + internal agent communication via Agentverse
"""

from uagents import Agent, Context, Model
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    TextContent,
)
import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Agent addresses from .env
AGENT_ADDRESSES = {
    "user_profile": os.getenv("USER_PROFILE_AGENT_ADDRESS"),
    "skill_matcher": os.getenv("SKILL_MATCHER_AGENT_ADDRESS"),
    "bounty_estimator": os.getenv("BOUNTY_ESTIMATOR_AGENT_ADDRESS"),
    "knowledge_synthesizer": os.getenv("KNOWLEDGE_SYNTHESIZER_AGENT_ADDRESS"),
}

# Create orchestrator agent
orchestrator = Agent(
    name="Orchestrator Agent",
    seed="orchestrator_bee2bee_2025_agent",
    port=8013,
    mailbox=True,
)

# Storage for agent responses
agent_responses = {}
response_lock = asyncio.Lock()


# REST API Models
class QueryRequest(Model):
    message: str
    user_id: str = "anonymous"
    conversation_id: str = None


class QueryResponse(Model):
    response: str
    intent: str
    agent_id: str
    conversation_id: str
    timestamp: str


@orchestrator.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("="*60)
    ctx.logger.info("🚀 ORCHESTRATOR AGENT STARTED")
    ctx.logger.info("="*60)
    ctx.logger.info(f"Address: {orchestrator.address}")
    ctx.logger.info(f"Port: 8013")
    ctx.logger.info("")
    ctx.logger.info("📡 REST Endpoint: http://localhost:8013/api/query")
    ctx.logger.info("")
    ctx.logger.info("Coordinating agents:")
    ctx.logger.info(f"  👤 User Profile:     {AGENT_ADDRESSES['user_profile'][:20]}...")
    ctx.logger.info(f"  🎯 Skill Matcher:    {AGENT_ADDRESSES['skill_matcher'][:20]}...")
    ctx.logger.info(f"  💰 Bounty Estimator: {AGENT_ADDRESSES['bounty_estimator'][:20]}...")
    if AGENT_ADDRESSES['knowledge_synthesizer']:
        ctx.logger.info(f"  🧠 Knowledge Synth:  {AGENT_ADDRESSES['knowledge_synthesizer'][:20]}...")
    else:
        ctx.logger.info(f"  🧠 Knowledge Synth:  Not configured")
    ctx.logger.info("="*60)


@orchestrator.on_message(ChatMessage)
async def handle_agent_response(ctx: Context, sender: str, msg: ChatMessage):
    """Receive responses from other agents via Agentverse"""

    ctx.logger.info(f"📩 Response received from {sender[:20]}...")

    text_content = next(
        (item for item in msg.content if isinstance(item, TextContent)),
        None
    )

    if text_content:
        async with response_lock:
            agent_responses[sender] = text_content.text
            ctx.logger.info(f"✅ Stored response from agent")


async def query_agents_parallel_http(queries: dict) -> dict:
    """Query all agents in parallel via HTTP (direct)"""

    print(f"🔄 Querying {len(queries)} agents in parallel via HTTP...")

    # Agent HTTP endpoints
    agent_endpoints = {
        "user_profile": "http://localhost:8009",
        "skill_matcher": "http://localhost:8010",
        "bounty_estimator": "http://localhost:8011",
        "knowledge_synthesizer": "http://localhost:8013",
    }

    import aiohttp

    async def query_single_agent(agent_name: str, query: dict):
        """Query single agent via HTTP"""
        endpoint = agent_endpoints.get(agent_name)
        if not endpoint:
            return None

        try:
            async with aiohttp.ClientSession() as session:
                # Try direct HTTP endpoint if exists
                url = f"{endpoint}/api/query"

                async with session.post(
                    url,
                    json=query,  # Send query directly, not wrapped
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"⚠️  {agent_name}: HTTP {response.status}")
                        return None

        except Exception as e:
            print(f"❌ ERROR - {agent_name}: {str(e)}")
            # Return None instead of mock - we want real responses only
            return None

    # Query all in parallel
    tasks = [
        query_single_agent(agent_name, query)
        for agent_name, query in queries.items()
    ]

    results = await asyncio.gather(*tasks)

    # Build response dict
    responses = {}
    agent_names = list(queries.keys())

    for i, result in enumerate(results):
        agent_name = agent_names[i]
        if result:
            # Extract 'response' field from JSON if it exists
            if isinstance(result, dict) and 'response' in result:
                responses[AGENT_ADDRESSES[agent_name]] = result['response']
            else:
                responses[AGENT_ADDRESSES[agent_name]] = str(result)
            print(f"✅ {agent_name}: Response received successfully")
        else:
            print(f"⚠️  {agent_name}: No response (agent might be offline)")

    print(f"\n📊 Summary: Received {len(responses)}/3 agent responses")

    if len(responses) == 0:
        print(f"❌ CRITICAL: No agents responded! Check if agents are running on ports 8009, 8010, 8011")

    return responses


def detect_intent(message: str) -> str:
    """Detect user intent with improved keyword matching"""
    message_lower = message.lower()

    # Keywords for FIND_MATCHES intent
    find_keywords = [
        "show", "find", "get", "search", "look", "fetch",
        "issues", "bounties", "bounty", "tasks", "projects",
        "python", "javascript", "typescript", "react", "node",
        "rust", "go", "java", "ruby", "php", "swift", "kotlin",
        "match", "suitable", "recommend", "suggest",
        "solve", "work on", "contribute"
    ]

    # Keywords for EXPLAIN_REASONING intent
    explain_keywords = [
        "why", "explain", "reasoning", "how", "what",
        "tell me", "describe", "elaborate"
    ]

    # Check for FIND_MATCHES intent
    if any(word in message_lower for word in find_keywords):
        return "FIND_MATCHES"

    # Check for EXPLAIN_REASONING intent
    elif any(word in message_lower for word in explain_keywords):
        return "EXPLAIN_REASONING"

    # Default to general_chat
    else:
        return "general_chat"


def extract_skills(message: str) -> list:
    """Extract skills from message"""
    common_skills = ["Python", "JavaScript", "TypeScript", "React", "Node.js",
                     "Go", "Rust", "Java", "C++", "Ruby", "asyncio", "FastAPI",
                     "Django", "Flask", "Vue", "Angular", "Solidity", "Kotlin", "Swift"]

    found_skills = []
    message_lower = message.lower()

    for skill in common_skills:
        if skill.lower() in message_lower:
            found_skills.append(skill)

    # Return empty list if no skills found - no mocks!
    return found_skills


def synthesize_response(agent_responses: dict, user_message: str, intent: str) -> str:
    """Synthesize responses from all agents"""

    if intent == "FIND_MATCHES":
        # Check if we have any responses
        if not agent_responses or len(agent_responses) == 0:
            return f"""⚠️ **No Agent Responses**

I couldn't reach any of the specialized agents. Please make sure all agents are running:

1. User Profile Agent (port 8009)
2. Skill Matcher Agent (port 8010)
3. Bounty Estimator Agent (port 8011)

Run each agent in a separate terminal:
```
cd user-profile-agent && python agent.py
cd skill-matcher-agent && python agent.py
cd bounty-estimator-agent && python agent.py
```

Your query: "{user_message}"
"""

        synthesis = "# 🎯 Perfect Issues for You!\n\n"
        synthesis += "I consulted with my specialized agents:\n"
        synthesis += "- 👤 User Profile Agent\n"
        synthesis += "- 🎯 Skill Matcher Agent\n"
        synthesis += "- 💰 Bounty Estimator Agent\n\n"
        synthesis += "---\n\n"

        # Add agent responses
        agents_responded = []
        for agent_address, response in agent_responses.items():
            # Determine which agent
            if AGENT_ADDRESSES["user_profile"] == agent_address:
                synthesis += "## 👤 User Profile Analysis\n\n"
                synthesis += f"{response}\n\n"
                agents_responded.append("user_profile")
            elif AGENT_ADDRESSES["skill_matcher"] == agent_address:
                synthesis += "## 🎯 Skills Match\n\n"
                synthesis += f"{response}\n\n"
                agents_responded.append("skill_matcher")
            elif AGENT_ADDRESSES["bounty_estimator"] == agent_address:
                synthesis += "## 💰 Bounty Estimation\n\n"
                synthesis += f"{response}\n\n"
                agents_responded.append("bounty_estimator")

        # Show warning for agents that didn't respond
        missing_agents = []
        if "user_profile" not in agents_responded:
            missing_agents.append("👤 User Profile Agent (port 8009)")
        if "skill_matcher" not in agents_responded:
            missing_agents.append("🎯 Skill Matcher Agent (port 8010)")
        if "bounty_estimator" not in agents_responded:
            missing_agents.append("💰 Bounty Estimator Agent (port 8011)")

        if missing_agents:
            synthesis += "---\n\n"
            synthesis += "⚠️ **Warning:** Some agents didn't respond:\n"
            for agent in missing_agents:
                synthesis += f"  • {agent}\n"
            synthesis += "\n"

        synthesis += "---\n\n"
        synthesis += "**Ready to accept?** 🚀\n"

        return synthesis

    else:
        return f"""🤖 **Autonomous Agents Orchestrator**

I coordinate 3 specialized agents with MeTTa reasoning.

**Try asking:**
• "Show me Python issues I can solve"
• "Find JavaScript bounties for me"
• "Match me with React projects"

What would you like to do?"""


@orchestrator.on_rest_post("/api/query", QueryRequest, QueryResponse)
async def handle_rest_query(ctx: Context, req: QueryRequest) -> QueryResponse:
    """
    REST endpoint for frontend integration
    This is called by http_server_frontend.py
    """

    ctx.logger.info("="*60)
    ctx.logger.info(f"📨 REST Query received: {req.message[:50]}...")
    ctx.logger.info("="*60)

    # Detect intent
    intent = detect_intent(req.message)
    ctx.logger.info(f"🎯 Intent: {intent}")

    conversation_id = req.conversation_id or f"conv_{datetime.now().timestamp()}"

    if intent == "FIND_MATCHES":
        # Extract skills from message
        skills = extract_skills(req.message)
        ctx.logger.info(f"🔍 Skills detected: {', '.join(skills) if skills else 'none'}")

        # Extract additional info from message (years, complexity, hours, stars)
        import re
        message_lower = req.message.lower()

        # Extract years of experience
        years_match = re.search(r'(\d+)\s*(?:years?|yrs?)', message_lower)
        years_experience = int(years_match.group(1)) if years_match else 0

        # Extract complexity
        complexity_score = 5  # default moderate
        if any(word in message_lower for word in ["easy", "simple", "trivial"]):
            complexity_score = 3
        elif any(word in message_lower for word in ["hard", "difficult", "complex"]):
            complexity_score = 7
        elif any(word in message_lower for word in ["very hard", "expert", "advanced"]):
            complexity_score = 9

        # Extract hours
        hours_match = re.search(r'(\d+)\s*(?:hours?|hrs?|h)', message_lower)
        estimated_hours = int(hours_match.group(1)) if hours_match else 0

        # Extract stars
        stars_match = re.search(r'(\d+)k?\s*stars?', message_lower)
        repo_stars = 0
        if stars_match:
            stars_value = int(stars_match.group(1))
            repo_stars = stars_value * 1000 if 'k' in stars_match.group(0) else stars_value

        # Prepare queries for each agent (NO HARDCODED VALUES!)
        queries = {
            "user_profile": {
                "user_id": req.user_id,
                "skills": skills,
                "years_experience": years_experience,
                "action": "get_profile"
            },
            "skill_matcher": {
                "user_skills": skills,
                "required_skills": skills  # Use same skills as required for now
            },
            "bounty_estimator": {
                "complexity_score": complexity_score,
                "required_skills": skills,
                "estimated_hours": estimated_hours,
                "repo_stars": repo_stars
            }
        }

        # Query agents in parallel
        responses = await query_agents_parallel_http(queries)

        # Synthesize
        synthesized = synthesize_response(responses, req.message, intent)

        ctx.logger.info("✅ Response synthesized!")
        ctx.logger.info("="*60)

        return QueryResponse(
            response=synthesized,
            intent=intent,
            agent_id="orchestrator",
            conversation_id=conversation_id,
            timestamp=datetime.now().isoformat()
        )

    else:
        # General chat
        return QueryResponse(
            response=synthesize_response({}, req.message, "general_chat"),
            intent="general_chat",
            agent_id="orchestrator",
            conversation_id=conversation_id,
            timestamp=datetime.now().isoformat()
        )


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 AUTONOMOUS AGENTS ORCHESTRATOR")
    print("="*60)
    print(f"\n📍 Agent Address: {orchestrator.address}")
    print(f"📡 REST API: http://localhost:8013/api/query")
    print(f"🌐 Port: 8013")
    print("\nThis orchestrator:")
    print("  1. Exposes REST endpoint for frontend")
    print("  2. Queries 3 agents in parallel via Agentverse")
    print("  3. Synthesizes intelligent responses")
    print("\nCoordinating agents:")
    print("  - User Profile Agent (8009)")
    print("  - Skill Matcher Agent (8010)")
    print("  - Bounty Estimator Agent (8011)")
    print("\n⚠️  Make sure the 3 agents are running first!")
    print("="*60 + "\n")

    print("Starting...")
    orchestrator.run()
