import { NextRequest, NextResponse } from 'next/server';
import { analyzeGitHubProfile } from '@/lib/agentverse-tools';

export const runtime = 'edge';

export async function POST(request: NextRequest) {
  try {
    const { username } = await request.json();

    if (!username) {
      return NextResponse.json(
        { error: 'Username is required' },
        { status: 400 }
      );
    }

    const apiKey = process.env.AGENTVERSE_API_KEY;

    if (!apiKey) {
      return NextResponse.json(
        { error: 'Agentverse API key not configured' },
        { status: 500 }
      );
    }

    // Call the GitHub Profile Analyzer agent
    const result = await analyzeGitHubProfile(username, apiKey);

    if (result.error) {
      return NextResponse.json(result, { status: 500 });
    }

    return NextResponse.json(result);

  } catch (error) {
    console.error('GitHub analysis error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
