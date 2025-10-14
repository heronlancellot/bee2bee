import { NextRequest, NextResponse } from 'next/server';
import { supabase } from '@/integrations/supabase/client';

export const runtime = 'edge';

/**
 * POST /api/smart-agents - Send message to smart agents
 *
 * This route connects the Next.js frontend with the Python smart agents
 * that handle repository analysis, skill matching, bounty estimation, etc.
 */
export async function POST(request: NextRequest) {
  try {
    const { message, user_id, conversation_id, context } = await request.json();

    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Call Python HTTP server
    const PYTHON_SERVER_URL = process.env.PYTHON_SERVER_URL || 'http://localhost:5001';
    
    const response = await fetch(`${PYTHON_SERVER_URL}/api/smart-agents`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        user_id,
        conversation_id,
        context,
      }),
    });

    if (!response.ok) {
      throw new Error(`Python server error: ${response.status}`);
    }

    const result = await response.json();

    // Save conversation to Supabase
    if (user_id && result.conversation_id) {
      try {
        const messages = [
          {
            role: 'user',
            content: message,
            timestamp: new Date().toISOString(),
            user_id: user_id
          },
          {
            role: 'assistant',
            content: result.response,
            agent_id: result.agent_id,
            timestamp: new Date().toISOString()
          }
        ];

        await supabase
          .from('conversations')
          .upsert({
            id: result.conversation_id,
            user_id: user_id,
            messages: messages,
            intent: result.intent
          });

        // Save knowledge for non-general chats
        if (result.intent !== 'general_chat') {
          await supabase
            .from('agent_knowledge')
            .insert({
              agent_id: result.agent_id,
              topic: result.intent,
              content: result.response,
              tags: [result.intent, result.agent_id],
              confidence: result.intent_confidence || 0.7
            });
        }

      } catch (dbError) {
        console.error('Database error:', dbError);
      }
    }

    return NextResponse.json({
      response: result.response,
      intent: result.intent,
      intent_confidence: result.intent_confidence,
      agent_id: result.agent_id,
      conversation_id: result.conversation_id,
      metadata: result.metadata,
      timestamp: result.timestamp
    });

  } catch (error) {
    console.error('Smart agents API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * GET /api/smart-agents - Get smart agents capabilities
 */
export async function GET() {
  try {
    // Call Python HTTP server for capabilities
    const PYTHON_SERVER_URL = process.env.PYTHON_SERVER_URL || 'http://localhost:5001';
    
    const response = await fetch(`${PYTHON_SERVER_URL}/api/smart-agents`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Python server error: ${response.status}`);
    }

    const data = await response.json();

    return NextResponse.json({
      agents: data.agents || {},
      count: data.count || 0,
      status: data.status || 'active'
    });

  } catch (error) {
    console.error('Get smart agents error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch smart agents' },
      { status: 500 }
    );
  }
}
