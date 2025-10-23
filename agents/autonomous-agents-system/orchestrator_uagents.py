# orchestrator_uagents.py
"""
Multi-Agent Orchestrator using uAgents library for direct communication
"""

import asyncio
import json
import os
from typing import Dict
from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent
from datetime import datetime
import uuid
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
    name="Orchestrator",
    seed="orchestrator_bee2bee_2025",
    port=8000,
    mailbox=True
)

# Storage for responses
responses_storage = {}


@orchestrator.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Orchestrator started!")
    ctx.logger.info(f"Orchestrator address: {orchestrator.address}")


async def query_agent_via_uagents(ctx: Context, agent_name: str, message: dict) -> dict:
    """Query a single agent using uagents messaging"""

    agent_address = AGENT_ADDRESSES.get(agent_name)
    if not agent_address:
        return {"error": f"Agent {agent_name} not configured", "success": False}

    try:
        # Create ChatMessage
        chat_msg = ChatMessage(
            content=[TextContent(text=json.dumps(message))],
            timestamp=datetime.now(),
            msg_id=str(uuid.uuid4())
        )

        # Send message to agent
        await ctx.send(agent_address, chat_msg)

        ctx.logger.info(f"Sent message to {agent_name} at {agent_address}")

        # Wait for response (with timeout)
        # Note: This is simplified - in production, use proper async waiting
        await asyncio.sleep(2)  # Give agent time to respond

        # Check if response received
        response_key = f"{agent_name}_response"
        if response_key in responses_storage:
            response_data = responses_storage.pop(response_key)
            return {
                "agent": agent_name,
                "response": response_data,
                "success": True
            }
        else:
            return {
                "agent": agent_name,
                "error": "No response received (timeout)",
                "success": False
            }

    except Exception as e:
        return {
            "agent": agent_name,
            "error": str(e),
            "success": False
        }


async def query_all_agents_parallel(ctx: Context, queries: Dict[str, dict]) -> Dict[str, dict]:
    """
    Query multiple agents IN PARALLEL
    """

    ctx.logger.info(f"Querying {len(queries)} agents in parallel...")

    # Create tasks for parallel execution
    tasks = [
        query_agent_via_uagents(ctx, agent_name, query)
        for agent_name, query in queries.items()
    ]

    # Execute all queries in parallel
    results = await asyncio.gather(*tasks)

    # Convert to dict
    responses = {}
    for result in results:
        agent_name = result.get("agent")
        responses[agent_name] = result

    ctx.logger.info(f"✓ Received {len(responses)} responses")

    return responses


async def find_perfect_matches(ctx: Context, user_query: Dict) -> str:
    """
    Implementation of FIND_MATCHES intent
    """

    ctx.logger.info("="*60)
    ctx.logger.info("FIND_MATCHES - Parallel Agent Consultation")
    ctx.logger.info("="*60)

    # Prepare queries for each agent
    queries = {
        "user_profile": {
            "user_id": user_query.get("user_id"),
            "skills": user_query.get("skills"),
            "years_experience": user_query.get("years_experience"),
            "action": "get_profile"
        },
        "skill_matcher": {
            "user_skills": user_query.get("skills", []),
            "required_skills": ["Python", "asyncio", "debugging"]
        },
        "bounty_estimator": {
            "complexity_score": 6,
            "required_skills": ["Python", "asyncio"],
            "estimated_hours": 4,
            "repo_stars": 450
        }
    }

    # Query all agents in parallel
    responses = await query_all_agents_parallel(ctx, queries)

    # Synthesize response
    synthesis = _synthesize_find_matches(responses, user_query)

    return synthesis


def _synthesize_find_matches(agent_responses: Dict, user_query: Dict) -> str:
    """Synthesize responses from all agents into coherent answer"""

    synthesis = "# 🎯 Perfect Issues for You!\n\n"

    user_profile_resp = agent_responses.get("user_profile", {})
    skill_match_resp = agent_responses.get("skill_matcher", {})
    bounty_est_resp = agent_responses.get("bounty_estimator", {})

    synthesis += "I consulted with my specialized agents:\n"
    synthesis += "- 👤 User Profile Agent\n"
    synthesis += "- 🎯 Skill Matcher Agent\n"
    synthesis += "- 💰 Bounty Estimator Agent\n\n"
    synthesis += "---\n\n"

    # Show actual responses
    if user_profile_resp.get("success"):
        synthesis += f"## 👤 User Profile\n{user_profile_resp.get('response', 'N/A')}\n\n"

    if skill_match_resp.get("success"):
        synthesis += f"## 🎯 Skill Match\n{skill_match_resp.get('response', 'N/A')}\n\n"

    if bounty_est_resp.get("success"):
        synthesis += f"## 💰 Bounty Estimate\n{bounty_est_resp.get('response', 'N/A')}\n\n"

    synthesis += "\n---\n\n"
    synthesis += "**Ready to accept this bounty?** 🚀\n"

    return synthesis


# Handler to receive responses from agents
@orchestrator.on_message(ChatMessage)
async def handle_agent_response(ctx: Context, sender: str, msg: ChatMessage):
    """Handle responses from queried agents"""

    ctx.logger.info(f"Received response from {sender}")

    # Extract text content
    text_content = next(
        (item for item in msg.content if isinstance(item, TextContent)),
        None
    )

    if text_content:
        # Determine which agent sent this
        for agent_name, agent_address in AGENT_ADDRESSES.items():
            if sender == agent_address:
                responses_storage[f"{agent_name}_response"] = text_content.text
                ctx.logger.info(f"Stored response from {agent_name}")
                break


# Test function - runs every 30 seconds
test_executed = False

@orchestrator.on_interval(period=30.0)
async def test_query(ctx: Context):
    """Test querying agents"""
    global test_executed

    if test_executed:
        return  # Only run once

    test_executed = True

    ctx.logger.info("\n🚀 Starting parallel agent queries...\n")

    user_query = {
        "user_id": "user123",
        "skills": ["Python", "JavaScript", "React"],
        "years_experience": 3,
        "issue_query": "show me Python issues I can solve"
    }

    result = await find_perfect_matches(ctx, user_query)

    ctx.logger.info("\n" + "="*60)
    ctx.logger.info("📋 SYNTHESIZED RESPONSE:")
    ctx.logger.info("="*60 + "\n")
    ctx.logger.info(result)
    ctx.logger.info("\n" + "="*60 + "\n")


if __name__ == "__main__":
    print("🚀 Starting Orchestrator Agent...")
    print(f"Orchestrator address will be: {orchestrator.address}")
    print("\nMake sure all other agents are running before starting this!")
    print("\nStarting in 3 seconds...")

    import time
    time.sleep(3)

    orchestrator.run()
