import { NextRequest, NextResponse } from 'next/server';
import { supabase } from '@/integrations/supabase/client';

export const runtime = 'edge';

// Tool implementation: Search Agentverse agents
async function searchAgentverseAgents(query: string, limit: number, apiKey?: string) {
  if (!apiKey) {
    return { error: 'Agentverse API key not configured' };
  }

  try {
    const response = await fetch('https://agentverse.ai/v1/search/agents', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        filters: {
          state: [],
          category: [],
          agent_type: [],
          protocol_digest: []
        },
        sort: 'relevancy',
        direction: 'asc',
        search_text: query,
        offset: 0,
        limit,
      }),
    });

    if (!response.ok) {
      return { error: `Agentverse API error: ${response.statusText}` };
    }

    const data = await response.json();
    return {
      agents: data.agents || [],
      total: data.total || 0,
      query
    };
  } catch (error) {
    return { error: 'Failed to search agents' };
  }
}

// Tool implementation: Get repository context
async function getRepositoryContext(repoId: string) {
  // TODO: Implement actual repository context fetching
  // For now, return mock data
  return {
    repo_id: repoId,
    name: 'Example Repository',
    description: 'This is a placeholder. Implement actual repo fetching logic.',
    complexity_score: 65,
    tech_stack: ['TypeScript', 'React', 'Next.js']
  };
}

// ASI-1 Chat function for general conversations
async function chatWithASI(message: string, user_id?: string) {
  const apiKey = process.env.ASI_ONE_API_KEY;
  const agentverseApiKey = process.env.AGENTVERSE_API_KEY;

  if (!apiKey) {
    return { error: 'ASI_ONE_API_KEY not configured' };
  }

  // Define tools (functions) that ASI-1 can call
  const tools = [
    {
      type: 'function',
      function: {
        name: 'search_agentverse_agents',
        description: 'Search for AI agents on Agentverse marketplace by capability, technology, or domain',
        parameters: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Search query for finding agents (e.g., "Next.js expert", "code analyzer")'
            },
            limit: {
              type: 'number',
              description: 'Maximum number of agents to return (default: 5)'
            }
          },
          required: ['query']
        }
      }
    },
    {
      type: 'function',
      function: {
        name: 'get_repository_context',
        description: 'Get context and information about a specific repository',
        parameters: {
          type: 'object',
          properties: {
            repo_id: {
              type: 'string',
              description: 'Repository ID'
            }
          },
          required: ['repo_id']
        }
      }
    }
  ];

  // Build request body with tools
  const requestBody: any = {
    model: 'asi1-mini',
    messages: [
      {
        role: 'user',
        content: message
      }
    ],
    tools,
    tool_choice: 'auto', // Let ASI-1 decide when to use tools
    temperature: 0.7,
    stream: false,
  };

  try {
    // Call ASI-1 API with MCP (Fetch.ai LLM + Agentverse agents)
    const response = await fetch('https://api.asi1.ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error('ASI-1 API error:', errorData);
      return { error: 'Failed to get response from ASI-1' };
    }

    const data = await response.json();
    const message = data.choices?.[0]?.message;

    // Check if ASI-1 wants to call tools
    if (message?.tool_calls && message.tool_calls.length > 0) {
      // Execute tool calls
      const toolResults = await Promise.all(
        message.tool_calls.map(async (toolCall: any) => {
          const toolName = toolCall.function.name;
          const toolArgs = JSON.parse(toolCall.function.arguments);

          let result;

          // Execute the appropriate tool
          if (toolName === 'search_agentverse_agents') {
            result = await searchAgentverseAgents(toolArgs.query, toolArgs.limit || 5, agentverseApiKey);
          } else if (toolName === 'get_repository_context') {
            result = await getRepositoryContext(toolArgs.repo_id);
          } else {
            result = { error: 'Unknown tool' };
          }

          return {
            role: 'tool',
            tool_call_id: toolCall.id,
            content: JSON.stringify(result)
          };
        })
      );

      // Send tool results back to ASI-1 for final response
      const followUpResponse = await fetch('https://api.asi1.ai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          ...requestBody,
          messages: [
            ...requestBody.messages,
            message,
            ...toolResults
          ]
        }),
      });

      if (!followUpResponse.ok) {
        throw new Error('Failed to get final response from ASI-1');
      }

      const finalData = await followUpResponse.json();
      const finalMessage = finalData.choices?.[0]?.message?.content;

      return {
        response: finalMessage,
        model: 'asi1-mini',
        tools_used: message.tool_calls.map((call: any) => call.function.name),
      };
    }

    // No tool calls - return direct response
    const assistantMessage = message?.content;

    if (!assistantMessage) {
      return { error: 'No response from ASI-1' };
    }

    return {
      response: assistantMessage,
      model: 'asi1-mini',
    };

  } catch (error) {
    console.error('ASI-1 Chat error:', error);
    return { error: 'Failed to chat with ASI-1' };
  }
}

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

    // If it's a general chat, use ASI-1 instead of Python agents
    if (result.intent === 'general_chat') {
      console.log('🤖 Using ASI-1 for general chat...');
      
      const asiResult = await chatWithASI(message, user_id);
      
      if (asiResult.error) {
        // Fallback to Python response if ASI fails
        console.error('ASI-1 error, using Python fallback:', asiResult.error);
      } else {
        // Use ASI-1 response
        result.response = asiResult.response;
        result.model = asiResult.model;
        result.tools_used = asiResult.tools_used;
      }
    }

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
      timestamp: result.timestamp,
      model: result.model || 'python_agents',
      tools_used: result.tools_used
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
