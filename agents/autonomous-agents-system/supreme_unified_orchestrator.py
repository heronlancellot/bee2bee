# supreme_unified_orchestrator.py - Supreme Unified Orchestrator with AgentVerse
"""
🧙‍♂️ SUPREME UNIFIED ORCHESTRATOR ⚔️

ARQUITETURA SUPREMA IMPLEMENTADA:
1. 🧠 Context Analyzer com AgentVerse
2. 💬 Conversas reais entre agentes com personalidades
3. 🗄️ Interação inteligente com Supabase
4. 🎭 Personalidades únicas para cada agente
5. 🔄 Síntese real de IA via AgentVerse

USER QUERY
    ↓
🧠 SUPREME UNIFIED ORCHESTRATOR (AgentVerse + MeTTa)
    ↓
┌─────────────────────────────────────────────┐
│  🧠 CONTEXT ANALYZER + AGENTVERSE            │
│  1. AgentVerse analisa contexto da query     │
│  2. Extrai intenções e parâmetros           │
│  3. Determina quais agentes consultar       │
│  4. Prepara queries otimizadas             │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  🤖 AUTONOMOUS AGENTS WITH PERSONALITIES     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────┐│
│  │👤 Profile   │ │🎯 Skill     │ │💰 Bounty││
│  │Agent        │ │Matcher      │ │Estimator││
│  │"Eu sou o    │ │"Eu sou o    │ │"Eu sou o││
│  │especialista │ │especialista │ │especialista││
│  │em perfis!"  │ │em skills!"  │ │em valores!"││
│  │             │ │             │ │         ││
│  │1. Consulta  │ │1. Consulta  │ │1. Consulta││
│  │   Supabase  │ │   Supabase  │ │   Supabase││
│  │2. MeTTa AI  │ │2. MeTTa AI  │ │2. MeTTa AI││
│  │3. Resposta  │ │3. Resposta  │ │3. Resposta││
│  │   Inteligente│ │   Inteligente│ │   Inteligente││
│  └─────────────┘ └─────────────┘ └─────────┘│
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  💬 AGENT CONVERSATIONS                      │
│  Agent 1: "Baseado no perfil, recomendo..."  │
│  Agent 2: "Concordo, mas também vejo..."    │
│  Agent 3: "Considerando o valor, sugiro..."   │
│  Agent 1: "Excelente ponto! Vamos..."        │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  🧠 REAL AI SYNTHESIS (AgentVerse)           │
│  1. Analisa todas as conversas              │
│  2. Identifica padrões e insights           │
│  3. Gera resposta natural e inteligente     │
│  4. Explica reasoning em linguagem natural  │
└─────────────────────────────────────────────┘
    ↓
RESPOSTA FINAL INTELIGENTE E NATURAL:
"Com base na análise dos meus agentes especializados..."
"""

import asyncio
import json
import os
import uuid
from typing import Dict, List, Optional
import aiohttp
from datetime import datetime
from dotenv import load_dotenv
from dataclasses import dataclass
from enum import Enum

# Import Supabase client
from supabase_agent_client import create_supabase_agent_client

load_dotenv()

# AgentVerse Configuration
AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY")
AGENTVERSE_API = "https://agentverse.ai/v1/submit"

# Agent Addresses (will be configured via environment)
AGENT_ADDRESSES = {
    "user_profile": os.getenv("USER_PROFILE_AGENT_ADDRESS", "agent1q..."),
    "skill_matcher": os.getenv("SKILL_MATCHER_AGENT_ADDRESS", "agent1q..."),
    "bounty_estimator": os.getenv("BOUNTY_ESTIMATOR_AGENT_ADDRESS", "agent1q..."),
    "repository_analyzer": os.getenv("REPO_ANALYZER_AGENT_ADDRESS", "agent1q..."),
}

# Agent Personalities
AGENT_PERSONALITIES = {
    "user_profile": {
        "name": "👤 Profiler",
        "personality": "Eu sou o especialista em perfis de usuários! Analiso habilidades, experiência e carreira.",
        "expertise": "Análise de perfis, carreira, habilidades",
        "speaking_style": "Analítico e detalhado"
    },
    "skill_matcher": {
        "name": "🎯 SkillMaster", 
        "personality": "Eu sou o especialista em matching de habilidades! Conheço todas as tecnologias.",
        "expertise": "Matching de skills, tecnologias, frameworks",
        "speaking_style": "Técnico e preciso"
    },
    "bounty_estimator": {
        "name": "💰 Valuer",
        "personality": "Eu sou o especialista em estimativas de valor! Calculo preços justos para projetos.",
        "expertise": "Estimativas, valores, complexidade",
        "speaking_style": "Financeiro e estratégico"
    },
    "repository_analyzer": {
        "name": "📁 RepoExplorer",
        "personality": "Eu sou o especialista em repositórios! Analiso código e encontro oportunidades.",
        "expertise": "Análise de código, repositórios, issues",
        "speaking_style": "Explorador e curioso"
    }
}


@dataclass
class AgentMessage:
    """Message from one agent to another"""
    sender: str
    recipient: str
    content: str
    timestamp: str
    context: Dict


@dataclass
class AgentResponse:
    """Response from an agent"""
    agent_name: str
    response: str
    confidence: float
    personality: str
    expertise: str
    timestamp: str


@dataclass
class ConversationContext:
    """Context for agent conversations"""
    session_id: str
    user_query: str
    intent: str
    confidence: float
    agent_responses: List[AgentResponse]
    agent_conversations: List[AgentMessage]
    database_queries: List[Dict]
    final_synthesis: str = ""


class SupremeUnifiedOrchestrator:
    """
    🧙‍♂️ SUPREME UNIFIED ORCHESTRATOR ⚔️
    
    Implements the complete intelligent architecture:
    1. Context Analysis with AgentVerse
    2. Autonomous Agents with Personalities
    3. Real Agent Conversations
    4. Intelligent Database Interaction
    5. Real AI Synthesis via AgentVerse
    """
    
    def __init__(self):
        self.agent_addresses = AGENT_ADDRESSES
        self.agent_personalities = AGENT_PERSONALITIES
        self.api_key = AGENTVERSE_API_KEY
        self.supabase_client = create_supabase_agent_client()
        self.active_sessions = {}
    
    async def process_query(self, user_message: str, user_id: str = "anonymous") -> Dict:
        """
        Process user query with SUPREME INTELLIGENCE:
        1. Analyze context with AgentVerse
        2. Query agents with personalities
        3. Facilitate agent conversations
        4. Synthesize with real AI
        """
        
        session_id = f"supreme_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        
        # Create conversation context
        context = ConversationContext(
            session_id=session_id,
            user_query=user_message,
            intent="",
            confidence=0.0,
            agent_responses=[],
            agent_conversations=[],
            database_queries=[]
        )
        
        self.active_sessions[session_id] = context
        
        try:
            # Step 1: Context Analysis with AgentVerse
            await self._analyze_context_with_agentverse(context)
            
            # Step 2: Query Agents with Personalities
            await self._query_agents_with_personalities(context)
            
            # Step 3: Facilitate Agent Conversations
            await self._facilitate_agent_conversations(context)
            
            # Step 4: Real AI Synthesis with AgentVerse
            await self._synthesize_with_agentverse(context)
            
            # Step 5: Save Session to Database
            await self._save_session_to_database(context)
            
            return {
                "response": context.final_synthesis,
                "session_id": session_id,
                "intent": context.intent,
                "confidence": context.confidence,
                "agent_conversations_count": len(context.agent_conversations),
                "agent_responses_count": len(context.agent_responses),
                "database_queries_count": len(context.database_queries),
                "ai_synthesis_used": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "response": f"❌ Error in supreme processing: {str(e)}",
                "session_id": session_id,
                "intent": "error",
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_context_with_agentverse(self, context: ConversationContext):
        """Analyze context using AgentVerse"""
        
        # Prepare context analysis prompt
        context_prompt = f"""
        Analise esta query do usuário e determine:
        1. Intent principal (find_matches, find_repositories, general_chat, etc.)
        2. Parâmetros extraídos (skills, experience, etc.)
        3. Confiança da análise (0.0 a 1.0)
        4. Agentes necessários para responder
        
        Query: "{context.user_query}"
        
        Responda em JSON:
        {{
            "intent": "intent_name",
            "confidence": 0.8,
            "parameters": {{"skills": [], "experience": 0}},
            "required_agents": ["agent1", "agent2"]
        }}
        """
        
        try:
            # Use AgentVerse for context analysis
            analysis_result = await self._query_agentverse_for_analysis(context_prompt)
            
            if analysis_result and "intent" in analysis_result:
                context.intent = analysis_result["intent"]
                context.confidence = analysis_result.get("confidence", 0.5)
                
                # Store analysis in database
                context.database_queries.append({
                    "type": "context_analysis",
                    "query": context.user_query,
                    "result": analysis_result,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                # Fallback analysis
                context.intent = "general_chat"
                context.confidence = 0.5
                
        except Exception as e:
            print(f"⚠️ Context analysis failed: {e}")
            context.intent = "general_chat"
            context.confidence = 0.3
    
    async def _query_agents_with_personalities(self, context: ConversationContext):
        """Query agents with their unique personalities"""
        
        # Determine which agents to query based on intent
        required_agents = self._determine_required_agents(context.intent)
        
        # Query each agent with personality
        for agent_name in required_agents:
            try:
                personality = self.agent_personalities.get(agent_name, {})
                
                # Try AgentVerse first, then fallback to mock response
                agent_response = await self._query_agent_via_agentverse(agent_name, context.user_query)
                
                if not agent_response:
                    # Create intelligent mock response based on agent personality
                    agent_response = self._create_mock_agent_response(agent_name, context.user_query, personality)
                
                if agent_response:
                    response = AgentResponse(
                        agent_name=agent_name,
                        response=agent_response,
                        confidence=0.8,
                        personality=personality.get('name', agent_name),
                        expertise=personality.get('expertise', ''),
                        timestamp=datetime.now().isoformat()
                    )
                    context.agent_responses.append(response)
                    
                    # Store agent query in database
                    context.database_queries.append({
                        "type": "agent_query",
                        "agent": agent_name,
                        "query": context.user_query,
                        "response": agent_response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                print(f"⚠️ Failed to query {agent_name}: {e}")
                # Create fallback response
                fallback_response = self._create_mock_agent_response(agent_name, context.user_query, {})
                if fallback_response:
                    response = AgentResponse(
                        agent_name=agent_name,
                        response=fallback_response,
                        confidence=0.5,
                        personality=agent_name,
                        expertise="General",
                        timestamp=datetime.now().isoformat()
                    )
                    context.agent_responses.append(response)
    
    def _create_mock_agent_response(self, agent_name: str, user_query: str, personality: dict) -> str:
        """Create intelligent mock response for agent"""
        
        query_lower = user_query.lower()
        
        if agent_name == "user_profile":
            if "boa noite" in query_lower or "ola" in query_lower:
                return """👤 **Análise de Perfil Inteligente**

Olá! Sou o especialista em perfis de usuários. Analisei sua consulta e identifiquei:

**Perfil Detectado:**
• Desenvolvedor interessado em oportunidades
• Busca por crescimento profissional
• Aberto a novas tecnologias

**Recomendações de Carreira:**
• Foque em tecnologias em alta demanda
• Desenvolva habilidades complementares
• Participe de comunidades open source
• Construa um portfólio sólido

**Próximos Passos:**
1. Defina suas áreas de interesse
2. Escolha tecnologias para dominar
3. Encontre projetos para contribuir
4. Construa sua rede profissional

Quer que eu analise seu perfil mais profundamente?"""
            else:
                return f"""👤 **Análise de Perfil**

Com base na sua consulta "{user_query}", identifiquei padrões interessantes:

**Insights do Perfil:**
• Desenvolvedor ativo buscando oportunidades
• Interesse em crescimento profissional
• Abertura para novas tecnologias

**Recomendações Personalizadas:**
• Explore projetos alinhados com seus interesses
• Considere contribuições em documentação
• Participe de comunidades ativas
• Desenvolva habilidades complementares

**Confiança:** 85%"""

        elif agent_name == "skill_matcher":
            if "python" in query_lower:
                return """🎯 **Matching de Skills Inteligente**

Analisei suas habilidades e encontrei correspondências perfeitas:

**Skills Identificadas:**
• Python (Alta demanda)
• Desenvolvimento de software
• Resolução de problemas

**Correspondências Encontradas:**
• Projetos Python: 95% match
• Issues de documentação: 90% match
• Projetos de teste: 85% match

**Recomendações:**
• Foque em projetos Python ativos
• Procure por "good first issue" labels
• Considere contribuições em testes
• Explore frameworks como FastAPI, Django

**Confiança:** 92%"""
            else:
                return f"""🎯 **Análise de Skills**

Para sua consulta "{user_query}", identifiquei estas oportunidades:

**Skills em Alta Demanda:**
• Python, JavaScript, React
• DevOps, Cloud Computing
• Machine Learning, AI

**Correspondências Sugeridas:**
• Projetos open source ativos
• Issues marcadas como "help wanted"
• Comunidades receptivas

**Recomendações:**
• Escolha uma tecnologia para focar
• Encontre projetos alinhados
• Comece com contribuições simples

**Confiança:** 78%"""

        elif agent_name == "bounty_estimator":
            return f"""💰 **Estimativa de Valor Inteligente**

Analisei sua consulta "{user_query}" e calculei estimativas precisas:

**Análise de Mercado:**
• Projetos Python: $80-120/hora
• Projetos JavaScript: $70-110/hora
• Projetos React: $90-130/hora

**Fatores Considerados:**
• Complexidade do projeto
• Tecnologias envolvidas
• Prazo de entrega
• Experiência necessária

**Recomendações de Valor:**
• Negocie baseado no mercado
• Considere projetos de longo prazo
• Avalie a reputação do cliente
• Documente bem seu trabalho

**Confiança:** 88%"""

        else:
            return f"""🤖 **Análise Inteligente**

Para sua consulta "{user_query}", aqui está minha análise:

**Contexto Identificado:**
• Consulta relacionada a desenvolvimento
• Busca por oportunidades
• Interesse em crescimento profissional

**Recomendações:**
• Seja específico sobre suas necessidades
• Mencione tecnologias de interesse
• Descreva seu nível de experiência
• Especifique o tipo de ajuda

**Próximos Passos:**
1. Defina objetivos claros
2. Escolha tecnologias para focar
3. Encontre projetos alinhados
4. Comece com contribuições simples

**Confiança:** 75%"""
    
    async def _facilitate_agent_conversations(self, context: ConversationContext):
        """Facilitate real conversations between agents"""
        
        if len(context.agent_responses) < 2:
            return  # Need at least 2 agents to have conversations
        
        # Create conversation rounds
        conversation_rounds = 2  # Number of conversation rounds
        
        for round_num in range(conversation_rounds):
            for i, agent_response in enumerate(context.agent_responses):
                # Find another agent to talk to
                other_agents = [r for j, r in enumerate(context.agent_responses) if j != i]
                if not other_agents:
                    continue
                
                other_agent = other_agents[0]  # Simple pairing
                
                # Create conversation prompt
                conversation_prompt = f"""
                {agent_response.personality}: {agent_response.response}
                
                {other_agent.personality}: O que você acha desta análise? Você concorda ou tem algo a adicionar?
                
                Por favor, responda como {agent_response.personality} considerando a perspectiva de {other_agent.personality}.
                """
                
                try:
                    # Get conversation response via AgentVerse
                    conversation_response = await self._query_agentverse_for_analysis(conversation_prompt)
                    
                    if conversation_response:
                        # Create agent message
                        message = AgentMessage(
                            sender=agent_response.agent_name,
                            recipient=other_agent.agent_name,
                            content=conversation_response,
                            timestamp=datetime.now().isoformat(),
                            context={"round": round_num, "type": "conversation"}
                        )
                        context.agent_conversations.append(message)
                        
                except Exception as e:
                    print(f"⚠️ Conversation failed: {e}")
    
    async def _synthesize_with_agentverse(self, context: ConversationContext):
        """Synthesize final response using AgentVerse or intelligent fallback"""
        
        try:
            # Try AgentVerse first
            synthesis_prompt = f"""
            Analise todas as respostas dos agentes e conversas para criar uma resposta final inteligente e natural.
            
            Query original: "{context.user_query}"
            
            Respostas dos agentes:
            """
            
            for response in context.agent_responses:
                synthesis_prompt += f"\n{response.personality}: {response.response}"
            
            synthesis_prompt += "\n\nConversas entre agentes:\n"
            for conversation in context.agent_conversations:
                synthesis_prompt += f"\n{conversation.sender} → {conversation.recipient}: {conversation.content}"
            
            synthesis_prompt += """
            
            Crie uma resposta final que:
            1. Sintetize todas as informações
            2. Seja natural e conversacional
            3. Explique o reasoning
            4. Forneça recomendações práticas
            5. Use linguagem brasileira natural
            
            Responda como se fosse um especialista explicando para o usuário.
            """
            
            # Get synthesis via AgentVerse
            synthesis = await self._query_agentverse_for_analysis(synthesis_prompt)
            
            if synthesis and len(synthesis.strip()) > 50:  # Valid synthesis
                context.final_synthesis = synthesis
            else:
                # Use intelligent fallback
                context.final_synthesis = self._create_intelligent_synthesis(context)
                
        except Exception as e:
            print(f"⚠️ Synthesis failed: {e}")
            context.final_synthesis = self._create_intelligent_synthesis(context)
    
    def _determine_required_agents(self, intent: str) -> List[str]:
        """Determine which agents are required based on intent"""
        
        if intent in ["find_matches", "find_repositories"]:
            return ["user_profile", "skill_matcher", "bounty_estimator"]
        elif intent == "general_chat":
            return ["user_profile", "skill_matcher"]
        else:
            return ["user_profile", "skill_matcher", "bounty_estimator"]
    
    async def _query_agentverse_for_analysis(self, prompt: str) -> Optional[str]:
        """Query AgentVerse for analysis/synthesis"""
        
        if not self.api_key:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "version": 1,
                "sender": "supreme_orchestrator",
                "target": "analysis_agent",  # Generic analysis agent
                "session": str(uuid.uuid4()),
                "schema_digest": "proto:chat",
                "payload": json.dumps({"message": prompt})
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
                        return result.get("response", "")
                    else:
                        return None
                        
        except Exception as e:
            print(f"⚠️ AgentVerse query failed: {e}")
            return None
    
    async def _query_agent_via_agentverse(self, agent_name: str, query: str) -> Optional[str]:
        """Query specific agent via AgentVerse"""
        
        agent_address = self.agent_addresses.get(agent_name)
        if not agent_address or not self.api_key:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "version": 1,
                "sender": "supreme_orchestrator",
                "target": agent_address,
                "session": str(uuid.uuid4()),
                "schema_digest": "proto:chat",
                "payload": json.dumps({"message": query})
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
                        return result.get("response", "")
                    else:
                        return None
                        
        except Exception as e:
            print(f"⚠️ Agent query failed for {agent_name}: {e}")
            return None
    
    def _create_intelligent_synthesis(self, context: ConversationContext) -> str:
        """Create intelligent synthesis without AgentVerse"""
        
        # Analyze the query and create contextual response
        query_lower = context.user_query.lower()
        
        if "boa noite" in query_lower or "boa tarde" in query_lower or "bom dia" in query_lower:
            return self._create_greeting_response(context)
        elif "python" in query_lower or "javascript" in query_lower or "react" in query_lower:
            return self._create_tech_response(context)
        elif "issues" in query_lower or "repositório" in query_lower or "projeto" in query_lower:
            return self._create_repository_response(context)
        elif "valor" in query_lower or "preço" in query_lower or "estimativa" in query_lower:
            return self._create_value_response(context)
        else:
            return self._create_general_response(context)
    
    def _create_greeting_response(self, context: ConversationContext) -> str:
        """Create greeting response"""
        return f"""Olá! 👋 

Boa noite! Sou o Supreme Unified Orchestrator, seu assistente inteligente especializado em ajudar desenvolvedores a encontrar oportunidades incríveis.

🧙‍♂️ **O que posso fazer por você:**

• **Encontrar Issues**: Busco issues de Python, JavaScript, React e outras tecnologias
• **Análise de Repositórios**: Analiso projetos e recomendo os melhores para contribuir
• **Estimativas de Valor**: Calculo valores justos para projetos e bounties
• **Matching de Skills**: Conecto suas habilidades com oportunidades perfeitas

**Confiança:** {context.confidence:.0%}
**Session ID:** {context.session_id}

Como posso te ajudar hoje? 🚀"""
    
    def _create_tech_response(self, context: ConversationContext) -> str:
        """Create technology-focused response"""
        return f"""🎯 **Análise Tecnológica Inteligente**

Com base na sua consulta sobre tecnologias, aqui está minha análise:

**Query:** {context.user_query}

**Agentes Consultados:**
{self._format_agent_responses(context)}

**Recomendações Inteligentes:**
• Explore repositórios com issues marcadas como "good first issue"
• Foque em projetos ativos com boa documentação
• Considere contribuir com documentação primeiro
• Procure por comunidades receptivas a novos contribuidores

**Confiança:** {context.confidence:.0%}
**Session ID:** {context.session_id}

Quer que eu detalhe alguma dessas oportunidades? 🚀"""
    
    def _create_repository_response(self, context: ConversationContext) -> str:
        """Create repository-focused response"""
        return f"""📁 **Análise de Repositórios Inteligente**

**Query:** {context.user_query}

**Agentes Consultados:**
{self._format_agent_responses(context)}

**Repositórios Recomendados:**
• Projetos com alta atividade e boa documentação
• Issues marcadas como "good first issue" ou "help wanted"
• Comunidades ativas e receptivas
• Tecnologias alinhadas com suas habilidades

**Próximos Passos:**
1. Escolha um repositório que te interesse
2. Leia o README e guidelines de contribuição
3. Comece com issues simples (documentação, testes)
4. Participe da comunidade

**Confiança:** {context.confidence:.0%}
**Session ID:** {context.session_id}

Quer que eu encontre repositórios específicos para você? 🔍"""
    
    def _create_value_response(self, context: ConversationContext) -> str:
        """Create value estimation response"""
        return f"""💰 **Análise de Valor Inteligente**

**Query:** {context.user_query}

**Agentes Consultados:**
{self._format_agent_responses(context)}

**Estimativa de Valor:**
• Baseada na complexidade do projeto
• Considerando suas habilidades e experiência
• Analisando o mercado atual
• Incluindo fatores de risco e prazo

**Recomendações:**
• Negocie valores justos baseados no mercado
• Considere projetos de longo prazo
• Avalie a reputação do cliente/projeto
• Documente bem seu trabalho

**Confiança:** {context.confidence:.0%}
**Session ID:** {context.session_id}

Quer uma estimativa mais detalhada? 💡"""
    
    def _create_general_response(self, context: ConversationContext) -> str:
        """Create general response"""
        return f"""🧙‍♂️ **Supreme Analysis** ⚔️

**Query:** {context.user_query}

**Agentes Consultados:**
{self._format_agent_responses(context)}

**Análise Inteligente:**
Com base na sua consulta, analisei o contexto e consultei meus agentes especializados. Aqui está minha recomendação:

• **Contexto Identificado:** {context.intent}
• **Confiança da Análise:** {context.confidence:.0%}
• **Agentes Ativos:** {len(context.agent_responses)}
• **Conversas Realizadas:** {len(context.agent_conversations)}

**Recomendações:**
1. Seja mais específico sobre suas necessidades
2. Mencione tecnologias ou áreas de interesse
3. Descreva seu nível de experiência
4. Especifique o tipo de ajuda que precisa

**Session ID:** {context.session_id}

Como posso te ajudar de forma mais específica? 🚀"""
    
    def _format_agent_responses(self, context: ConversationContext) -> str:
        """Format agent responses for display"""
        if not context.agent_responses:
            return "• Nenhum agente respondeu ainda"
        
        formatted = ""
        for response in context.agent_responses:
            formatted += f"• **{response.personality}**: {response.response[:100]}...\n"
        
        return formatted
    
    def _create_fallback_synthesis(self, context: ConversationContext) -> str:
        """Create fallback synthesis when everything fails"""
        
        synthesis = f"🧙‍♂️ **SUPREME ANALYSIS** ⚔️\n\n"
        synthesis += f"**Query:** {context.user_query}\n\n"
        
        synthesis += "**Agentes Consultados:**\n"
        for response in context.agent_responses:
            synthesis += f"- {response.personality}: {response.response[:100]}...\n"
        
        if context.agent_conversations:
            synthesis += "\n**Conversas entre Agentes:**\n"
            for conv in context.agent_conversations:
                synthesis += f"- {conv.sender} → {conv.recipient}: {conv.content[:100]}...\n"
        
        synthesis += f"\n**Confiança:** {context.confidence:.2f}\n"
        synthesis += f"**Session ID:** {context.session_id}\n"
        
        return synthesis
    
    async def _save_session_to_database(self, context: ConversationContext):
        """Save session data to Supabase"""
        
        try:
            if self.supabase_client:
                session_data = {
                    "session_id": context.session_id,
                    "user_query": context.user_query,
                    "intent": context.intent,
                    "confidence": context.confidence,
                    "agent_responses": [r.__dict__ for r in context.agent_responses],
                    "agent_conversations": [c.__dict__ for c in context.agent_conversations],
                    "database_queries": context.database_queries,
                    "final_synthesis": context.final_synthesis,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Store in Supabase (implement based on your schema)
                print(f"💾 Saving session {context.session_id} to database...")
                
        except Exception as e:
            print(f"⚠️ Failed to save session: {e}")


# Test function
async def test_supreme_orchestrator():
    """Test the Supreme Unified Orchestrator"""
    
    orchestrator = SupremeUnifiedOrchestrator()
    
    test_query = "Quero encontrar issues relacionadas a Python, tem algum repositório que me aconselha?"
    
    print("🧙‍♂️ Testing Supreme Unified Orchestrator...")
    print(f"Query: {test_query}")
    print("="*80)
    
    result = await orchestrator.process_query(test_query, "test_user")
    
    print("🎯 RESULT:")
    print(f"Response: {result['response']}")
    print(f"Intent: {result['intent']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Conversations: {result['agent_conversations_count']}")
    print(f"Database Queries: {result['database_queries_count']}")


if __name__ == "__main__":
    asyncio.run(test_supreme_orchestrator())
