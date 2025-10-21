# bounty-estimator-agent/agent.py
"""
Bounty Estimator Agent - Estimates bounty values using MeTTa reasoning
"""

from uagents import Context, Protocol, Agent, Model
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)
import os
import json
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.knowledge_base import shared_kb
from supabase_agent_client import create_supabase_agent_client

# MeTTa imports for intelligent reasoning
from hyperon import MeTTa
from metta.knowledge import initialize_bounty_knowledge_graph
from metta.bountyrag import BountyRAG

load_dotenv()

# Initialize Supabase client
supabase_client = create_supabase_agent_client()

agent = Agent(
    name="Bounty Estimator Agent",
    seed="bounty_estimator_bee2bee_2025_agent",
    port=8011,
    mailbox=True,
    publish_agent_details=True
)

# Initialize MeTTa AI reasoning
metta = MeTTa()
initialize_bounty_knowledge_graph(metta)
bounty_rag = BountyRAG(metta)

chat_proto = Protocol(spec=chat_protocol_spec)


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle intelligent bounty estimation queries with natural language processing"""

    text_content = next(
        (item for item in msg.content if isinstance(item, TextContent)),
        None
    )

    if not text_content:
        await ctx.send(sender, ChatMessage(
            content=[TextContent(text="❌ No text content")],
            timestamp=datetime.now(),
            msg_id=msg.msg_id
        ))
        return

    user_message = text_content.text.strip()
    ctx.logger.info(f"Processing intelligent bounty estimation: {user_message[:100]}")

    try:
        # Default values for natural language processing (will be updated from query)
        complexity_score = None
        required_skills = []
        estimated_hours = None
        repo_stars = 0

        # Try to parse as JSON first
        try:
            query = json.loads(user_message)
            if isinstance(query, dict):
                complexity_score = query.get("complexity_score")
                required_skills = query.get("required_skills", [])
                estimated_hours = query.get("estimated_hours")
                repo_stars = query.get("repo_stars", 0)
        except json.JSONDecodeError:
            # Natural language processing - extract information from text
            ctx.logger.info("Processing as natural language query")

            # Extract skills from text
            skill_keywords = {
                "python": "Python", "javascript": "JavaScript", "js": "JavaScript",
                "react": "React", "node": "Node.js", "nodejs": "Node.js",
                "java": "Java", "go": "Go", "rust": "Rust",
                "typescript": "TypeScript", "ts": "TypeScript",
                "solidity": "Solidity", "blockchain": "Blockchain",
                "fastapi": "FastAPI", "django": "Django"
            }

            message_lower = user_message.lower()
            for keyword, skill_name in skill_keywords.items():
                if keyword in message_lower:
                    if skill_name not in required_skills:
                        required_skills.append(skill_name)

            # Extract complexity (look for keywords)
            if any(word in message_lower for word in ["trivial", "simple", "easy"]):
                complexity_score = 3
            elif any(word in message_lower for word in ["moderate", "medium"]):
                complexity_score = 5
            elif any(word in message_lower for word in ["hard", "difficult", "complex"]):
                complexity_score = 7
            elif any(word in message_lower for word in ["very hard", "expert", "advanced"]):
                complexity_score = 9

            # Extract hours (look for patterns like "20 hours", "10h", "5-10 hours")
            import re
            hours_match = re.search(r'(\d+)\s*(?:hours?|hrs?|h)', message_lower)
            if hours_match:
                estimated_hours = int(hours_match.group(1))

            # Extract stars (look for patterns like "5000 stars", "5k stars")
            stars_match = re.search(r'(\d+)k?\s*stars?', message_lower)
            if stars_match:
                stars_value = int(stars_match.group(1))
                repo_stars = stars_value * 1000 if 'k' in stars_match.group(0) else stars_value

            # Apply intelligent defaults only if we have SOME information
            if not complexity_score:
                complexity_score = 5  # Default to moderate if not specified

            if not estimated_hours:
                estimated_hours = 10  # Default to 10 hours if not specified

        # Validate that we have minimum required information
        if complexity_score is None or estimated_hours is None:
            await ctx.send(sender, ChatMessage(
                content=[TextContent(text="""🤖 **Bounty Estimator Agent**

I need more information to estimate the bounty value.

**Try asking like:**
• "Estimate a moderate complexity Python task, 20 hours, 5000 stars"
• "Hard Rust bounty, 15 hours on a 10k star repo"
• Or send JSON: `{"complexity_score": 7, "required_skills": ["Python"], "estimated_hours": 20, "repo_stars": 5000}`

**What I need:**
• Complexity level (1-10 or easy/moderate/hard)
• Estimated hours
• Skills required (optional)
• Repository stars (optional)""")],
                timestamp=datetime.now(),
                msg_id=msg.msg_id
            ))
            return

        ctx.logger.info(f"Detected: complexity={complexity_score}, skills={required_skills}, hours={estimated_hours}, stars={repo_stars}")

        # Use MeTTa AI for intelligent bounty estimation
        response = bounty_rag.generate_intelligent_response(
            complexity_score=complexity_score,
            skills=required_skills,
            hours=estimated_hours,
            repo_stars=repo_stars
        )

        await ctx.send(sender, ChatMessage(
            content=[TextContent(text=response.strip())],
            timestamp=datetime.now(),
            msg_id=msg.msg_id
        ))

    except Exception as e:
        ctx.logger.error(f"Error: {e}")
        await ctx.send(sender, ChatMessage(
            content=[TextContent(text=f"❌ Error: {str(e)}")],
            timestamp=datetime.now(),
            msg_id=msg.msg_id
        ))


def _get_bounty_tier(value: int) -> str:
    """Get bounty tier"""
    if value >= 1000:
        return "XLarge"
    elif value >= 500:
        return "Large"
    elif value >= 200:
        return "Medium"
    elif value >= 50:
        return "Small"
    else:
        return "Micro"


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Ack from {sender}")


agent.include(chat_proto, publish_manifest=True)


# REST endpoint for orchestrator
class BountyEstimateRequest(Model):
    complexity_score: int
    required_skills: list
    estimated_hours: int
    repo_stars: int = 500


class BountyEstimateResponse(Model):
    response: str
    estimated_value: int
    min_value: int
    max_value: int
    hourly_rate: float
    tier: str


@agent.on_rest_post("/api/query", BountyEstimateRequest, BountyEstimateResponse)
async def handle_rest_query(ctx: Context, req: BountyEstimateRequest) -> BountyEstimateResponse:
    """REST endpoint for orchestrator to query this agent - INTELLIGENT RAG with MeTTa"""

    ctx.logger.info(f"REST: Intelligent RAG bounty estimation - Complexity: {req.complexity_score}, Hours: {req.estimated_hours}")

    # 🔍 STEP 1: RAG RETRIEVAL - Search for similar bounty estimates in Supabase
    ctx.logger.info(f"🔍 RAG RETRIEVAL: Searching for similar bounty estimates...")
    historical_data = await supabase_client.search_similar_bounty_estimates(
        complexity_score=req.complexity_score,
        required_skills=req.required_skills,
        estimated_hours=req.estimated_hours,
        limit=5
    )
    ctx.logger.info(f"✅ Found {len(historical_data)} similar bounty estimates in knowledge base")

    # 🧠 STEP 2: RAG AUGMENTATION - Use MeTTa AI + historical data for intelligent estimation
    response = bounty_rag.generate_intelligent_response(
        complexity_score=req.complexity_score,
        skills=req.required_skills,
        hours=req.estimated_hours,
        repo_stars=req.repo_stars,
        historical_data=historical_data  # ← RAG historical data!
    )

    # Get detailed estimation for response fields
    estimate = bounty_rag.calculate_intelligent_estimate(
        complexity_score=req.complexity_score,
        skills=req.required_skills,
        hours=req.estimated_hours,
        repo_stars=req.repo_stars
    )

    # 💾 STEP 3: RAG STORAGE - Store new bounty pattern in Supabase for future learning
    ctx.logger.info(f"💾 RAG STORAGE: Saving new bounty pattern to knowledge base...")
    asyncio.create_task(supabase_client.store_bounty_estimation_pattern(
        agent_id=agent.address,
        complexity_score=req.complexity_score,
        required_skills=req.required_skills,
        estimated_hours=req.estimated_hours,
        estimated_value=estimate['estimated_value'],
        hourly_rate=estimate['hourly_rate'],
        tier=estimate['tier'],
        repo_stars=req.repo_stars
    ))

    return BountyEstimateResponse(
        response=response,
        estimated_value=estimate['estimated_value'],
        min_value=estimate['min_value'],
        max_value=estimate['max_value'],
        hourly_rate=estimate['hourly_rate'],
        tier=estimate['tier']
    )


if __name__ == "__main__":
    agent.run()
