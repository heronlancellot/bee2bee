import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'edge';

/**
 * POST /api/supreme-orchestrator - Send message to Supreme Unified Orchestrator
 *
 * This route connects the Next.js frontend with the Supreme Unified Orchestrator
 * that handles intelligent agent coordination with AgentVerse integration
 */
export async function POST(request: NextRequest) {
  try {
    const { message, user_id, conversation_id } = await request.json();

    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Call Supreme Unified Orchestrator
    const SUPREME_ORCHESTRATOR_URL = process.env.SUPREME_ORCHESTRATOR_URL || 'http://localhost:8020';
    
    const response = await fetch(`${SUPREME_ORCHESTRATOR_URL}/api/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        user_id: user_id || 'frontend_user',
        conversation_id: conversation_id || undefined,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Supreme Orchestrator error:', errorText);
      throw new Error(`Supreme Orchestrator error: ${response.status}`);
    }

    const result = await response.json();

    // Transform response to match frontend expectations
    return NextResponse.json({
      response: result.response,
      intent: result.intent,
      confidence: result.confidence,
      session_id: result.session_id,
      agent_conversations_count: result.agent_conversations_count,
      agent_responses_count: result.agent_responses_count,
      database_queries_count: result.database_queries_count,
      ai_synthesis_used: result.ai_synthesis_used,
      timestamp: result.timestamp,
      agent_id: 'supreme_orchestrator',
      conversation_id: conversation_id || result.session_id,
    });

  } catch (error) {
    console.error('Supreme Orchestrator API error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to get response from Supreme Orchestrator',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/supreme-orchestrator - Get Supreme Orchestrator capabilities
 */
export async function GET() {
  try {
    // Call Supreme Unified Orchestrator for capabilities
    const SUPREME_ORCHESTRATOR_URL = process.env.SUPREME_ORCHESTRATOR_URL || 'http://localhost:8020';
    
    const response = await fetch(`${SUPREME_ORCHESTRATOR_URL}/api/query`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Supreme Orchestrator error: ${response.status}`);
    }

    return NextResponse.json({
      agents: {
        'supreme_orchestrator': {
          name: 'Supreme Unified Orchestrator',
          description: 'Intelligent agent coordination with AgentVerse integration',
          capabilities: [
            'Context Analysis with AgentVerse',
            'Real Agent Conversations',
            'Agent Personalities',
            'Intelligent Database Interaction',
            'Real AI Synthesis'
          ],
          status: 'active'
        }
      },
      count: 1,
      status: 'active',
      features: [
        '🧠 Context Analysis with AgentVerse',
        '💬 Real Agent Conversations',
        '🎭 Agent Personalities',
        '🗄️ Intelligent Database Interaction',
        '🔄 Real AI Synthesis'
      ]
    });

  } catch (error) {
    console.error('Get Supreme Orchestrator capabilities error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch Supreme Orchestrator capabilities' },
      { status: 500 }
    );
  }
}



