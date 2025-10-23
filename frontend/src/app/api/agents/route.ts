import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'edge';

// Backend API URL - should be configured via environment variable
const AGENTS_API_URL = process.env.AGENTS_API_URL || 'http://localhost:5001';

/**
 * POST /api/agents - Send message to intelligent agents
 *
 * This route connects the Next.js frontend with the Python backend
 * that orchestrates Sigmar and Slaanesh agents with LLM integration
 */
export async function POST(request: NextRequest) {
  try {
    const { messages, agents, context, conversation_id } = await request.json();

    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return NextResponse.json(
        { error: 'Messages array is required' },
        { status: 400 }
      );
    }

    // Get the last user message
    const lastMessage = messages[messages.length - 1];
    if (!lastMessage || lastMessage.role !== 'user') {
      return NextResponse.json(
        { error: 'Last message must be from user' },
        { status: 400 }
      );
    }

    // Call Python backend API
    const response = await fetch(`${AGENTS_API_URL}/api/chat/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: lastMessage.content,
        agents: agents || ['sigmar', 'slaanesh'], // Default to both agents
        context: context,
        conversation_id: conversation_id,
      }),
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error('Agents API error:', errorData);
      return NextResponse.json(
        { error: 'Failed to get response from agents' },
        { status: response.status }
      );
    }

    const data = await response.json();

    // Poll for responses (simple polling strategy)
    // In production, you'd use WebSockets for real-time updates
    const queryIds = data.query_ids || [];
    const conversationId = data.conversation_id;

    // Wait a bit for agents to process (agents check every 3 seconds)
    await new Promise(resolve => setTimeout(resolve, 100000));

    // Get conversation history with responses
    const conversationResponse = await fetch(
      `${AGENTS_API_URL}/api/chat/conversation/${conversationId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!conversationResponse.ok) {
      return NextResponse.json(
        { error: 'Failed to get conversation history' },
        { status: conversationResponse.status }
      );
    }

    const conversationData = await conversationResponse.json();
    const allMessages = conversationData.messages || [];

    // Get the latest agent responses
    const agentResponses = allMessages
      .filter((msg: any) => msg.role === 'agent' || msg.agent_id)
      .slice(-2); // Get last 2 agent responses

    // Combine responses if multiple agents responded
    let combinedResponse = '';
    const agentsUsed: string[] = [];

    if (agentResponses.length > 0) {
      agentResponses.forEach((response: any) => {
        if (response.content) {
          combinedResponse += response.content + '\n\n';
          if (response.agent_name) {
            agentsUsed.push(response.agent_name);
          }
        }
      });
    } else {
      // Fallback if no responses yet
      combinedResponse = 'Agents are processing your request. Please wait a moment and try again.';
    }

    return NextResponse.json({
      message: combinedResponse.trim(),
      conversation_id: conversationId,
      agents_used: agentsUsed,
      query_ids: queryIds,
    });

  } catch (error) {
    console.error('Agents API route error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * GET /api/agents - Get available agents and their status
 */
export async function GET() {
  try {
    const response = await fetch(`${AGENTS_API_URL}/api/agents`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to get agents' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      agents: data.agents || [],
      count: data.count || 0,
    });

  } catch (error) {
    console.error('Get agents error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch agents' },
      { status: 500 }
    );
  }
}
