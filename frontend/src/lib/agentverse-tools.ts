/**
 * Agentverse Agent Tools
 * Functions to interact with deployed agents on Agentverse
 *
 * Note: These agents run locally with Mailbox integration (not hosted on Agentverse cloud)
 * because they require MeTTa (hyperon) which only works on Linux/Mac, not in Agentverse containers.
 */

// Agent addresses (these are locally running agents connected via Mailbox)
const REPOSITORY_ANALYZER_AGENT = 'agent1qdk5p9ssk358gppkg9eufxf3ftzf50fttvxppfp5fa3y3qa6ff9asnxe4sa';

/**
 * Analyze a GitHub repository using the Repository Analyzer agent
 */
export async function analyzeRepository(repoFullName: string, apiKey: string) {
  try {
    // Send message to agent via Agentverse Mailbox API
    const response = await fetch(`https://agentverse.ai/v1/agents/${REPOSITORY_ANALYZER_AGENT}/messages`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        type: 'text',
        content: repoFullName // Format: "owner/repo" (e.g., "facebook/react")
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return {
        error: `Failed to contact agent: ${response.statusText}`,
        details: errorText
      };
    }

    const data = await response.json();
    return {
      success: true,
      agent_address: REPOSITORY_ANALYZER_AGENT,
      repository: repoFullName,
      response: data
    };
  } catch (error: any) {
    return {
      error: 'Failed to analyze repository via agent',
      details: error.message
    };
  }
}

/**
 * Get agent status
 */
export async function getAgentStatus(agentAddress: string, apiKey: string) {
  try {
    const response = await fetch(`https://agentverse.ai/v1/hosting/agents/${agentAddress}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      return { error: `Failed to get agent status: ${response.statusText}` };
    }

    return await response.json();
  } catch (error: any) {
    return { error: error.message };
  }
}

/**
 * List all available agents
 */
export const AGENTS = {
  REPOSITORY: {
    address: REPOSITORY_ANALYZER_AGENT,
    name: 'Repository Analyzer',
    description: 'Analyzes GitHub repositories for complexity, tech stack, and difficulty using MeTTa reasoning',
    inputFormat: 'Repository in format "owner/repo" (e.g., "facebook/react")'
  }
} as const;
