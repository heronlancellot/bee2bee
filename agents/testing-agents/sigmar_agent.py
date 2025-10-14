"""
Sigmar - Strategic Analysis Agent
Agent module (not a standalone server)
"""

import asyncio
from typing import Dict, Optional, List
from llm_integration import create_llm
from shared_memory import shared_memory


class SigmarAgent:
    """Strategic Analysis and Planning Agent"""

    def __init__(self):
        self.agent_id = "sigmar"
        self.agent_name = "Sigmar"
        self.specialization = "Strategic Analysis and Planning"
        self.llm = None
        self._initialized = False

    async def initialize(self):
        """Initialize the agent and its LLM"""
        if self._initialized:
            return

        print(f"[{self.agent_name}] Initializing...")

        try:
            self.llm = create_llm()
            print(f"[{self.agent_name}] ✓ LLM initialized")
        except Exception as e:
            print(f"[{self.agent_name}] ✗ LLM failed: {e}")

        # Store metadata
        shared_memory.update_agent_metadata(self.agent_id, {
            "name": self.agent_name,
            "specialization": self.specialization,
            "status": "online"
        })

        self._initialized = True
        print(f"[{self.agent_name}] ✓ Ready!")

    async def handle_query(self, query: str, context: Optional[str] = None,
                          conversation_id: Optional[str] = None) -> Dict:
        """
        Handle incoming query

        Args:
            query: The user query
            context: Optional context for the query
            conversation_id: Optional conversation ID for history

        Returns:
            Dict with response, confidence, agent info
        """
        if not self._initialized:
            await self.initialize()

        print(f"\n[{self.agent_name}] Processing query:")
        print(f"  Query: {query[:50]}...")
        print(f"  Conversation: {conversation_id}")

        try:
            # Get context from shared memory
            context_data = shared_memory.get_relevant_context(
                query=query,
                agent_id=self.agent_id
            )

            # Get conversation history
            history = []
            if conversation_id:
                history = shared_memory.get_conversation_history(
                    conversation_id,
                    limit=5
                )

            # Generate response with LLM
            if self.llm:
                print(f"[{self.agent_name}] Generating LLM response...")

                result = await self.llm.generate_agent_response(
                    agent_name=self.agent_name,
                    agent_specialization=self.specialization,
                    query=query,
                    context=context,
                    conversation_history=history,
                    shared_knowledge=context_data.get('knowledge', [])
                )

                if result['success']:
                    response_text = result['response']
                    confidence = result.get('confidence', 0.7)
                    print(f"[{self.agent_name}] ✓ Response generated (confidence: {confidence:.2f})")
                else:
                    response_text = f"[{self.agent_name}] Error: {result.get('error')}"
                    confidence = 0.3
                    print(f"[{self.agent_name}] ✗ LLM error: {result.get('error')}")
            else:
                response_text = f"[{self.agent_name}] Hello! I'm {self.agent_name}, specialized in {self.specialization}. However, my LLM is not available right now."
                confidence = 0.2
                print(f"[{self.agent_name}] ⚠ LLM not available, using fallback")

            # Store in memory
            if conversation_id:
                shared_memory.store_conversation_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=response_text,
                    agent_id=self.agent_id
                )

            print(f"[{self.agent_name}] ✓ Query completed\n")

            return {
                "success": True,
                "response": response_text,
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "confidence": confidence,
                "conversation_id": conversation_id
            }

        except Exception as e:
            print(f"[{self.agent_name}] ✗ Error: {e}")
            import traceback
            traceback.print_exc()

            return {
                "success": False,
                "response": f"[{self.agent_name}] An error occurred",
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "confidence": 0.0,
                "error": str(e)
            }

    def get_info(self) -> Dict:
        """Get agent information"""
        return {
            "id": self.agent_id,
            "name": self.agent_name,
            "specialization": self.specialization,
            "status": "online" if self._initialized else "offline",
            "llm_ready": self.llm is not None
        }


# Singleton instance
sigmar_agent = SigmarAgent()
