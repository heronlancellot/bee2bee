import { NextRequest, NextResponse } from 'next/server';

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

export async function POST(request: NextRequest) {
  try {
    const { messages } = await request.json();

    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json(
        { error: 'Messages array is required' },
        { status: 400 }
      );
    }

    const apiKey = process.env.ASI_ONE_API_KEY;
    const agentverseApiKey = process.env.AGENTVERSE_API_KEY;

    if (!apiKey) {
      return NextResponse.json(
        { error: 'ASI_ONE_API_KEY not configured' },
        { status: 500 }
      );
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
      messages: messages.map((msg: any) => ({
        role: msg.role,
        content: msg.content
      })),
      tools,
      tool_choice: 'auto', // Let ASI-1 decide when to use tools
      temperature: 0.7,
      stream: false,
    };

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
      return NextResponse.json(
        { error: 'Failed to get response from ASI-1' },
        { status: response.status }
      );
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

      return NextResponse.json({
        message: finalMessage,
        model: 'asi1-mini',
        tools_used: message.tool_calls.map((call: any) => call.function.name),
      });
    }

    // No tool calls - return direct response
    const assistantMessage = message?.content;

    if (!assistantMessage) {
      return NextResponse.json(
        { error: 'No response from ASI-1' },
        { status: 500 }
      );
    }

    return NextResponse.json({
      message: assistantMessage,
      model: 'asi1-mini',
    });

  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
