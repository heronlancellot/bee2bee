# skill-matcher-agent/agent.py
"""
Skill Matcher Agent - Matches skills with requirements using MeTTa reasoning
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

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.knowledge_base import shared_kb

load_dotenv()

agent = Agent(
    name="Skill Matcher Agent",
    seed="skill_matcher_bee2bee_2025_agent",
    port=8010,
    mailbox=True,
    publish_agent_details=True
)

chat_proto = Protocol(spec=chat_protocol_spec)


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle skill matching queries"""

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
    ctx.logger.info(f"Processing skill match query: {user_message[:100]}")

    try:
        query = json.loads(user_message)
        user_skills = query.get("user_skills", [])
        required_skills = query.get("required_skills", [])

        if not required_skills:
            await ctx.send(sender, ChatMessage(
                content=[TextContent(text="❌ required_skills needed")],
                timestamp=datetime.now(),
                msg_id=msg.msg_id
            ))
            return

        # Calculate match using shared KB
        exact_matches = [s for s in user_skills if s in required_skills]
        missing_skills = [s for s in required_skills if s not in user_skills]

        # Calculate match percentage
        match_score = (len(exact_matches) / len(required_skills)) * 100 if required_skills else 0

        # Determine domains using shared KB
        user_domains = [shared_kb.query_language_domain(skill) for skill in user_skills]
        required_domains = [shared_kb.query_language_domain(skill) for skill in required_skills]

        # Check for related domains
        related_matches = []
        for req_skill in missing_skills:
            req_domain = shared_kb.query_language_domain(req_skill)
            if req_domain in user_domains:
                related_skill = [s for s in user_skills if shared_kb.query_language_domain(s) == req_domain][0]
                related_matches.append({
                    "required": req_skill,
                    "user_has": related_skill,
                    "domain": req_domain
                })

        # Calculate confidence
        confidence = min(100, match_score + (len(related_matches) * 10))

        # Share pattern with KB
        if match_score > 80:
            shared_kb.add_match_pattern({
                "user_skills": user_skills,
                "required_skills": required_skills,
                "match_score": match_score,
                "success": True
            })

        response = f"""
🎯 **Skill Match Analysis**

**Match Score:** {match_score:.0f}%
**Confidence:** {confidence:.0f}%

✅ **Exact Matches ({len(exact_matches)}):**
{', '.join(exact_matches) if exact_matches else '  None'}

🔄 **Related Skills ({len(related_matches)}):**
"""
        for rm in related_matches:
            response += f"\n  • You have {rm['user_has']} (related to {rm['required']} via {rm['domain']})"

        if missing_skills:
            response += f"\n\n❌ **Missing Skills ({len(missing_skills)}):**\n"
            response += '\n'.join([f"  • {skill}" for skill in missing_skills])

        response += f"\n\n💡 **Recommendation:** "
        if confidence >= 80:
            response += "HIGHLY RECOMMENDED - Great match!"
        elif confidence >= 60:
            response += "RECOMMENDED - Good match with some learning needed"
        else:
            response += "CONSIDER - Significant skill gap"

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

if __name__ == "__main__":
    agent.run()
