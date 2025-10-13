/**
 * Agentverse Agent Tools
 * Functions to interact with deployed agents on Agentverse
 */

const GITHUB_PROFILE_AGENT = 'agent1qwxydcn7vpksaw0vs3wuy4h2r6s65dunevll09aje0zjn27s039tknnvrm3';

/**
 * Analyze a GitHub profile using the GitHub Profile Analyzer agent
 */
export async function analyzeGitHubProfile(username: string, apiKey: string) {
  try {
    // Send message to agent via Agentverse Mailbox API
    const response = await fetch(`https://agentverse.ai/v1/agents/${GITHUB_PROFILE_AGENT}/messages`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        type: 'text',
        content: username
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
      agent_address: GITHUB_PROFILE_AGENT,
      username,
      response: data
    };
  } catch (error: any) {
    return {
      error: 'Failed to analyze GitHub profile via agent',
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
