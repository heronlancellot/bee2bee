"""
Smart Agents Orchestrator
Central coordinator for all smart agents
"""

import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from intent_classifier import IntentClassifier, IntentType
from bounty_agents.repo_analyzer import RepoAnalyzer
from bounty_agents.skill_matcher import SkillMatcher
from bounty_agents.bounty_estimator import BountyEstimator
from bounty_agents.user_profile_agent import UserProfileAgent
from consensus_synthesizer import consensus_synthesizer


class SmartAgentsOrchestrator:
    """
    Central orchestrator for all smart agents
    
    Responsibilities:
    - Classify user intent
    - Route queries to appropriate agents
    - Coordinate multi-agent responses
    - Manage conversation context
    """
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.agents = {
            IntentType.REPO_ANALYSIS: RepoAnalyzer(),
            IntentType.SKILL_MATCHING: SkillMatcher(),
            IntentType.BOUNTY_ESTIMATION: BountyEstimator(),
            IntentType.USER_PROFILE: UserProfileAgent(),
        }
        
        # Conversation context
        self.active_conversations = {}
    
    def process_query(self, query: str, user_id: str = None, 
                     conversation_id: str = None, context: Dict = None) -> Dict:
        """
        Process user query through appropriate agent
        
        Args:
            query: User input query
            user_id: User identifier
            conversation_id: Conversation ID (optional)
            context: Additional context data
            
        Returns:
            Dict with response, intent, and metadata
        """
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Classify intent
        intent_result = self.intent_classifier.classify(query)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]

        # Get or create conversation context
        conversation = self._get_conversation_context(conversation_id)

        # Add user message to conversation
        conversation["messages"].append({
            "role": "user",
            "content": query,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        })

        # Check if this is a complex intent requiring multiple agents
        if self._requires_consensus_layer(intent):
            # Use consensus layer (parallel query + synthesis)
            agent_response = self._process_with_consensus(
                intent=intent,
                query=query,
                user_id=user_id,
                context=context or {},
                conversation_history=conversation["messages"][-5:]
            )
        else:
            # Route to appropriate single agent
            agent_response = self._route_to_agent(
                intent=intent,
                query=query,
                user_id=user_id,
                context=context or {},
                conversation_history=conversation["messages"][-5:]  # Last 5 messages
            )
        
        # Add agent response to conversation
        conversation["messages"].append({
            "role": "assistant",
            "content": agent_response["response"],
            "agent_id": agent_response.get("agent_id"),
            "timestamp": datetime.now().isoformat()
        })
        
        # Update conversation metadata
        conversation["last_intent"] = intent.value
        conversation["updated_at"] = datetime.now().isoformat()
        
        # Prepare response
        response = {
            "conversation_id": conversation_id,
            "intent": intent.value,
            "intent_confidence": confidence,
            "response": agent_response["response"],
            "agent_id": agent_response.get("agent_id"),
            "metadata": {
                "reasoning": intent_result["reasoning"],
                "agent_metadata": agent_response.get("metadata", {}),
                "context": context or {}
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    def _get_conversation_context(self, conversation_id: str) -> Dict:
        """Get or create conversation context"""
        
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = {
                "id": conversation_id,
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "last_intent": None
            }
        
        return self.active_conversations[conversation_id]
    
    def _route_to_agent(self, intent: IntentType, query: str, user_id: str,
                       context: Dict, conversation_history: List[Dict]) -> Dict:
        """Route query to appropriate agent"""
        
        if intent == IntentType.UNKNOWN:
            return self._handle_unknown_intent(query)
        
        if intent not in self.agents:
            return self._handle_unknown_intent(query)
        
        try:
            agent = self.agents[intent]
            
            # Call agent with context
            agent_response = agent.process(
                query=query,
                user_id=user_id,
                context=context,
                conversation_history=conversation_history
            )
            
            return {
                "response": agent_response.get("response", "I couldn't process that request."),
                "agent_id": agent_response.get("agent_id", intent.value),
                "metadata": agent_response.get("metadata", {})
            }
            
        except Exception as e:
            print(f"[Orchestrator] Error routing to {intent.value}: {e}")
            return self._handle_error_response(intent, str(e))
    
    def _handle_unknown_intent(self, query: str) -> Dict:
        """Handle queries with unknown intent"""
        
        return {
            "response": f"I'm not sure how to help with that. I can help you with:\n" +
                       "- Repository analysis\n" +
                       "- Skill matching\n" +
                       "- Bounty estimation\n" +
                       "- User profile management\n\n" +
                       "Could you rephrase your question?",
            "agent_id": "orchestrator",
            "metadata": {"intent": "unknown", "fallback": True}
        }
    
    def _handle_error_response(self, intent: IntentType, error: str) -> Dict:
        """Handle agent errors gracefully"""

        return {
            "response": f"I encountered an issue while processing your {intent.value} request. " +
                       "Please try again or rephrase your question.",
            "agent_id": "orchestrator",
            "metadata": {"error": error, "intent": intent.value}
        }

    def _requires_consensus_layer(self, intent: IntentType) -> bool:
        """Check if intent requires consensus layer (multiple agents)"""

        complex_intents = [
            IntentType.FIND_MATCHES,
            IntentType.EXPLAIN_REASONING,
            IntentType.COMPREHENSIVE_ANALYSIS
        ]

        return intent in complex_intents

    def _process_with_consensus(self, intent: IntentType, query: str, user_id: str,
                                context: Dict, conversation_history: List[Dict]) -> Dict:
        """
        Process query using consensus layer (parallel query + synthesis)

        This is the core of the intelligent multi-agent system:
        1. Query multiple agents in parallel
        2. Collect all responses
        3. Synthesize into a coherent, intelligent response
        """

        print(f"[Orchestrator] Using CONSENSUS LAYER for intent: {intent.value}")

        # Determine which agents to query based on intent
        agents_to_query = self._get_agents_for_intent(intent)

        # Query agents in parallel
        agent_responses = self._query_agents_parallel(
            agents=agents_to_query,
            query=query,
            user_id=user_id,
            context=context,
            conversation_history=conversation_history
        )

        # Synthesize responses based on intent
        try:
            if intent == IntentType.FIND_MATCHES:
                synthesized = consensus_synthesizer.synthesize_find_matches(
                    query=query,
                    user_id=user_id,
                    agent_responses=agent_responses,
                    conversation_history=conversation_history
                )
            elif intent == IntentType.EXPLAIN_REASONING:
                synthesized = consensus_synthesizer.synthesize_explain_reasoning(
                    query=query,
                    user_id=user_id,
                    agent_responses=agent_responses,
                    conversation_history=conversation_history,
                    context=context
                )
            elif intent == IntentType.COMPREHENSIVE_ANALYSIS:
                synthesized = consensus_synthesizer.synthesize_comprehensive_analysis(
                    query=query,
                    user_id=user_id,
                    agent_responses=agent_responses,
                    conversation_history=conversation_history
                )
            else:
                # Fallback to basic synthesis
                synthesized = self._basic_synthesis(agent_responses)

            return {
                "response": synthesized.get("response", "Unable to synthesize response"),
                "agent_id": "consensus_layer",
                "metadata": {
                    "agents_consulted": list(agent_responses.keys()),
                    "synthesis_metadata": synthesized.get("metadata", {}),
                    "intent": intent.value
                }
            }

        except Exception as e:
            print(f"[Orchestrator] Error in consensus synthesis: {e}")
            return self._basic_synthesis(agent_responses)

    def _get_agents_for_intent(self, intent: IntentType) -> List[str]:
        """Determine which agents to query for a given intent"""

        # Map intents to required agents
        intent_agent_map = {
            IntentType.FIND_MATCHES: [
                IntentType.USER_PROFILE,
                IntentType.REPO_ANALYSIS,
                IntentType.SKILL_MATCHING,
                IntentType.BOUNTY_ESTIMATION
            ],
            IntentType.EXPLAIN_REASONING: [
                IntentType.SKILL_MATCHING,
                IntentType.USER_PROFILE,
                IntentType.BOUNTY_ESTIMATION
            ],
            IntentType.COMPREHENSIVE_ANALYSIS: [
                IntentType.REPO_ANALYSIS,
                IntentType.SKILL_MATCHING,
                IntentType.BOUNTY_ESTIMATION,
                IntentType.USER_PROFILE
            ]
        }

        return intent_agent_map.get(intent, [])

    def _query_agents_parallel(self, agents: List[IntentType], query: str,
                              user_id: str, context: Dict,
                              conversation_history: List[Dict]) -> Dict[str, Dict]:
        """
        Query multiple agents in parallel

        Returns:
            Dict mapping agent_id to agent response
        """

        agent_responses = {}

        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            # Submit all agent queries
            future_to_agent = {}

            for agent_intent in agents:
                if agent_intent in self.agents:
                    agent = self.agents[agent_intent]

                    # Submit the agent query
                    future = executor.submit(
                        self._safe_agent_call,
                        agent=agent,
                        query=query,
                        user_id=user_id,
                        context=context,
                        conversation_history=conversation_history
                    )

                    future_to_agent[future] = agent.agent_id

            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent_id = future_to_agent[future]
                try:
                    response = future.result()
                    agent_responses[agent_id] = response
                    print(f"[Orchestrator] ✓ Received response from {agent_id}")
                except Exception as e:
                    print(f"[Orchestrator] ✗ Error from {agent_id}: {e}")
                    agent_responses[agent_id] = {
                        "response": f"Error from {agent_id}",
                        "agent_id": agent_id,
                        "metadata": {"error": str(e)}
                    }

        return agent_responses

    def _safe_agent_call(self, agent, query: str, user_id: str,
                        context: Dict, conversation_history: List[Dict]) -> Dict:
        """Safely call an agent with error handling"""

        try:
            return agent.process(
                query=query,
                user_id=user_id,
                context=context,
                conversation_history=conversation_history
            )
        except Exception as e:
            return {
                "response": f"Error processing query",
                "agent_id": getattr(agent, 'agent_id', 'unknown'),
                "metadata": {"error": str(e)}
            }

    def _basic_synthesis(self, agent_responses: Dict[str, Dict]) -> Dict:
        """Basic synthesis when consensus layer fails"""

        response_text = "## Multi-Agent Response\n\n"

        for agent_id, agent_response in agent_responses.items():
            response_text += f"### {agent_id.replace('_', ' ').title()}\n"
            response_text += f"{agent_response.get('response', 'No response')}\n\n"

        return {
            "response": response_text,
            "agent_id": "orchestrator",
            "metadata": {
                "agents_consulted": list(agent_responses.keys()),
                "synthesis_type": "basic"
            }
        }
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation by ID"""
        return self.active_conversations.get(conversation_id)
    
    def get_conversation_summary(self, conversation_id: str) -> Dict:
        """Get conversation summary"""
        
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return {"error": "Conversation not found"}
        
        messages = conversation.get("messages", [])
        
        return {
            "conversation_id": conversation_id,
            "message_count": len(messages),
            "last_intent": conversation.get("last_intent"),
            "created_at": conversation.get("created_at"),
            "updated_at": conversation.get("updated_at"),
            "recent_messages": messages[-3:] if messages else []
        }
    
    def get_agent_capabilities(self) -> Dict:
        """Get capabilities of all agents"""
        
        capabilities = {}
        
        for intent_type, agent in self.agents.items():
            try:
                capabilities[intent_type.value] = {
                    "description": agent.get_description(),
                    "capabilities": agent.get_capabilities(),
                    "status": "active"
                }
            except Exception as e:
                capabilities[intent_type.value] = {
                    "description": f"Agent for {intent_type.value}",
                    "capabilities": [],
                    "status": f"error: {str(e)}"
                }
        
        return capabilities
    
    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Clean up old conversations"""
        
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        conversations_to_remove = []
        
        for conv_id, conversation in self.active_conversations.items():
            created_at = datetime.fromisoformat(conversation["created_at"]).timestamp()
            if created_at < cutoff_time:
                conversations_to_remove.append(conv_id)
        
        for conv_id in conversations_to_remove:
            del self.active_conversations[conv_id]
        
        print(f"[Orchestrator] Cleaned up {len(conversations_to_remove)} old conversations")


# Global instance
orchestrator = SmartAgentsOrchestrator()


def process_user_query(query: str, user_id: str = None, 
                      conversation_id: str = None, context: Dict = None) -> Dict:
    """
    Convenience function to process user query
    
    Args:
        query: User input query
        user_id: User identifier
        conversation_id: Conversation ID (optional)
        context: Additional context data
        
    Returns:
        Dict with response and metadata
    """
    return orchestrator.process_query(query, user_id, conversation_id, context)


def get_orchestrator() -> SmartAgentsOrchestrator:
    """Get global orchestrator instance"""
    return orchestrator
