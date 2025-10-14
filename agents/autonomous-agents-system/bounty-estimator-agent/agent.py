# bounty-estimator-agent/agent.py
"""
Bounty Estimator Agent - Estimates bounty values using MeTTa reasoning
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
    name="Bounty Estimator Agent",
    seed="bounty_estimator_bee2bee_2025_agent",
    port=8011,
    mailbox=True,
    publish_agent_details=True
)

chat_proto = Protocol(spec=chat_protocol_spec)


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle bounty estimation queries"""

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
    ctx.logger.info(f"Processing bounty estimation: {user_message[:100]}")

    try:
        query = json.loads(user_message)

        # Extract issue details
        complexity_score = query.get("complexity_score", 5)
        required_skills = query.get("required_skills", [])
        estimated_hours = query.get("estimated_hours", 10)
        repo_stars = query.get("repo_stars", 500)

        # Use shared KB for complexity assessment
        complexity_level = shared_kb.query_complexity_level(complexity_score)

        # Base rates by complexity
        base_rates = {
            "trivial": 25,
            "easy": 50,
            "moderate": 100,
            "hard": 200,
            "very-hard": 400
        }

        base_value = base_rates.get(complexity_level, 100)

        # Adjust by hours
        value_by_hours = estimated_hours * 10  # $10/hour base

        # Adjust by tech stack (some skills worth more)
        premium_skills = ["Rust", "Go", "Solidity", "Kotlin", "Swift"]
        has_premium = any(skill in premium_skills for skill in required_skills)
        tech_multiplier = 1.3 if has_premium else 1.0

        # Adjust by repo popularity
        pop_multiplier = 1.0
        if repo_stars > 10000:
            pop_multiplier = 1.5
        elif repo_stars > 1000:
            pop_multiplier = 1.2

        # Calculate final estimate
        estimated_value = int(base_value * tech_multiplier * pop_multiplier)
        min_value = int(estimated_value * 0.8)
        max_value = int(estimated_value * 1.3)

        # Calculate hourly rate
        hourly_rate = estimated_value / estimated_hours if estimated_hours > 0 else 0

        response = f"""
💰 **Bounty Estimation**

**Complexity:** {complexity_level.title()} ({complexity_score}/10)
**Estimated Time:** ~{estimated_hours} hours
**Repository:** {repo_stars} stars

**Estimated Value:** ${min_value} - ${max_value}
**Recommended:** ${estimated_value}
**Hourly Rate:** ~${hourly_rate:.2f}/hour

**Breakdown:**
• Base (complexity): ${base_value}
• Tech multiplier: {tech_multiplier}x {"(premium skills)" if has_premium else ""}
• Popularity multiplier: {pop_multiplier}x

**Tier:** {_get_bounty_tier(estimated_value)}

💡 **Recommendation:**
"""
        if hourly_rate >= 15:
            response += f"Excellent value at ${hourly_rate:.2f}/hour!"
        elif hourly_rate >= 10:
            response += f"Good value at ${hourly_rate:.2f}/hour"
        else:
            response += f"Consider negotiating - ${hourly_rate:.2f}/hour is below market"

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

if __name__ == "__main__":
    agent.run()
