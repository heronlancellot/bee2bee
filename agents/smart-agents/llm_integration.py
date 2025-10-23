"""
LLM Integration Module for Smart Agents
Provides intelligent responses using OpenAI API
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class LLMIntegration:
    """
    LLM Integration for intelligent agent responses
    """

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-4o-mini"  # Cost-effective model

        # Improved system prompts for each agent type
        self.enhanced_prompts = self._build_enhanced_prompts()

    def generate_intelligent_response(self,
                                    agent_type: str,
                                    query: str,
                                    context: Dict = None,
                                    conversation_history: List[Dict] = None,
                                    structured_data: Dict = None) -> str:
        """
        Generate intelligent response using LLM

        Args:
            agent_type: Type of agent (repo_analyzer, skill_matcher, etc.)
            query: User query
            context: Additional context
            conversation_history: Previous conversation
            structured_data: Structured data from agent analysis

        Returns:
            Intelligent response string
        """

        if not self.api_key:
            return self._fallback_response(agent_type, structured_data)

        try:
            # Build system prompt based on agent type
            system_prompt = self._build_system_prompt(agent_type, structured_data)

            # Build conversation messages
            messages = self._build_messages(system_prompt, query, conversation_history)

            # Call OpenAI API
            response = self._call_openai_api(messages)

            return response

        except Exception as e:
            print(f"[LLMIntegration] Error: {e}")
            return self._fallback_response(agent_type, structured_data)

    def _build_enhanced_prompts(self) -> Dict[str, str]:
        """Build enhanced prompts for each agent type"""

        return {
            "repo_analyzer": """
You are an expert repository analyst with deep knowledge of software engineering best practices.

Your analysis should be:
- **Data-driven**: Use the provided metrics and statistics
- **Insightful**: Identify patterns and trends
- **Actionable**: Provide specific, implementable recommendations
- **Contextual**: Consider the repository's domain and purpose

When analyzing repositories:
1. Assess code quality and architecture
2. Evaluate technology stack and dependencies
3. Analyze project health and maintenance patterns
4. Identify security considerations
5. Provide performance insights
6. Suggest best practices and improvements

Use a conversational, professional tone. Be specific and cite evidence from the data.
""",
            "skill_matcher": """
You are an expert skill matcher specializing in developer-project alignment.

Your matching should be:
- **Comprehensive**: Consider skills, experience, and preferences
- **Evidence-based**: Use concrete data points
- **Confidence-scored**: Provide match confidence with reasoning
- **Developmental**: Suggest learning paths for skill gaps

When matching skills:
1. Analyze exact skill matches
2. Identify related/transferable skills
3. Assess experience level alignment
4. Consider preference compatibility
5. Calculate confidence scores with reasoning
6. Provide actionable recommendations

Use an encouraging, educational tone. Explain WHY matches work or don't work.
""",
            "bounty_estimator": """
You are an expert in project estimation and pricing with industry experience.

Your estimates should be:
- **Realistic**: Based on industry standards and data
- **Detailed**: Break down complexity factors
- **Range-aware**: Provide ranges, not just point estimates
- **Risk-conscious**: Identify uncertainties and assumptions

When estimating bounties:
1. Analyze project complexity and scope
2. Estimate time and effort requirements
3. Consider technology-specific multipliers
4. Account for risk and uncertainty
5. Provide pricing recommendations by skill level
6. Suggest milestone-based approaches when appropriate

Use an analytical, professional tone. Show your reasoning clearly.
""",
            "user_profile": """
You are an expert in developer profiling and career development.

Your analysis should be:
- **Holistic**: Consider skills, experience, preferences, and goals
- **Growth-oriented**: Focus on development and progression
- **Personalized**: Tailor insights to the individual
- **Actionable**: Provide specific next steps

When analyzing profiles:
1. Assess current skill set and diversity
2. Evaluate experience level and trajectory
3. Identify earning potential and opportunities
4. Analyze preference patterns
5. Provide personalized recommendations
6. Suggest career development paths

Use a supportive, motivational tone. Be honest but encouraging.
"""
        }

    def _build_system_prompt(self, agent_type: str, structured_data: Dict = None) -> str:
        """Build system prompt based on agent type"""

        # Use enhanced prompts if available
        prompt = self.enhanced_prompts.get(agent_type, "You are a helpful AI assistant.")

        if structured_data:
            prompt += f"\n\n**Structured Data Available:**\n```json\n{json.dumps(structured_data, indent=2)}\n```\n"
            prompt += "\nUse this data to provide specific, evidence-based insights. Reference specific metrics and values in your response."

        return prompt

    def _build_messages(self, system_prompt: str, query: str,
                       conversation_history: List[Dict] = None) -> List[Dict]:
        """Build messages for OpenAI API"""

        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 6 messages for context
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        # Add current query
        messages.append({"role": "user", "content": query})

        return messages

    def _call_openai_api(self, messages: List[Dict]) -> str:
        """Call OpenAI API"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1500,  # Increased for more detailed responses
            "stream": False
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    def _fallback_response(self, agent_type: str, structured_data: Dict = None) -> str:
        """Fallback response when LLM is not available"""

        fallbacks = {
            "repo_analyzer": """
## 📊 Repository Analysis (Basic Mode)

I've analyzed the repository data, but I need OpenAI API integration for more intelligent insights.

**To enable intelligent analysis:**
Set your OPENAI_API_KEY environment variable to get:
- Deep code quality insights
- Intelligent recommendations
- Contextual analysis
- Professional explanations
""",
            "skill_matcher": """
## 🎯 Skill Matching (Basic Mode)

I've processed the skill matching data, but I need OpenAI API integration for intelligent matching.

**To enable intelligent matching:**
Set your OPENAI_API_KEY environment variable to get:
- Detailed match reasoning
- Confidence scores with explanations
- Learning path recommendations
- Personalized insights
""",
            "bounty_estimator": """
## 💰 Bounty Estimation (Basic Mode)

I've calculated the estimation data, but I need OpenAI API integration for intelligent analysis.

**To enable intelligent estimates:**
Set your OPENAI_API_KEY environment variable to get:
- Detailed complexity analysis
- Risk assessment
- Pricing recommendations
- Professional breakdowns
""",
            "user_profile": """
## 👤 User Profile (Basic Mode)

I've processed the profile data, but I need OpenAI API integration for intelligent insights.

**To enable intelligent profiling:**
Set your OPENAI_API_KEY environment variable to get:
- Personalized recommendations
- Career development insights
- Growth opportunities
- Actionable next steps
"""
        }

        base_response = fallbacks.get(agent_type, "Analysis completed with basic data.")

        if structured_data:
            base_response += f"\n\n**Raw Data:**\n```json\n{json.dumps(structured_data, indent=2)}\n```"

        return base_response

    def generate_synthesis_response(self,
                                   synthesis_type: str,
                                   agent_data: Dict,
                                   query: str,
                                   conversation_history: List[Dict] = None) -> str:
        """
        Generate intelligent synthesis response combining multiple agent insights

        This is used by the ConsensusSynthesizer for high-quality multi-agent responses
        """

        if not self.api_key:
            return self._fallback_synthesis(synthesis_type, agent_data)

        try:
            system_prompt = self._build_synthesis_prompt(synthesis_type)
            messages = self._build_messages(system_prompt, query, conversation_history)

            # Add agent data context
            messages.append({
                "role": "system",
                "content": f"Agent Data:\n```json\n{json.dumps(agent_data, indent=2)}\n```"
            })

            response = self._call_openai_api(messages)
            return response

        except Exception as e:
            print(f"[LLMIntegration] Synthesis error: {e}")
            return self._fallback_synthesis(synthesis_type, agent_data)

    def _build_synthesis_prompt(self, synthesis_type: str) -> str:
        """Build prompt for synthesis operations"""

        synthesis_prompts = {
            "find_matches": """
You are an expert synthesis agent combining insights from multiple specialists to find perfect matches.

Create compelling, personalized recommendations that:
- Show TOP matches with clear reasoning
- Explain WHY each match is perfect
- Include specific details (bounty, complexity, skills)
- Provide confidence scores
- Use engaging, conversational tone
- Format beautifully with emojis and structure
""",
            "explain_reasoning": """
You are an expert at explaining complex decision-making processes clearly.

Provide detailed explanations that:
- Break down the reasoning step-by-step
- Show evidence and data points
- Explain confidence calculations
- Identify key factors and trade-offs
- Use clear, educational language
""",
            "comprehensive": """
You are an expert at synthesizing complex information into coherent insights.

Create comprehensive analysis that:
- Combines all agent insights cohesively
- Identifies patterns and connections
- Provides holistic recommendations
- Maintains professional structure
- Balances depth with clarity
"""
        }

        return synthesis_prompts.get(synthesis_type, "You are a helpful synthesis agent.")

    def _fallback_synthesis(self, synthesis_type: str, agent_data: Dict) -> str:
        """Fallback for synthesis when LLM unavailable"""

        return f"""
## Multi-Agent Synthesis (Basic Mode)

Synthesis Type: {synthesis_type}

I've collected data from multiple agents but need OpenAI API for intelligent synthesis.

**To enable intelligent synthesis:**
Set your OPENAI_API_KEY environment variable to get:
- Intelligent multi-agent responses
- Deep reasoning and explanations
- Personalized recommendations
- Professional synthesis

**Raw Agent Data:**
```json
{json.dumps(agent_data, indent=2)}
```
"""


# Global LLM instance
llm_integration = LLMIntegration()
