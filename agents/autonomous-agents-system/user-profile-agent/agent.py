# user-profile-agent/agent.py
"""
User Profile Agent - Autonomous agent for user profile management
Manages user skills, preferences, history, and provides personalized insights
"""

from uagents import Context, Protocol, Agent
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)
import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add shared knowledge to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.knowledge_base import shared_kb

load_dotenv()

# Initialize agent
agent = Agent(
    name="User Profile Agent",
    seed="user_profile_bee2bee_2025_agent",
    port=8009,
    mailbox=True,
    publish_agent_details=True
)

chat_proto = Protocol(spec=chat_protocol_spec)


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle user profile queries"""

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
    ctx.logger.info(f"Processing user profile query: {user_message[:100]}")

    try:
        # Parse query (expect JSON with user_id and optionally action)
        query = json.loads(user_message)
        user_id = query.get("user_id")
        action = query.get("action", "get_profile")

        if not user_id:
            await ctx.send(sender, ChatMessage(
                content=[TextContent(text="❌ user_id required")],
                timestamp=datetime.now(),
                msg_id=msg.msg_id
            ))
            return

        # Mock profile data (in production, fetch from database)
        profile = {
            "user_id": user_id,
            "skills": query.get("skills", ["Python", "JavaScript"]),
            "years_experience": query.get("years_experience", 3),
            "completed_bounties": query.get("completed_bounties", 5),
            "avg_complexity": query.get("avg_complexity", 6),
            "preferences": {
                "min_bounty": query.get("min_bounty", 50),
                "max_bounty": query.get("max_bounty", 500),
                "repo_size_pref": "small",  # < 1000 stars
                "work_hours_per_week": 20
            }
        }

        # Use shared knowledge base
        skill_level = shared_kb.query_skill_level(profile["years_experience"])

        # Add insight to shared KB
        shared_kb.add_user_insight(user_id, {
            "skill_level": skill_level,
            "expertise": profile["skills"],
            "preferences": profile["preferences"]
        })

        # Generate response
        response = f"""
👤 **User Profile: {user_id}**

**Skills:** {', '.join(profile['skills'])}
**Experience Level:** {skill_level.title()} ({profile['years_experience']} years)
**Bounties Completed:** {profile['completed_bounties']}
**Avg Complexity Solved:** {profile['avg_complexity']}/10

**Preferences:**
- Bounty Range: ${profile['preferences']['min_bounty']} - ${profile['preferences']['max_bounty']}
- Repo Size: {profile['preferences']['repo_size_pref']}
- Available: {profile['preferences']['work_hours_per_week']}h/week

🧠 **Insight:** User prefers {profile['preferences']['repo_size_pref']} repos and mid-tier bounties.
        """

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
from uagents import Model

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
    """REST endpoint for orchestrator to query this agent"""

    ctx.logger.info(f"REST: Processing profile for {req.user_id}")

    # Use shared knowledge base
    skill_level = shared_kb.query_skill_level(req.years_experience)

    # Add insight to shared KB
    shared_kb.add_user_insight(req.user_id, {
        "skill_level": skill_level,
        "expertise": req.skills,
    })

    # Generate response
    response = f"""👤 **User Profile: {req.user_id}**

**Skills:** {', '.join(req.skills) if req.skills else 'No skills provided'}
**Experience Level:** {skill_level.title()} ({req.years_experience} years)

🧠 **Insight:** {skill_level.title()} developer with {len(req.skills)} skills"""

    return ProfileResponse(
        response=response,
        skill_level=skill_level,
        user_id=req.user_id
    )


if __name__ == "__main__":
    agent.run()
