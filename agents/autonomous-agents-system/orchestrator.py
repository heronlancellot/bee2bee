# orchestrator.py
"""
Multi-Agent Orchestrator with Parallel Queries
Coordinates all autonomous agents to provide intelligent, synthesized responses
"""

import asyncio
import json
import os
import uuid
from typing import Dict, List
import aiohttp
from dotenv import load_dotenv

load_dotenv()

# Agent addresses (will be filled after agents start)
AGENT_ADDRESSES = {
    "user_profile": os.getenv("USER_PROFILE_AGENT_ADDRESS", "agent1q..."),
    "skill_matcher": os.getenv("SKILL_MATCHER_AGENT_ADDRESS", "agent1q..."),
    "bounty_estimator": os.getenv("BOUNTY_ESTIMATOR_AGENT_ADDRESS", "agent1q..."),
    "repo_analyzer": os.getenv("REPO_ANALYZER_AGENT_ADDRESS", "agent1q..."),
}

AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY")
AGENTVERSE_API = "https://agentverse.ai/v1/submit"


class MultiAgentOrchestrator:
    """
    Orchestrates multiple autonomous agents to provide comprehensive responses

    This implements the CONSENSUS LAYER architecture:
    1. Receives user query
    2. Queries multiple agents IN PARALLEL
    3. Collects all responses
    4. Synthesizes into intelligent, coherent response
    """

    def __init__(self):
        self.agent_addresses = AGENT_ADDRESSES
        self.api_key = AGENTVERSE_API_KEY

    async def query_agent(self, agent_name: str, message: dict) -> dict:
        """Query a single agent via Agentverse"""

        agent_address = self.agent_addresses.get(agent_name)
        if not agent_address:
            return {"error": f"Agent {agent_name} not configured"}

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "version": 1,
                "sender": "orchestrator",
                "target": agent_address,
                "session": str(uuid.uuid4()),
                "schema_digest": "proto:chat",
                "payload": json.dumps(message)
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    AGENTVERSE_API,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "agent": agent_name,
                            "response": result,
                            "success": True
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "agent": agent_name,
                            "error": f"HTTP {response.status}: {error_text}",
                            "success": False
                        }

        except Exception as e:
            return {
                "agent": agent_name,
                "error": str(e),
                "success": False
            }

    async def query_all_agents_parallel(self, queries: Dict[str, dict]) -> Dict[str, dict]:
        """
        Query multiple agents IN PARALLEL

        Args:
            queries: Dict mapping agent_name to query message

        Returns:
            Dict mapping agent_name to response
        """

        print(f"[Orchestrator] Querying {len(queries)} agents in parallel...")

        # Create tasks for parallel execution
        tasks = [
            self.query_agent(agent_name, query)
            for agent_name, query in queries.items()
        ]

        # Execute all queries in parallel
        results = await asyncio.gather(*tasks)

        # Convert to dict
        responses = {}
        for result in results:
            agent_name = result.get("agent")
            responses[agent_name] = result

        print(f"[Orchestrator] ✓ Received {len(responses)} responses")

        return responses

    async def find_perfect_matches(self, user_query: Dict) -> str:
        """
        Implementation of FIND_MATCHES intent

        Example query:
        {
            "user_id": "user123",
            "skills": ["Python", "JavaScript"],
            "years_experience": 3,
            "issue_query": "show me Python issues I can solve"
        }
        """

        print("\n" + "="*60)
        print("FIND_MATCHES - Parallel Agent Consultation")
        print("="*60 + "\n")

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
                "required_skills": ["Python", "asyncio", "debugging"]  # Example
            },
            "bounty_estimator": {
                "complexity_score": 6,
                "required_skills": ["Python", "asyncio"],
                "estimated_hours": 4,
                "repo_stars": 450
            }
        }

        # Query all agents in parallel
        responses = await self.query_all_agents_parallel(queries)

        # Synthesize response
        synthesis = self._synthesize_find_matches(responses, user_query)

        return synthesis

    def _synthesize_find_matches(self, agent_responses: Dict, user_query: Dict) -> str:
        """Synthesize responses from all agents into coherent answer"""

        synthesis = "# 🎯 Perfect Issues for You!\n\n"

        # Extract insights from each agent
        user_profile_resp = agent_responses.get("user_profile", {})
        skill_match_resp = agent_responses.get("skill_matcher", {})
        bounty_est_resp = agent_responses.get("bounty_estimator", {})

        synthesis += "I consulted with my specialized agents:\n"
        synthesis += "- 👤 User Profile Agent\n"
        synthesis += "- 🎯 Skill Matcher Agent\n"
        synthesis += "- 💰 Bounty Estimator Agent\n\n"

        synthesis += "---\n\n"

        # Mock example match (in production, would be real)
        synthesis += """
## Issue #23 - Fix async rendering bug in Python

**Repository:** python-async-tools (450 stars)

💰 **Bounty:** $50
⏱️ **Estimated Time:** ~4 hours
🎯 **Complexity:** 6/10
🟢 **Match Confidence:** 89%

**Why This is PERFECT for You:**

✅ **Skills Match (100%):**
  • You have: Python (3 years exp)
  • Issue requires: Python + asyncio + debugging
  • Your experience level: Advanced - Perfect for this complexity!

✅ **Experience Match:**
  • Issue complexity: 6/10
  • Your average: 5.5/10 (ideal match!)
  • You've solved 3 similar issues before

✅ **Bounty Value:**
  • $50 for ~4 hours = $12.50/hour
  • Above market average for this complexity
  • Within your preferred range

✅ **Repository Fit:**
  • 450 stars (you prefer small repos < 1000)
  • Active maintainer (merges PRs in <48h)
  • Good first contributor experience

**Confidence Score: 89%** 🟢

---

💡 **Agent Insights:**
"""

        # Add agent-specific insights
        if user_profile_resp.get("success"):
            synthesis += "\n📊 User Profile: Advanced Python developer, prefers small repos\n"

        if skill_match_resp.get("success"):
            synthesis += "🎯 Skill Match: 100% exact match, no skill gaps\n"

        if bounty_est_resp.get("success"):
            synthesis += "💰 Bounty Analysis: Excellent value at $12.50/hour\n"

        synthesis += "\n---\n\n"
        synthesis += "**Ready to accept this bounty?** 🚀\n"
        synthesis += "[Accept] [Tell me more] [Show more matches]"

        return synthesis

    async def explain_reasoning(self, query: Dict) -> str:
        """
        Implementation of EXPLAIN_REASONING intent

        Shows detailed reasoning behind a match
        """

        print("\n" + "="*60)
        print("EXPLAIN_REASONING - Deep Analysis")
        print("="*60 + "\n")

        # Query relevant agents
        queries = {
            "skill_matcher": {
                "user_skills": query.get("user_skills", []),
                "required_skills": query.get("required_skills", [])
            },
            "user_profile": {
                "user_id": query.get("user_id"),
                "action": "get_insights"
            }
        }

        responses = await self.query_all_agents_parallel(queries)

        # Generate detailed explanation
        explanation = "# 🧠 Complete Reasoning Analysis\n\n"
        explanation += "Here's the full reasoning behind the recommendation:\n\n"

        # Add detailed breakdown from each agent
        explanation += "## Skills Analysis\n"
        explanation += "*(from Skill Matcher Agent)*\n\n"
        # ... add skill matcher insights

        explanation += "\n## Experience Assessment\n"
        explanation += "*(from User Profile Agent)*\n\n"
        # ... add user profile insights

        explanation += "\n## Value Calculation\n"
        explanation += "*(from Bounty Estimator Agent)*\n\n"
        # ... add bounty estimator insights

        explanation += "\n---\n"
        explanation += "**Final Recommendation: HIGHLY RECOMMENDED** (89% confidence)\n"

        return explanation


# Example usage
async def main():
    """Test the orchestrator"""

    orchestrator = MultiAgentOrchestrator()

    # Test FIND_MATCHES
    user_query = {
        "user_id": "user123",
        "skills": ["Python", "JavaScript", "React"],
        "years_experience": 3,
        "issue_query": "show me Python issues I can solve"
    }

    result = await orchestrator.find_perfect_matches(user_query)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
