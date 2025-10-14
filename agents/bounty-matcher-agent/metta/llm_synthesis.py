# llm_synthesis.py
"""
LLM Synthesis for Bounty Matching
Combines MeTTa reasoning with LLM intelligence for conversational responses
"""

import os
import json
import requests
from typing import Dict, List, Any


class LLMSynthesizer:
    """
    Synthesizes MeTTa reasoning output into intelligent, conversational responses

    This is the KEY to making the agent truly intelligent:
    - MeTTa provides the REASONING (calculations, rules, scores)
    - LLM provides the INTELLIGENCE (context, conversation, personality)
    """

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-4o-mini"

    def synthesize_matches(self,
                          matches: List[Dict],
                          user_profile: Dict,
                          conversation_context: str = "") -> str:
        """
        Transform MeTTa matching results into intelligent, conversational response

        Args:
            matches: List of matches with MeTTa reasoning
            user_profile: User's profile data
            conversation_context: Previous conversation for context

        Returns:
            Intelligent, personalized response
        """

        if not self.api_key:
            return self._fallback_response(matches, user_profile)

        try:
            # Build context from MeTTa reasoning
            metta_analysis = self._extract_metta_insights(matches, user_profile)

            # Create intelligent prompt
            system_prompt = self._build_synthesis_prompt()

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self._build_user_prompt(metta_analysis, conversation_context)}
            ]

            # Call OpenAI
            response = self._call_openai(messages)

            return response

        except Exception as e:
            print(f"LLM synthesis error: {e}")
            return self._fallback_response(matches, user_profile)

    def _build_synthesis_prompt(self) -> str:
        """Build system prompt for intelligent synthesis"""

        return """You are an expert bounty matching assistant with deep understanding of developer profiles and project needs.

Your role is to:
1. **Synthesize MeTTa reasoning** into conversational, engaging responses
2. **Personalize recommendations** based on user's history and preferences
3. **Explain WHY** matches are good with specific, actionable reasoning
4. **Be conversational** - sound human, not robotic
5. **Show confidence** - use the MeTTa scores to express certainty
6. **Motivate action** - encourage the user to engage with matches

Key principles:
- Use emojis sparingly but effectively 🎯
- Write in active voice and direct address ("you", "your")
- Reference specific data points from MeTTa analysis
- Provide actionable next steps
- Balance enthusiasm with realism
- Explain technical details when relevant

Format your response as:
1. **Hook**: Exciting opening about matches found
2. **Top Matches**: 3-5 best matches with reasoning
3. **Why It Fits**: Personalized explanation for each
4. **Call to Action**: Clear next steps

Be specific, be helpful, be intelligent."""

    def _build_user_prompt(self, metta_analysis: Dict, conversation_context: str) -> str:
        """Build user prompt with MeTTa data"""

        prompt = f"""I need you to synthesize the following bounty match analysis into an intelligent, engaging response for the user.

**User Profile:**
```json
{json.dumps(metta_analysis['user_profile'], indent=2)}
```

**MeTTa Matching Results:**
```json
{json.dumps(metta_analysis['matches'], indent=2)}
```

**Conversation Context:**
{conversation_context if conversation_context else "This is the first interaction"}

**Task:**
Transform this structured data into a compelling, personalized recommendation that:
- Feels natural and conversational
- Explains the reasoning behind matches
- Shows confidence in the recommendations
- Motivates the user to take action
- References specific data points from the analysis

Make it feel like advice from an expert colleague, not a robot."""

        return prompt

    def _extract_metta_insights(self, matches: List[Dict], user_profile: Dict) -> Dict:
        """Extract key insights from MeTTa reasoning"""

        insights = {
            "user_profile": {
                "experience_level": user_profile.get("experience_level", "unknown"),
                "skills": user_profile.get("skills", []),
                "completed_bounties": user_profile.get("completed_bounties", 0),
                "preferences": user_profile.get("preferences", {})
            },
            "matches": []
        }

        for match in matches[:5]:  # Top 5
            bounty = match["bounty"]
            analysis = match["match_analysis"]

            insights["matches"].append({
                "title": bounty["title"],
                "bounty_value": bounty["bounty_value"],
                "complexity": bounty["complexity_score"],
                "estimated_hours": bounty["estimated_hours"],
                "required_skills": bounty["required_skills"],
                "url": bounty["url"],
                "confidence": {
                    "score": analysis["confidence_score"],
                    "level": analysis["confidence_level"],
                    "recommendation": analysis["recommendation"]
                },
                "reasoning": analysis["reasoning"],
                "confidence_factors": analysis["confidence_factors"]
            })

        return insights

    def _call_openai(self, messages: List[Dict]) -> str:
        """Call OpenAI API"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,  # Longer for detailed responses
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

    def _fallback_response(self, matches: List[Dict], user_profile: Dict) -> str:
        """Fallback when LLM unavailable - still uses MeTTa reasoning"""

        if not matches:
            return "❌ No matching bounties found. Try adjusting your preferences or skills."

        response = f"# 🎯 Bounty Matches\n\n"
        response += f"**Profile:** {', '.join(user_profile.get('skills', []))}\n"
        response += f"**Experience:** {user_profile.get('experience_level', 'unknown').title()}\n\n"

        for idx, match in enumerate(matches[:5], 1):
            bounty = match["bounty"]
            analysis = match["match_analysis"]

            conf_emoji = "🟢" if analysis["confidence_score"] >= 80 else "🟡" if analysis["confidence_score"] >= 60 else "🔴"

            response += f"## {idx}. {bounty['title']}\n"
            response += f"💰 ${bounty['bounty_value']} | ⏱️ ~{bounty['estimated_hours']}h | 🎯 {bounty['complexity_score']}/10\n"
            response += f"{conf_emoji} Confidence: {analysis['confidence_score']}%\n\n"

            response += "**Reasoning:**\n"
            for reason in analysis["reasoning"]:
                response += f"  • {reason}\n"
            response += "\n"

            response += f"🔗 {bounty['url']}\n\n---\n\n"

        response += "\n💡 **Tip:** Configure OPENAI_API_KEY for intelligent, conversational responses!"

        return response


# Global instance
llm_synthesizer = LLMSynthesizer()
