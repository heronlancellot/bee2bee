"""
LLM Integration Module
Supports multiple LLM providers: OpenAI, Anthropic, and local models
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
import json


class LLMProvider:
    """Base class for LLM providers"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv(self.env_var_name)

    async def generate_response(self, prompt: str, context: List[Dict] = None,
                               system_prompt: str = None, **kwargs) -> Dict:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    env_var_name = "OPENAI_API_KEY"

    def __init__(self, api_key: str = None, model: str = None):
        super().__init__(api_key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self.client = None

    async def generate_response(self, prompt: str, context: List[Dict] = None,
                               system_prompt: str = None, **kwargs) -> Dict:
        """Generate response using OpenAI API"""
        try:
            # Lazy import to avoid dependency issues
            from openai import AsyncOpenAI

            if not self.client:
                self.client = AsyncOpenAI(api_key=self.api_key)

            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Add context/history
            if context:
                for msg in context:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })

            # Add current prompt
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000)
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    env_var_name = "ANTHROPIC_API_KEY"

    def __init__(self, api_key: str = None, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key)
        self.model = model
        self.client = None

    async def generate_response(self, prompt: str, context: List[Dict] = None,
                               system_prompt: str = None, **kwargs) -> Dict:
        """Generate response using Anthropic API"""
        try:
            # Lazy import
            from anthropic import AsyncAnthropic

            if not self.client:
                self.client = AsyncAnthropic(api_key=self.api_key)

            messages = []

            # Add context/history
            if context:
                for msg in context:
                    role = "user" if msg.get("role") == "user" else "assistant"
                    messages.append({
                        "role": role,
                        "content": msg.get("content", "")
                    })

            # Add current prompt
            messages.append({"role": "user", "content": prompt})

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                system=system_prompt or "",
                messages=messages
            )

            return {
                "success": True,
                "content": response.content[0].text,
                "model": self.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }


class ASIOneProvider(LLMProvider):
    """ASI-1 API provider (OpenAI-compatible)"""
    env_var_name = "ASI_ONE_API_KEY"

    def __init__(self, api_key: str = None, model: str = None):
        super().__init__(api_key)
        self.model = model or os.getenv("ASI_ONE_MODEL", "gpt-4")
        self.base_url = "https://api.asi.one/v1"
        self.client = None

    async def generate_response(self, prompt: str, context: List[Dict] = None,
                               system_prompt: str = None, **kwargs) -> Dict:
        """Generate response using ASI-1 API (OpenAI-compatible)"""
        try:
            from openai import AsyncOpenAI

            print(f"[ASI-1] Initializing client...")
            print(f"[ASI-1] Base URL: {self.base_url}")
            print(f"[ASI-1] Model: {self.model}")
            print(f"[ASI-1] API Key: {self.api_key[:20]}...")

            if not self.client:
                self.client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )

            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            if context:
                for msg in context:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })

            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000)
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

        except Exception as e:
            print(f"[ASI-1] ❌ ERROR: {type(e).__name__}")
            print(f"[ASI-1] ❌ Message: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "content": None
            }


class LocalLLMProvider(LLMProvider):
    """Local LLM provider (Ollama, LM Studio, etc.)"""
    env_var_name = "LOCAL_LLM_URL"

    def __init__(self, api_key: str = None, model: str = "llama2",
                 base_url: str = "http://localhost:11434"):
        super().__init__(api_key)
        self.model = model
        self.base_url = base_url or os.getenv(self.env_var_name, "http://localhost:11434")

    async def generate_response(self, prompt: str, context: List[Dict] = None,
                               system_prompt: str = None, **kwargs) -> Dict:
        """Generate response using local LLM (Ollama format)"""
        try:
            import aiohttp

            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            if context:
                for msg in context:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })

            messages.append({"role": "user", "content": prompt})

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "content": data["message"]["content"],
                            "model": self.model
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "content": None
                        }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }


class AgentLLM:
    """
    Main LLM interface for agents
    Handles provider selection and prompt engineering
    """

    def __init__(self, provider_type: str = "openai", **kwargs):
        self.providers = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "asi1": ASIOneProvider,
            "local": LocalLLMProvider
        }

        if provider_type not in self.providers:
            raise ValueError(f"Unknown provider: {provider_type}")

        self.provider = self.providers[provider_type](**kwargs)
        self.provider_type = provider_type

    async def generate_agent_response(self, agent_name: str, agent_specialization: str,
                                     query: str, context: str = None,
                                     conversation_history: List[Dict] = None,
                                     shared_knowledge: List[Dict] = None) -> Dict:
        """
        Generate a response from an agent using LLM
        """

        # Build system prompt based on agent specialization
        system_prompt = self._build_system_prompt(agent_name, agent_specialization,
                                                   shared_knowledge)

        # Build the full prompt
        full_prompt = self._build_query_prompt(query, context, conversation_history)

        # Generate response
        response = await self.provider.generate_response(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1500
        )

        if response["success"]:
            return {
                "success": True,
                "response": response["content"],
                "model": response.get("model"),
                "usage": response.get("usage"),
                "confidence": self._calculate_confidence(response["content"])
            }
        else:
            return {
                "success": False,
                "error": response["error"],
                "response": f"[{agent_name}] I encountered an error processing your query. Please try again."
            }

    def _build_system_prompt(self, agent_name: str, specialization: str,
                            shared_knowledge: List[Dict] = None) -> str:
        """Build system prompt for the agent"""

        prompt = f"""You are {agent_name}, an intelligent agent specializing in {specialization}.

Your role:
- Provide expert insights based on your specialization
- Collaborate with other agents when needed
- Share knowledge and learn from interactions
- Be concise, clear, and actionable in your responses

"""

        if shared_knowledge:
            prompt += "\nShared Knowledge from other agents:\n"
            for knowledge in shared_knowledge[-5:]:  # Last 5 knowledge items
                prompt += f"- {knowledge.get('topic')}: {knowledge.get('content')}\n"

        prompt += "\nAlways identify yourself at the start of your response and provide practical, actionable insights."

        return prompt

    def _build_query_prompt(self, query: str, context: str = None,
                           conversation_history: List[Dict] = None) -> str:
        """Build the query prompt with context"""

        prompt = ""

        if conversation_history:
            prompt += "Previous conversation:\n"
            for msg in conversation_history[-3:]:  # Last 3 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt += f"{role}: {content}\n"
            prompt += "\n"

        if context:
            prompt += f"Context: {context}\n\n"

        prompt += f"Query: {query}\n\n"
        prompt += "Please provide your analysis:"

        return prompt

    def _calculate_confidence(self, response: str) -> float:
        """
        Calculate confidence score based on response characteristics
        This is a simple heuristic - you could make it more sophisticated
        """
        if not response:
            return 0.0

        # Basic heuristics
        confidence = 0.5  # Base confidence

        # Length factor (longer, more detailed responses might be more confident)
        if len(response) > 200:
            confidence += 0.1

        # Presence of specific language
        uncertain_words = ["maybe", "perhaps", "might", "possibly", "unclear"]
        certain_words = ["definitely", "certainly", "clearly", "specifically"]

        for word in uncertain_words:
            if word in response.lower():
                confidence -= 0.05

        for word in certain_words:
            if word in response.lower():
                confidence += 0.05

        # Clamp between 0.3 and 0.95
        return max(0.3, min(0.95, confidence))


# Factory function
def create_llm(provider: str = None, **kwargs) -> AgentLLM:
    """
    Factory function to create LLM instance
    Auto-detects provider based on available API keys if not specified
    """
    if provider:
        return AgentLLM(provider_type=provider, **kwargs)

    # Check LLM_PROVIDER environment variable FIRST
    llm_provider = os.getenv("LLM_PROVIDER")
    if llm_provider:
        return AgentLLM(provider_type=llm_provider.lower(), **kwargs)

    # Auto-detect based on environment variables
    if os.getenv("ASI_ONE_API_KEY"):
        return AgentLLM(provider_type="asi1", **kwargs)
    elif os.getenv("ANTHROPIC_API_KEY"):
        return AgentLLM(provider_type="anthropic", **kwargs)
    elif os.getenv("OPENAI_API_KEY"):
        return AgentLLM(provider_type="openai", **kwargs)
    else:
        # Default to local
        return AgentLLM(provider_type="local", **kwargs)
