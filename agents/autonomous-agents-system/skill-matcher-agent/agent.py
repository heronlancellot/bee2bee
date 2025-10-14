# skill-matcher-agent/agent.py
"""
Intelligent Skill Matcher Agent - Uses MeTTa reasoning and natural language processing
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
from hyperon import MeTTa

# Import MeTTa components
from metta.knowledge import initialize_skill_knowledge_graph
from metta.skillrag import SkillRAG

# Import Supabase agent client
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from supabase_agent_client import create_supabase_agent_client

load_dotenv()

agent = Agent(
    name="Intelligent Skill Matcher Agent",
    seed="skill_matcher_bee2bee_2025_agent",
    port=8010,
    mailbox=True,
    publish_agent_details=True
)

# Initialize MeTTa components
metta = MeTTa()
initialize_skill_knowledge_graph(metta)
skill_rag = SkillRAG(metta)

# Initialize Supabase agent client
supabase_client = create_supabase_agent_client()

chat_proto = Protocol(spec=chat_protocol_spec)


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle intelligent skill matching queries with natural language processing"""

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
    ctx.logger.info(f"Processing intelligent skill match query: {user_message[:100]}")

    try:
        # Intelligent skill extraction from natural language
        user_skills = skill_rag.extract_skills_from_text(user_message)
        
        # Check if this is actually a skill-related query
        skill_keywords = ["skill", "know", "experience", "programming", "coding", "development", 
                         "python", "javascript", "react", "match", "project", "work", "bounty"]
        
        is_skill_query = any(keyword in user_message.lower() for keyword in skill_keywords)
        
        if not is_skill_query and not user_skills:
            # This is not a skill-related query, provide helpful response
            await ctx.send(sender, ChatMessage(
                content=[TextContent(text=f"""🤖 **Intelligent Skill Matcher Agent**

I'm specialized in skill matching and analysis! 

**Try asking me:**
• "I know Python and React, find me suitable projects"
• "Match me with JavaScript bounties"
• "What skills do I need for backend development?"
• "I have frontend experience, what can I work on?"

**Your message:** "{user_message}"

I can analyze your skills and match them with project requirements using MeTTa reasoning! 🧠""")],
                timestamp=datetime.now(),
                msg_id=msg.msg_id
            ))
            return
        
        # Try to parse JSON if it looks like structured data
        try:
            query_data = json.loads(user_message)
            if isinstance(query_data, dict):
                user_skills = query_data.get("user_skills", user_skills)
                required_skills = query_data.get("required_skills", [])
            else:
                required_skills = []
        except json.JSONDecodeError:
            # Natural language processing - infer required skills from context
            required_skills = skill_rag.extract_skills_from_text(user_message)
            # Add some common requirements if none detected
            if not required_skills:
                required_skills = ["Python", "JavaScript", "React"]

        ctx.logger.info(f"Detected user skills: {user_skills}")
        ctx.logger.info(f"Detected required skills: {required_skills}")

        if not required_skills:
            await ctx.send(sender, ChatMessage(
                content=[TextContent(text="❌ Could not determine required skills from your message")],
                timestamp=datetime.now(),
                msg_id=msg.msg_id
            ))
            return

        # Intelligent skill matching using MeTTa reasoning
        relationships = skill_rag.find_skill_relationships(user_skills, required_skills)
        match_score, confidence = skill_rag.calculate_match_score(relationships, required_skills)
        
        # Generate intelligent response
        response = skill_rag.generate_intelligent_response(
            user_skills, required_skills, relationships, match_score, confidence
        )

        # Store knowledge in Supabase for learning
        asyncio.create_task(supabase_client.store_skill_match_pattern(
            agent_id=agent.address,
            user_skills=user_skills,
            required_skills=required_skills,
            match_score=match_score,
            confidence=confidence,
            relationships=relationships
        ))

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
class SkillMatchRequest(Model):
    user_skills: list
    required_skills: list


class SkillMatchResponse(Model):
    response: str
    match_score: float
    confidence: float
    exact_matches: list
    missing_skills: list


@agent.on_rest_post("/api/query", SkillMatchRequest, SkillMatchResponse)
async def handle_rest_query(ctx: Context, req: SkillMatchRequest) -> SkillMatchResponse:
    """REST endpoint for orchestrator to query this intelligent agent"""

    ctx.logger.info(f"REST: Intelligent skill matching - User: {req.user_skills}, Required: {req.required_skills}")

    # Use intelligent skill matching
    relationships = skill_rag.find_skill_relationships(req.user_skills, req.required_skills)
    match_score, confidence = skill_rag.calculate_match_score(relationships, req.required_skills)
    
    # Generate intelligent response
    response = skill_rag.generate_intelligent_response(
        req.user_skills, req.required_skills, relationships, match_score, confidence
    )

    # Store knowledge in Supabase for learning
    asyncio.create_task(supabase_client.store_skill_match_pattern(
        agent_id=agent.address,
        user_skills=req.user_skills,
        required_skills=req.required_skills,
        match_score=match_score,
        confidence=confidence,
        relationships=relationships
    ))

    return SkillMatchResponse(
        response=response,
        match_score=match_score,
        confidence=confidence,
        exact_matches=relationships["exact_matches"],
        missing_skills=[skill for skill in req.required_skills if skill not in relationships["exact_matches"]]
    )


if __name__ == "__main__":
    agent.run()
