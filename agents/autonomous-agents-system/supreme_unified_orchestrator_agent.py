# supreme_unified_orchestrator_agent.py - Supreme Unified Orchestrator Agent
"""
🧙‍♂️ SUPREME UNIFIED ORCHESTRATOR AGENT ⚔️

Agent que expõe o Supreme Unified Orchestrator via REST API
Integra AgentVerse + Personalidades + Conversas Reais + Síntese IA
"""

from uagents import Agent, Context, Model, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)
import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Import Supreme Unified Orchestrator
from supreme_unified_orchestrator import SupremeUnifiedOrchestrator

load_dotenv()

# Create Supreme Unified Orchestrator Agent
supreme_agent = Agent(
    name="Supreme Unified Orchestrator Agent",
    seed="supreme_unified_bee2bee_2025_agent",
    port=8020,  # New port for Supreme system
    mailbox=True,
    publish_agent_details=True
)

# Initialize Supreme Orchestrator
supreme_orchestrator = SupremeUnifiedOrchestrator()

chat_proto = Protocol(spec=chat_protocol_spec)


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle intelligent queries with SUPREME PROCESSING"""
    
    ctx.logger.info("="*80)
    ctx.logger.info(f"🧙‍♂️ SUPREME Query received from {sender}: {msg.content[:50]}...")
    ctx.logger.info("="*80)
    
    try:
        # Process through Supreme Orchestrator
        result = await supreme_orchestrator.process_query(msg.content, sender)
        
        ctx.logger.info("✅ Supreme processing complete!")
        ctx.logger.info(f"Intent: {result['intent']}, Confidence: {result['confidence']:.2f}")
        ctx.logger.info(f"Conversations: {result['agent_conversations_count']}")
        ctx.logger.info("="*80)
        
        # Send response
        await ctx.send(
            sender,
            ChatMessage(
                content=TextContent(text=result['response']),
                message_id=str(uuid.uuid4()),
                timestamp=datetime.now().timestamp(),
                sender=supreme_agent.address,
            ),
        )
        
    except Exception as e:
        ctx.logger.error(f"Error in supreme processing: {e}")
        
        await ctx.send(
            sender,
            ChatMessage(
                content=TextContent(text=f"❌ Error in supreme processing: {str(e)}"),
                message_id=str(uuid.uuid4()),
                timestamp=datetime.now().timestamp(),
                sender=supreme_agent.address,
            ),
        )


# REST API Models
class SupremeQueryRequest(Model):
    message: str
    user_id: str = "anonymous"
    conversation_id: str = None


class SupremeQueryResponse(Model):
    response: str
    intent: str
    confidence: float
    session_id: str
    agent_conversations_count: int
    agent_responses_count: int
    database_queries_count: int
    ai_synthesis_used: bool
    timestamp: str


@supreme_agent.on_rest_post("/api/query", SupremeQueryRequest, SupremeQueryResponse)
async def handle_rest_query(ctx: Context, req: SupremeQueryRequest) -> SupremeQueryResponse:
    """
    REST endpoint for frontend integration with SUPREME INTELLIGENT PROCESSING
    
    This implements the complete SUPREME ARCHITECTURE:
    1. Context Analysis with AgentVerse
    2. Autonomous Agents with Personalities
    3. Real Agent Conversations
    4. Intelligent Database Interaction
    5. Real AI Synthesis via AgentVerse
    """
    
    ctx.logger.info("="*80)
    ctx.logger.info(f"🧙‍♂️ SUPREME REST Query received: {req.message[:50]}...")
    ctx.logger.info("="*80)
    
    conversation_id = req.conversation_id or f"supreme_conv_{datetime.now().timestamp()}"
    
    try:
        # Process through Supreme Orchestrator
        result = await supreme_orchestrator.process_query(req.message, req.user_id)
        
        ctx.logger.info("✅ Supreme processing complete!")
        ctx.logger.info(f"Intent: {result['intent']}, Confidence: {result['confidence']:.2f}")
        ctx.logger.info(f"Conversations: {result['agent_conversations_count']}")
        ctx.logger.info("="*80)
        
        return SupremeQueryResponse(
            response=result['response'],
            intent=result['intent'],
            confidence=result['confidence'],
            session_id=result['session_id'],
            agent_conversations_count=result['agent_conversations_count'],
            agent_responses_count=result['agent_responses_count'],
            database_queries_count=result['database_queries_count'],
            ai_synthesis_used=result['ai_synthesis_used'],
            timestamp=result['timestamp']
        )
        
    except Exception as e:
        ctx.logger.error(f"Error in supreme processing: {e}")
        
        return SupremeQueryResponse(
            response=f"❌ Error in supreme processing: {str(e)}",
            intent="error",
            confidence=0.0,
            session_id=f"error_{datetime.now().timestamp()}",
            agent_conversations_count=0,
            agent_responses_count=0,
            database_queries_count=0,
            ai_synthesis_used=False,
            timestamp=datetime.now().isoformat()
        )


@supreme_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("="*80)
    ctx.logger.info("🧙‍♂️ SUPREME UNIFIED ORCHESTRATOR AGENT STARTING ⚔️")
    ctx.logger.info("="*80)
    ctx.logger.info(f"Agent address: {supreme_agent.address}")
    ctx.logger.info(f"Port: 8020")
    ctx.logger.info(f"📡 REST Endpoint: http://localhost:8020/api/query")
    ctx.logger.info("="*80)
    ctx.logger.info("🎯 SUPREME FEATURES:")
    ctx.logger.info("  🧠 Context Analysis with AgentVerse")
    ctx.logger.info("  💬 Real Agent Conversations")
    ctx.logger.info("  🎭 Agent Personalities")
    ctx.logger.info("  🗄️ Intelligent Database Interaction")
    ctx.logger.info("  🔄 Real AI Synthesis")
    ctx.logger.info("="*80)
    
    # Check AgentVerse configuration
    if os.getenv("AGENTVERSE_API_KEY"):
        ctx.logger.info("✅ AgentVerse API Key configured")
    else:
        ctx.logger.warning("⚠️ AgentVerse API Key not configured - using fallback")
    
    # Check Supabase configuration
    if os.getenv("NEXT_PUBLIC_SUPABASE_URL") and os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY"):
        ctx.logger.info("✅ Supabase configured")
    else:
        ctx.logger.warning("⚠️ Supabase not configured - limited functionality")


if __name__ == "__main__":
    print("🧙‍♂️ SUPREME UNIFIED ORCHESTRATOR AGENT ⚔️")
    print("="*80)
    print("🎯 SUPREME FEATURES:")
    print("  🧠 Context Analysis with AgentVerse")
    print("  💬 Real Agent Conversations")
    print("  🎭 Agent Personalities")
    print("  🗄️ Intelligent Database Interaction")
    print("  🔄 Real AI Synthesis")
    print("="*80)
    print(f"📡 REST API: http://localhost:8020/api/query")
    print(f"🌐 Port: 8020")
    print("="*80)
    
    supreme_agent.run()



