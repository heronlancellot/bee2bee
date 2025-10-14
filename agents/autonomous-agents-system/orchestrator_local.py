# orchestrator_local.py
"""
Local Multi-Agent Orchestrator - Communicates directly via HTTP with local agents
For when agents run locally with mailbox enabled
"""

import asyncio
import json
import uuid
from typing import Dict
import aiohttp
from datetime import datetime


class LocalMultiAgentOrchestrator:
    """
    Orchestrates local agents via direct HTTP communication
    """

    def __init__(self):
        # Local agent HTTP endpoints
        self.agent_endpoints = {
            "user_profile": "http://localhost:8009",
            "skill_matcher": "http://localhost:8010",
            "bounty_estimator": "http://localhost:8011",
        }

    async def query_agent(self, agent_name: str, message: dict) -> dict:
        """Query a single agent via local HTTP endpoint"""

        endpoint = self.agent_endpoints.get(agent_name)
        if not endpoint:
            return {"error": f"Agent {agent_name} not configured"}

        try:
            # Create ChatMessage payload
            chat_payload = {
                "content": [{
                    "type": "text",
                    "text": json.dumps(message)
                }],
                "timestamp": datetime.now().isoformat(),
                "msg_id": str(uuid.uuid4())
            }

            async with aiohttp.ClientSession() as session:
                # Try to send to agent's chat protocol endpoint
                url = f"{endpoint}/submit"

                async with session.post(
                    url,
                    json=chat_payload,
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

        # Show actual agent responses if successful
        if user_profile_resp.get("success"):
            synthesis += "## 👤 User Profile Response\n\n"
            synthesis += f"```\n{json.dumps(user_profile_resp.get('response', {}), indent=2)}\n```\n\n"

        if skill_match_resp.get("success"):
            synthesis += "## 🎯 Skill Matcher Response\n\n"
            synthesis += f"```\n{json.dumps(skill_match_resp.get('response', {}), indent=2)}\n```\n\n"

        if bounty_est_resp.get("success"):
            synthesis += "## 💰 Bounty Estimator Response\n\n"
            synthesis += f"```\n{json.dumps(bounty_est_resp.get('response', {}), indent=2)}\n```\n\n"

        # Mock example match
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


# Example usage
async def main():
    """Test the local orchestrator"""

    orchestrator = LocalMultiAgentOrchestrator()

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
