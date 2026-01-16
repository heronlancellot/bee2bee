import { NextRequest, NextResponse } from 'next/server';
import { analyzeRepository } from '@/lib/agentverse-tools';

export const runtime = 'edge';

export async function POST(request: NextRequest) {
  try {
    const { repository } = await request.json();

    if (!repository) {
      return NextResponse.json(
        { error: 'Repository name is required (format: "owner/repo")' },
        { status: 400 }
      );
    }

    // Validate format
    if (!repository.includes('/')) {
      return NextResponse.json(
        { error: 'Invalid repository format. Use "owner/repo" (e.g., "facebook/react")' },
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

    // Call the Repository Analyzer agent
    const result = await analyzeRepository(repository, apiKey);

    if (result.error) {
      return NextResponse.json(result, { status: 500 });
    }

    return NextResponse.json(result);

  } catch (error) {
    console.error('Repository analysis error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
