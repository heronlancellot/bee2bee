"""
Consensus Synthesizer
Synthesizes responses from multiple agents into a coherent, intelligent response
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from llm_integration import llm_integration


class ConsensusSynthesizer:
    """
    Synthesizes responses from multiple agents into a unified, intelligent response

    This is the "Consensus Layer" that:
    - Collects responses from multiple agents queried in parallel
    - Analyzes and synthesizes the information
    - Generates intelligent, contextual responses with reasoning
    - Provides deep insights and recommendations
    """

    def __init__(self):
        self.synthesizer_id = "consensus_synthesizer"

    def synthesize_find_matches(self,
                               query: str,
                               user_id: str,
                               agent_responses: Dict[str, Dict],
                               conversation_history: List[Dict] = None) -> Dict:
        """
        Synthesize responses for FIND_MATCHES intent

        Args:
            query: User query
            user_id: User identifier
            agent_responses: Dict of agent_id -> response
            conversation_history: Previous conversation

        Returns:
            Synthesized response with reasoning
        """

        # Extract data from each agent
        user_profile_data = agent_responses.get("user_profile_agent", {}).get("metadata", {})
        repo_analysis_data = agent_responses.get("repo_analyzer", {}).get("metadata", {})
        skill_match_data = agent_responses.get("skill_matcher", {}).get("metadata", {})
        bounty_estimate_data = agent_responses.get("bounty_estimator", {}).get("metadata", {})

        # Build structured data for synthesis
        synthesis_data = {
            "user_profile": user_profile_data.get("result", {}),
            "repositories": repo_analysis_data.get("analysis", {}),
            "skill_matches": skill_match_data.get("match_result", {}),
            "bounty_estimates": bounty_estimate_data.get("estimation", {})
        }

        # Generate intelligent synthesis using LLM
        synthesized_response = self._generate_match_synthesis(
            query=query,
            synthesis_data=synthesis_data,
            agent_responses=agent_responses,
            conversation_history=conversation_history
        )

        return {
            "response": synthesized_response,
            "synthesizer_id": self.synthesizer_id,
            "metadata": {
                "synthesis_type": "find_matches",
                "agents_consulted": list(agent_responses.keys()),
                "synthesis_data": synthesis_data,
                "timestamp": datetime.now().isoformat()
            }
        }

    def synthesize_explain_reasoning(self,
                                     query: str,
                                     user_id: str,
                                     agent_responses: Dict[str, Dict],
                                     conversation_history: List[Dict] = None,
                                     context: Dict = None) -> Dict:
        """
        Synthesize responses for EXPLAIN_REASONING intent

        Args:
            query: User query
            user_id: User identifier
            agent_responses: Dict of agent_id -> response
            conversation_history: Previous conversation
            context: Additional context (e.g., what to explain)

        Returns:
            Synthesized explanation with deep reasoning
        """

        # Extract relevant data
        synthesis_data = {}
        for agent_id, response in agent_responses.items():
            synthesis_data[agent_id] = response.get("metadata", {})

        # Generate intelligent explanation
        explanation_response = self._generate_reasoning_explanation(
            query=query,
            synthesis_data=synthesis_data,
            agent_responses=agent_responses,
            conversation_history=conversation_history,
            context=context
        )

        return {
            "response": explanation_response,
            "synthesizer_id": self.synthesizer_id,
            "metadata": {
                "synthesis_type": "explain_reasoning",
                "agents_consulted": list(agent_responses.keys()),
                "synthesis_data": synthesis_data,
                "timestamp": datetime.now().isoformat()
            }
        }

    def synthesize_comprehensive_analysis(self,
                                         query: str,
                                         user_id: str,
                                         agent_responses: Dict[str, Dict],
                                         conversation_history: List[Dict] = None) -> Dict:
        """
        Synthesize responses for COMPREHENSIVE_ANALYSIS intent

        Args:
            query: User query
            user_id: User identifier
            agent_responses: Dict of agent_id -> response
            conversation_history: Previous conversation

        Returns:
            Comprehensive synthesized analysis
        """

        # Extract all data from agents
        synthesis_data = {}
        for agent_id, response in agent_responses.items():
            synthesis_data[agent_id] = {
                "response": response.get("response", ""),
                "metadata": response.get("metadata", {})
            }

        # Generate comprehensive synthesis
        comprehensive_response = self._generate_comprehensive_synthesis(
            query=query,
            synthesis_data=synthesis_data,
            agent_responses=agent_responses,
            conversation_history=conversation_history
        )

        return {
            "response": comprehensive_response,
            "synthesizer_id": self.synthesizer_id,
            "metadata": {
                "synthesis_type": "comprehensive_analysis",
                "agents_consulted": list(agent_responses.keys()),
                "synthesis_data": synthesis_data,
                "timestamp": datetime.now().isoformat()
            }
        }

    def _generate_match_synthesis(self,
                                  query: str,
                                  synthesis_data: Dict,
                                  agent_responses: Dict,
                                  conversation_history: List[Dict] = None) -> str:
        """Generate intelligent synthesis for match finding"""

        # Build system prompt for synthesis
        system_prompt = """
You are an expert synthesis agent that combines insights from multiple specialized agents to provide intelligent, actionable recommendations.

You have received insights from:
1. **User Profile Agent**: User's skills, preferences, experience, and history
2. **Repository Analyzer**: Analysis of available repositories and projects
3. **Skill Matcher**: Analysis of skill compatibility and gaps
4. **Bounty Estimator**: Estimation of bounty values and complexity

Your task is to synthesize these insights into a compelling, personalized recommendation that:
- Shows the TOP 3-5 most relevant issues/bounties for the user
- Explains WHY each match is perfect (reasoning)
- Includes specific details (bounty value, complexity, skills required)
- Provides confidence scores and recommendations
- Uses a conversational, engaging tone

Format your response like this example:

"Encontrei 3 issues perfeitas pra você! 🎯

**Issue #23 - python-async-tools**
💰 $50 | ⏱️ ~4 horas | ⭐ 450 stars
🔍 Por que combina:
  • Você tem exp. avançada em Python + asyncio
  • Similar ao issue que você resolveu semana passada
  • Repo pequeno (sua preferência)

[Accept Bounty] [Tell me more]

**Issue #45 - api-optimizer**
💰 $75 | ⏱️ ~6 horas | ⭐ 800 stars
🔍 Por que combina:
  • Envolve performance optimization (seu forte)
  • Maintainer responde rápido (95% em <24h)

[Accept Bounty] [Tell me more]

..."

Use the structured data provided to create this personalized, intelligent response.
"""

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history[-4:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        # Add current query with context
        user_message = f"""
User Query: {query}

Agent Insights:

**User Profile Data:**
{json.dumps(synthesis_data.get("user_profile", {}), indent=2)}

**Repository Analysis:**
{json.dumps(synthesis_data.get("repositories", {}), indent=2)}

**Skill Match Results:**
{json.dumps(synthesis_data.get("skill_matches", {}), indent=2)}

**Bounty Estimates:**
{json.dumps(synthesis_data.get("bounty_estimates", {}), indent=2)}

Please synthesize these insights into a compelling, personalized response for the user.
"""

        messages.append({"role": "user", "content": user_message})

        # Call LLM for synthesis
        try:
            response = llm_integration._call_openai_api(messages)
            return response
        except Exception as e:
            print(f"[ConsensusSynthesizer] Error generating synthesis: {e}")
            return self._fallback_match_synthesis(synthesis_data, agent_responses)

    def _generate_reasoning_explanation(self,
                                       query: str,
                                       synthesis_data: Dict,
                                       agent_responses: Dict,
                                       conversation_history: List[Dict] = None,
                                       context: Dict = None) -> str:
        """Generate intelligent explanation of reasoning"""

        system_prompt = """
You are an expert at explaining complex reasoning in a clear, accessible way.

You have access to insights from multiple specialized agents. Your task is to:
- Explain the REASONING behind recommendations
- Break down WHY certain matches were made
- Show the EVIDENCE and ANALYSIS that led to conclusions
- Provide CONFIDENCE SCORES and explain them
- Use a conversational, educational tone

Format your response to include:
1. **Main Reasoning**: Why this recommendation was made
2. **Skills Match Analysis**: Detailed skill compatibility
3. **Experience Match**: How user's experience aligns
4. **Preference Match**: How it fits user preferences
5. **Confidence Score**: Overall confidence with explanation
6. **Points of Attention**: Any concerns or considerations

Use emojis and clear formatting to make it engaging and easy to understand.
"""

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        if conversation_history:
            for msg in conversation_history[-4:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        user_message = f"""
User Query: {query}

Context: {json.dumps(context or {}, indent=2)}

Agent Data:
{json.dumps(synthesis_data, indent=2)}

Please explain the reasoning behind the recommendations in detail.
"""

        messages.append({"role": "user", "content": user_message})

        try:
            response = llm_integration._call_openai_api(messages)
            return response
        except Exception as e:
            print(f"[ConsensusSynthesizer] Error generating explanation: {e}")
            return self._fallback_reasoning_explanation(synthesis_data)

    def _generate_comprehensive_synthesis(self,
                                         query: str,
                                         synthesis_data: Dict,
                                         agent_responses: Dict,
                                         conversation_history: List[Dict] = None) -> str:
        """Generate comprehensive analysis synthesis"""

        system_prompt = """
You are an expert synthesis agent that combines ALL insights from multiple specialized agents into a comprehensive, coherent analysis.

You have insights from:
- Repository Analyzer
- Skill Matcher
- Bounty Estimator
- User Profile Agent

Your task is to create a COMPREHENSIVE analysis that:
- Synthesizes ALL agent insights
- Provides a holistic view
- Identifies patterns and connections
- Gives actionable recommendations
- Uses professional yet accessible language

Structure your response with clear sections and detailed analysis.
"""

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        if conversation_history:
            for msg in conversation_history[-4:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        user_message = f"""
User Query: {query}

All Agent Data:
{json.dumps(synthesis_data, indent=2)}

Please provide a comprehensive analysis synthesizing all these insights.
"""

        messages.append({"role": "user", "content": user_message})

        try:
            response = llm_integration._call_openai_api(messages)
            return response
        except Exception as e:
            print(f"[ConsensusSynthesizer] Error generating comprehensive synthesis: {e}")
            return self._fallback_comprehensive_synthesis(synthesis_data)

    def _fallback_match_synthesis(self, synthesis_data: Dict, agent_responses: Dict) -> str:
        """Fallback response when LLM is not available"""

        response = "## 🎯 Matches Found (Basic Mode)\n\n"
        response += "I've consulted multiple agents but need LLM integration for intelligent synthesis.\n\n"

        # Show basic data
        for agent_id, agent_response in agent_responses.items():
            response += f"### {agent_id.replace('_', ' ').title()}\n"
            response += f"{agent_response.get('response', 'No response')}\n\n"

        response += "\n💡 Configure OPENAI_API_KEY for intelligent synthesis and reasoning.\n"

        return response

    def _fallback_reasoning_explanation(self, synthesis_data: Dict) -> str:
        """Fallback explanation when LLM is not available"""

        response = "## 🧠 Reasoning Explanation (Basic Mode)\n\n"
        response += "I have the analysis data but need LLM integration for intelligent explanation.\n\n"
        response += f"Data Summary:\n{json.dumps(synthesis_data, indent=2)}\n\n"
        response += "💡 Configure OPENAI_API_KEY for detailed reasoning and explanations.\n"

        return response

    def _fallback_comprehensive_synthesis(self, synthesis_data: Dict) -> str:
        """Fallback comprehensive synthesis when LLM is not available"""

        response = "## 📊 Comprehensive Analysis (Basic Mode)\n\n"
        response += "All agent data collected but LLM integration needed for synthesis.\n\n"
        response += f"Raw Data:\n{json.dumps(synthesis_data, indent=2)}\n\n"
        response += "💡 Configure OPENAI_API_KEY for comprehensive analysis.\n"

        return response


# Global synthesizer instance
consensus_synthesizer = ConsensusSynthesizer()
