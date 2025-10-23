#!/usr/bin/env python3
"""
Orchestrator bridge for Autonomous Agents
This bridges the old smart-agents interface with the new autonomous agents system
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any

# Add autonomous-agents-system to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'autonomous-agents-system'))

from orchestrator import MultiAgentOrchestrator


class AutonomousAgentsBridge:
    """
    Bridge between old smart-agents API and new autonomous agents
    """

    def __init__(self):
        self.orchestrator = MultiAgentOrchestrator()

    def detect_intent(self, message: str) -> str:
        """Simple intent detection"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["show", "find", "get", "issues", "bounties", "matches", "python", "javascript"]):
            return "FIND_MATCHES"
        elif any(word in message_lower for word in ["why", "explain", "reasoning", "how did you"]):
            return "EXPLAIN_REASONING"
        elif any(word in message_lower for word in ["profile", "my skills", "my history"]):
            return "USER_PROFILE"
        else:
            return "general_chat"

    def extract_skills_from_message(self, message: str) -> list:
        """Extract programming languages/skills from message"""
        common_skills = ["Python", "JavaScript", "TypeScript", "React", "Node.js",
                         "Go", "Rust", "Java", "C++", "Ruby", "PHP", "Swift", "Kotlin",
                         "asyncio", "FastAPI", "Django", "Flask", "Vue", "Angular"]

        found_skills = []
        message_lower = message.lower()

        for skill in common_skills:
            if skill.lower() in message_lower:
                found_skills.append(skill)

        return found_skills if found_skills else ["Python"]

    async def process_query_async(
        self,
        query: str,
        user_id: str = "anonymous",
        conversation_id: str = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process query using autonomous agents (async)"""

        intent = self.detect_intent(query)
        context = context or {}

        try:
            if intent == "FIND_MATCHES":
                # Extract skills
                skills = self.extract_skills_from_message(query)

                user_query = {
                    "user_id": user_id,
                    "skills": skills,
                    "years_experience": context.get("years_experience", 3),
                    "issue_query": query
                }

                # Call autonomous agents orchestrator
                response = await self.orchestrator.find_perfect_matches(user_query)

                return {
                    "response": response,
                    "intent": "FIND_MATCHES",
                    "intent_confidence": 0.9,
                    "agent_id": "orchestrator",
                    "conversation_id": conversation_id or "new_conversation",
                    "metadata": {
                        "agents_consulted": ["user_profile", "skill_matcher", "bounty_estimator"],
                        "query_mode": "parallel",
                        "reasoning_engine": "metta",
                        "skills_detected": skills
                    },
                    "timestamp": self._get_timestamp()
                }

            elif intent == "EXPLAIN_REASONING":
                skills = self.extract_skills_from_message(query)

                reasoning_query = {
                    "user_id": user_id,
                    "user_skills": skills,
                    "required_skills": context.get("required_skills", [])
                }

                response = await self.orchestrator.explain_reasoning(reasoning_query)

                return {
                    "response": response,
                    "intent": "EXPLAIN_REASONING",
                    "intent_confidence": 0.85,
                    "agent_id": "orchestrator",
                    "conversation_id": conversation_id or "new_conversation",
                    "metadata": {
                        "agents_consulted": ["user_profile", "skill_matcher"],
                        "query_mode": "parallel"
                    },
                    "timestamp": self._get_timestamp()
                }

            else:
                # General chat
                return {
                    "response": self._generate_general_response(query),
                    "intent": "general_chat",
                    "intent_confidence": 0.7,
                    "agent_id": "orchestrator",
                    "conversation_id": conversation_id or "new_conversation",
                    "metadata": {},
                    "timestamp": self._get_timestamp()
                }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "response": f"Error processing query: {str(e)}",
                "intent": "error",
                "intent_confidence": 1.0,
                "agent_id": "orchestrator",
                "conversation_id": conversation_id or "new_conversation",
                "metadata": {"error": str(e)},
                "timestamp": self._get_timestamp()
            }

    def process_query(self, query: str, user_id: str = "anonymous",
                     conversation_id: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Synchronous wrapper for async process_query"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self.process_query_async(query, user_id, conversation_id, context)
        )

    def _generate_general_response(self, query: str) -> str:
        """Generate response for general chat"""
        return f"""
🤖 **Autonomous Agents Orchestrator**

I understand you asked: "{query}"

I coordinate **3 specialized autonomous agents** with MeTTa reasoning:

**Available Commands:**
• "Show me Python issues I can solve"
• "Find JavaScript bounties for me"
• "Why did you recommend this match?"
• "Explain your reasoning"

**Agents:**
- 👤 User Profile Agent (port 8009)
- 🎯 Skill Matcher Agent (port 8010)
- 💰 Bounty Estimator Agent (port 8011)

**Features:**
✅ Parallel agent queries
✅ MeTTa symbolic reasoning
✅ Shared knowledge base
✅ Intelligent synthesis

What would you like to do?
"""

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of all autonomous agents"""
        return {
            "user_profile": {
                "name": "User Profile Agent",
                "capabilities": ["profile_management", "skill_tracking", "preferences", "history"],
                "port": 8009,
                "status": "active",
                "reasoning": "metta"
            },
            "skill_matcher": {
                "name": "Skill Matcher Agent",
                "capabilities": ["skill_matching", "gap_analysis", "domain_matching", "confidence_scoring"],
                "port": 8010,
                "status": "active",
                "reasoning": "metta"
            },
            "bounty_estimator": {
                "name": "Bounty Estimator Agent",
                "capabilities": ["bounty_estimation", "complexity_analysis", "value_calculation", "tier_classification"],
                "port": 8011,
                "status": "active",
                "reasoning": "metta"
            }
        }


# Singleton instance
_bridge = None


def get_bridge() -> AutonomousAgentsBridge:
    """Get or create bridge instance"""
    global _bridge
    if _bridge is None:
        _bridge = AutonomousAgentsBridge()
    return _bridge


# Compatibility function for old API
def process_user_query(query: str, user_id: str = "anonymous",
                      conversation_id: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Process user query (compatible with old smart_agents_server.py)
    """
    bridge = get_bridge()
    return bridge.process_query(query, user_id, conversation_id, context)


def get_orchestrator():
    """Get orchestrator for compatibility"""
    return get_bridge()
