# agent.py
"""
Bounty Matcher Agent
Autonomous agent that matches developers with perfect bounties/issues using MeTTa reasoning
"""

from hyperon import MeTTa
from uagents import Context, Model, Protocol, Agent
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Import MeTTa components
from metta.knowledge import initialize_bounty_knowledge
from metta.bountyrag import BountyRAG
from metta.utils import (
    fetch_github_issues,
    analyze_user_profile,
    find_best_matches,
    format_match_response,
    format_error_response
)
from metta.llm_synthesis import llm_synthesizer

# Load environment
load_dotenv()

# Initialize agent
agent = Agent(
    name="Bounty Matcher",
    seed="bounty_matcher_bee2bee_2025",
    port=8008,
    mailbox=True,
    publish_agent_details=True
)

# Initialize global MeTTa components
metta = MeTTa()
initialize_bounty_knowledge(metta)
rag = BountyRAG(metta)

# Protocol setup
chat_proto = Protocol(spec=chat_protocol_spec)


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages and match bounties"""

    # Extract text from message
    text_content = next(
        (item for item in msg.content if isinstance(item, TextContent)),
        None
    )

    if not text_content:
        await ctx.send(
            sender,
            ChatMessage(
                content=[
                    TextContent(text="❌ No text content found in message.")
                ],
                timestamp=datetime.now(),
                msg_id=msg.msg_id
            )
        )
        return

    user_message = text_content.text.strip()

    ctx.logger.info(f"Processing bounty match request: {user_message}")

    try:
        # Parse user message
        # Expected format: JSON with user profile and preferences
        # Example: {"skills": ["Python", "JavaScript"], "years_experience": 3, "preferences": {"min_bounty": 50}}

        # Try to parse as JSON first
        try:
            user_data = json.loads(user_message)
        except json.JSONDecodeError:
            # If not JSON, provide help message
            await ctx.send(
                sender,
                ChatMessage(
                    content=[
                        TextContent(
                            text="""❌ Invalid format. Please send your profile as JSON.

**Example:**
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

**Required fields:**
- skills: Array of your programming skills
- years_experience: Your total years of experience

**Optional fields:**
- preferences.min_bounty: Minimum bounty value
- preferences.max_bounty: Maximum bounty value
- preferences.max_hours_per_week: Max hours you can work"""
                        )
                    ],
                    timestamp=datetime.now(),
                    msg_id=msg.msg_id
                )
            )
            return

        # Validate user data
        if "skills" not in user_data or not user_data["skills"]:
            await ctx.send(
                sender,
                ChatMessage(
                    content=[
                        TextContent(text="❌ Error: 'skills' field is required and must not be empty.")
                    ],
                    timestamp=datetime.now(),
                    msg_id=msg.msg_id
                )
            )
            return

        # Analyze user profile
        user_profile = analyze_user_profile(user_data)

        ctx.logger.info(f"User profile: {user_profile.get('experience_level')} with {len(user_profile.get('skills', []))} skills")

        # Fetch bounties from multiple sources
        # For demo: fetch from common open source repos
        all_bounties = []

        demo_repos = [
            ("facebook", "react"),
            ("microsoft", "typescript"),
            ("python", "cpython"),
            ("nodejs", "node"),
            ("vuejs", "vue")
        ]

        for owner, repo in demo_repos:
            bounties = fetch_github_issues(owner, repo)
            all_bounties.extend(bounties)

        ctx.logger.info(f"Found {len(all_bounties)} total bounties")

        if not all_bounties:
            await ctx.send(
                sender,
                ChatMessage(
                    content=[
                        TextContent(
                            text="❌ No bounties found at the moment. Try again later."
                        )
                    ],
                    timestamp=datetime.now(),
                    msg_id=msg.msg_id
                )
            )
            return

        # Find best matches using MeTTa reasoning
        top_matches = find_best_matches(
            user_profile=user_profile,
            bounties=all_bounties,
            rag=rag,
            top_n=5
        )

        ctx.logger.info(f"Found {len(top_matches)} matches")

        # Generate intelligent response using LLM + MeTTa
        # MeTTa provides the REASONING, LLM provides the INTELLIGENCE
        try:
            ctx.logger.info("Synthesizing intelligent response with LLM...")
            response_text = llm_synthesizer.synthesize_matches(
                matches=top_matches,
                user_profile=user_profile,
                conversation_context=user_message
            )
            ctx.logger.info("✓ Intelligent response generated")
        except Exception as e:
            ctx.logger.warning(f"LLM synthesis failed, using fallback: {e}")
            # Fallback to basic formatting
            response_text = format_match_response(top_matches, user_profile)

        # Send response
        await ctx.send(
            sender,
            ChatMessage(
                content=[
                    TextContent(text=response_text)
                ],
                timestamp=datetime.now(),
                msg_id=msg.msg_id
            )
        )

        # Send acknowledgement
        await ctx.send(
            sender,
            ChatAcknowledgement(
                msg_id=msg.msg_id,
                ack_type="delivered"
            )
        )

    except Exception as e:
        ctx.logger.error(f"Error processing bounty match: {e}")
        await ctx.send(
            sender,
            ChatMessage(
                content=[
                    TextContent(text=format_error_response(str(e)))
                ],
                timestamp=datetime.now(),
                msg_id=msg.msg_id
            )
        )


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle acknowledgements"""
    ctx.logger.info(f"Received acknowledgement from {sender}: {msg.ack_type}")


# Register protocol
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
