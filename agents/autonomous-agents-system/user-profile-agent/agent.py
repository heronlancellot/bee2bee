# user-profile-agent/agent.py
"""
User Profile Agent - Autonomous agent for user profile management
Manages user skills, preferences, history, and provides personalized insights
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

# Add shared knowledge to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.knowledge_base import shared_kb
from supabase_agent_client import create_supabase_agent_client

# MeTTa imports for intelligent reasoning
from hyperon import MeTTa
from metta.knowledge import initialize_profile_knowledge_graph
from metta.profilerag import ProfileRAG

load_dotenv()

# Initialize Supabase client
supabase_client = create_supabase_agent_client()

# Initialize agent
agent = Agent(
    name="User Profile Agent",
    seed="user_profile_bee2bee_2025_agent",
    port=8009,
    mailbox=True,
    publish_agent_details=True
)

# Initialize MeTTa AI reasoning
metta = MeTTa()
initialize_profile_knowledge_graph(metta)
profile_rag = ProfileRAG(metta)

chat_proto = Protocol(spec=chat_protocol_spec)


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle intelligent user profile queries with natural language processing"""

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
    ctx.logger.info(f"Processing intelligent user profile query: {user_message[:100]}")

    try:
        # Default values for natural language processing
        import hashlib
        import uuid

        # Generate unique user_id based on sender or create anonymous ID
        user_id = f"user_{hashlib.md5(sender.encode()).hexdigest()[:8]}"
        skills = []
        years_experience = 0

        # Try to parse as JSON first
        try:
            query = json.loads(user_message)
            if isinstance(query, dict):
                user_id = query.get("user_id", user_id)
                skills = query.get("skills", [])
                years_experience = query.get("years_experience", 0)
        except json.JSONDecodeError:
            # Natural language processing - extract information from text
            ctx.logger.info("Processing as natural language query")

            # Extract skills from text (simple keyword matching)
            skill_keywords = {
                "python": "Python", "javascript": "JavaScript", "js": "JavaScript",
                "react": "React", "node": "Node.js", "nodejs": "Node.js",
                "java": "Java", "go": "Go", "rust": "Rust",
                "typescript": "TypeScript", "ts": "TypeScript",
                "fastapi": "FastAPI", "django": "Django"
            }

            message_lower = user_message.lower()
            for keyword, skill_name in skill_keywords.items():
                if keyword in message_lower:
                    if skill_name not in skills:
                        skills.append(skill_name)

            # Extract years of experience (look for patterns like "3 years", "5+ years")
            import re
            years_match = re.search(r'(\d+)\s*(?:years?|yrs?)', message_lower)
            if years_match:
                years_experience = int(years_match.group(1))

            # If NO skills or experience detected, inform user
            if not skills and years_experience == 0:
                await ctx.send(sender, ChatMessage(
                    content=[TextContent(text="""🤖 **User Profile Agent**

I couldn't extract skills or experience from your message.

**Try asking like:**
• "I'm a Python developer with 5 years of experience"
• "I know React, JavaScript and have 3 years experience"
• Or send JSON: `{"user_id": "your_id", "skills": ["Python"], "years_experience": 5}`

What are your skills and experience level?""")],
                    timestamp=datetime.now(),
                    msg_id=msg.msg_id
                ))
                return

        ctx.logger.info(f"Detected: user={user_id}, skills={skills}, years={years_experience}")

        # Use MeTTa AI for intelligent profile analysis
        response = profile_rag.generate_intelligent_profile(
            user_id=user_id,
            skills=skills,
            years=years_experience
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


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Ack from {sender}")


agent.include(chat_proto, publish_manifest=True)


# REST endpoint for orchestrator
class ProfileRequest(Model):
    user_id: str
    skills: list = []
    years_experience: int = 0
    action: str = "get_profile"


class ProfileResponse(Model):
    response: str
    skill_level: str
    user_id: str


@agent.on_rest_post("/api/query", ProfileRequest, ProfileResponse)
async def handle_rest_query(ctx: Context, req: ProfileRequest) -> ProfileResponse:
    """REST endpoint for orchestrator to query this agent - INTELLIGENT RAG with MeTTa"""

    ctx.logger.info(f"REST: Processing intelligent RAG profile for {req.user_id}")

    # 🔍 STEP 1: RAG RETRIEVAL - Search for similar profiles in Supabase
    ctx.logger.info(f"🔍 RAG RETRIEVAL: Searching for similar profiles...")
    historical_data = await supabase_client.search_similar_user_profiles(
        skills=req.skills if req.skills else [],
        years_experience=req.years_experience,
        limit=5
    )
    ctx.logger.info(f"✅ Found {len(historical_data)} similar profiles in knowledge base")

    # 🧠 STEP 2: RAG AUGMENTATION - Use MeTTa AI + historical data for intelligent analysis
    response = profile_rag.generate_intelligent_profile(
        user_id=req.user_id,
        skills=req.skills if req.skills else [],
        years=req.years_experience,
        historical_data=historical_data  # ← RAG historical data!
    )

    # Get skill level for backward compatibility
    skill_level = profile_rag.get_experience_level(req.years_experience)

    # Add insight to shared KB
    shared_kb.add_user_insight(req.user_id, {
        "skill_level": skill_level,
        "expertise": req.skills,
    })

    # 💾 STEP 3: RAG STORAGE - Store new profile pattern in Supabase for future learning
    ctx.logger.info(f"💾 RAG STORAGE: Saving new profile pattern to knowledge base...")
    asyncio.create_task(supabase_client.store_user_profile_pattern(
        agent_id=agent.address,
        user_id=req.user_id,
        skills=req.skills if req.skills else [],
        years_experience=req.years_experience,
        skill_level=skill_level,
        preferences={}
    ))

    return ProfileResponse(
        response=response,
        skill_level=skill_level,
        user_id=req.user_id
    )


if __name__ == "__main__":
    agent.run()
