import { NextRequest, NextResponse } from 'next/server';

import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';
import type { Database, TablesInsert } from '@/integrations/supabase/types';

type RepositoryInsert = TablesInsert<'repositories'>;

export async function POST(request: NextRequest) {
  const cookieStore = cookies();
  const supabase = createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value;
        },
        set(name: string, value: string, options) {
          cookieStore.set({ name, value, ...options });
        },
        remove(name: string, options) {
          cookieStore.set({ name, value: '', ...options });
        },
      },
    }
  );

  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const repoData = await request.json() as any;

    if (!repoData || !repoData.id || !repoData.full_name || !repoData.name || !repoData.owner) {
      return NextResponse.json({ error: 'Missing required repository data' }, { status: 400 });
    }

    const repositoryToUpsert: RepositoryInsert = {
      id: Number(repoData.id),
      user_id: session.user.id,
      name: String(repoData.name),
      full_name: String(repoData.full_name),
      owner: String(repoData.owner),
      description: repoData.description ? String(repoData.description) : null,
      is_private: Boolean(repoData.is_private),
      language: repoData.language ? String(repoData.language) : null,
      stars: repoData.stars ? Number(repoData.stars) : 0,
      default_branch: repoData.default_branch ? String(repoData.default_branch) : null,
      branches: Array.isArray(repoData.branches) ? repoData.branches : null,
      complexity_score: repoData.complexity_score ? Number(repoData.complexity_score) : null,
      complexity_tier: repoData.complexity_tier ? String(repoData.complexity_tier) : null,
      size_category: repoData.size_category ? String(repoData.size_category) : null,
      difficulty_tier: repoData.difficulty_tier ? String(repoData.difficulty_tier) : null,
      project_type: repoData.project_type ? String(repoData.project_type) : null,
      tech_domains: Array.isArray(repoData.tech_domains) ? repoData.tech_domains : null,
      indexed_at: new Date().toISOString(),
    };

    const { data, error } = await supabase
      .from("repositories")
      .upsert(repositoryToUpsert)
      .select()
      .single();

    if (error) {
      console.error('Supabase upsert error:', error.message);
      return NextResponse.json({ error: 'Failed to save repository', details: error.message }, { status: 500 });
    }

    return NextResponse.json({ message: 'Repository saved successfully', repository: data }, { status: 200 });

  } catch (e) {
    let errorMessage = 'An unexpected error occurred';
    if (e instanceof Error) {
      errorMessage = e.message;
    }
    console.error('Server error:', errorMessage);
    return NextResponse.json({ error: 'An unexpected server error occurred', details: errorMessage }, { status: 500 });
  }
}
