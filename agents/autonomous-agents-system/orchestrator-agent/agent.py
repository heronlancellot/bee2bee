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
}

# Create orchestrator agent
orchestrator = Agent(
    name="Orchestrator Agent",
    seed="orchestrator_bee2bee_2025_agent",
    port=8012,
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
    ctx.logger.info(f"Port: 8012")
    ctx.logger.info("")
    ctx.logger.info("📡 REST Endpoint: http://localhost:8012/api/query")
    ctx.logger.info("")
    ctx.logger.info("Coordinating agents:")
    ctx.logger.info(f"  👤 User Profile:     {AGENT_ADDRESSES['user_profile'][:20]}...")
    ctx.logger.info(f"  🎯 Skill Matcher:    {AGENT_ADDRESSES['skill_matcher'][:20]}...")
    ctx.logger.info(f"  💰 Bounty Estimator: {AGENT_ADDRESSES['bounty_estimator'][:20]}...")
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
    }

    import aiohttp

    async def query_single_agent(agent_name: str, query: dict):
        """Query single agent via HTTP"""
        endpoint = agent_endpoints.get(agent_name)
        if not endpoint:
            return None

        try:
            # Create payload for agent
            payload = json.dumps(query)

            async with aiohttp.ClientSession() as session:
                # Try direct HTTP endpoint if exists
                url = f"{endpoint}/api/query"

                async with session.post(
                    url,
                    json={"query": payload},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"⚠️  {agent_name}: HTTP {response.status}")
                        return None

        except Exception as e:
            print(f"⚠️  {agent_name}: {str(e)}")
            # Return mock response for now
            return create_mock_response(agent_name, query)

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
        if result:
            agent_name = agent_names[i]
            responses[AGENT_ADDRESSES[agent_name]] = str(result)

    print(f"✅ Received {len(responses)}/3 responses")

    return responses


def create_mock_response(agent_name: str, query: dict) -> str:
    """Create mock response when agent not available via HTTP"""

    if agent_name == "user_profile":
        skills = query.get("skills", [])
        years = query.get("years_experience", 3)
        return f"""👤 **User Profile**

**Skills:** {', '.join(skills)}
**Experience:** {years} years
**Level:** Advanced

(Mock response - agent running but no HTTP endpoint)"""

    elif agent_name == "skill_matcher":
        user_skills = query.get("user_skills", [])
        required = query.get("required_skills", [])
        matches = [s for s in user_skills if s in required]
        return f"""🎯 **Skill Match**

**Your Skills:** {', '.join(user_skills)}
**Required:** {', '.join(required)}
**Matches:** {len(matches)}/{len(required)}
**Score:** {int(len(matches)/len(required)*100) if required else 0}%

(Mock response - agent running but no HTTP endpoint)"""

    elif agent_name == "bounty_estimator":
        complexity = query.get("complexity_score", 5)
        hours = query.get("estimated_hours", 4)
        return f"""💰 **Bounty Estimation**

**Complexity:** {complexity}/10
**Estimated Time:** ~{hours} hours
**Recommended Value:** $50-$100
**Hourly Rate:** ~$12.50/hour

(Mock response - agent running but no HTTP endpoint)"""

    return "Response not available"


def detect_intent(message: str) -> str:
    """Detect user intent"""
    message_lower = message.lower()

    if any(word in message_lower for word in ["show", "find", "get", "issues", "bounties", "python", "javascript", "match"]):
        return "FIND_MATCHES"
    elif any(word in message_lower for word in ["why", "explain", "reasoning"]):
        return "EXPLAIN_REASONING"
    else:
        return "general_chat"


def extract_skills(message: str) -> list:
    """Extract skills from message"""
    common_skills = ["Python", "JavaScript", "TypeScript", "React", "Node.js",
                     "Go", "Rust", "Java", "C++", "Ruby", "asyncio", "FastAPI"]

    found_skills = []
    message_lower = message.lower()

    for skill in common_skills:
        if skill.lower() in message_lower:
            found_skills.append(skill)

    return found_skills if found_skills else ["Python"]


def synthesize_response(agent_responses: dict, user_message: str, intent: str) -> str:
    """Synthesize responses from all agents"""

    if intent == "FIND_MATCHES":
        synthesis = "# 🎯 Perfect Issues for You!\n\n"
        synthesis += "I consulted with my specialized agents:\n"
        synthesis += "- 👤 User Profile Agent\n"
        synthesis += "- 🎯 Skill Matcher Agent\n"
        synthesis += "- 💰 Bounty Estimator Agent\n\n"
        synthesis += "---\n\n"

        # Add agent responses
        for agent_address, response in agent_responses.items():
            # Determine which agent
            if AGENT_ADDRESSES["user_profile"] == agent_address:
                synthesis += "## 👤 User Profile Analysis\n\n"
                synthesis += f"{response}\n\n"
            elif AGENT_ADDRESSES["skill_matcher"] == agent_address:
                synthesis += "## 🎯 Skills Match\n\n"
                synthesis += f"{response}\n\n"
            elif AGENT_ADDRESSES["bounty_estimator"] == agent_address:
                synthesis += "## 💰 Bounty Estimation\n\n"
                synthesis += f"{response}\n\n"

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
        # Extract skills
        skills = extract_skills(req.message)
        ctx.logger.info(f"🔍 Skills detected: {', '.join(skills)}")

        # Prepare queries for each agent
        queries = {
            "user_profile": {
                "user_id": req.user_id,
                "skills": skills,
                "years_experience": 3,
                "action": "get_profile"
            },
            "skill_matcher": {
                "user_skills": skills,
                "required_skills": ["Python", "asyncio", "FastAPI"]
            },
            "bounty_estimator": {
                "complexity_score": 6,
                "required_skills": skills,
                "estimated_hours": 4,
                "repo_stars": 450
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
    print(f"📡 REST API: http://localhost:8012/api/query")
    print(f"🌐 Port: 8012")
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
