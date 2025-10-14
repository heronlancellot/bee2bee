import { NextRequest, NextResponse } from "next/server";
import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { Database } from "@/integrations/supabase/types";




export async function POST(request: NextRequest) {
  const supabase = createRouteHandlerClient<Database>({ cookies });

  try {
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

        const repoData = await request.json()
    if (!repoData || !repoData.id || !repoData.full_name) {
      return NextResponse.json(
        { error: "Missing required repository data" },
        { status: 400 },
      );
    }

    const { data, error } = await supabase
      .from("repositories")
      .upsert({
        id: repoData.id,
        user_id: session.user.id,
        name: repoData.name,
        full_name: repoData.full_name,
        owner: repoData.owner,
        description: repoData.description,
        is_private: repoData.is_private,
        language: repoData.language,
        stars: repoData.stars,
        default_branch: repoData.default_branch,
        branches: repoData.branches,
        complexity_score: repoData.complexity_score,
        complexity_tier: repoData.complexity_tier,
        size_category: repoData.size_category,
        difficulty_tier: repoData.difficulty_tier,
        project_type: repoData.project_type,
        tech_domains: repoData.tech_domains,
        indexed_at: new Date().toISOString(),
      })
      .select()
      .single();

    if (error) {
      console.error("Supabase error:", error.message);
      return NextResponse.json(
        { error: "Failed to save repository data", details: error.message },
        { status: 500 },
      );
    }

    return NextResponse.json(
      { message: "Repository saved successfully", repository: data },
      { status: 200 },
    );
  } catch (e) {
    let errorMessage = "An unexpected error occurred";
    if (e instanceof Error) {
      errorMessage = e.message;
    }
    console.error("Server error:", errorMessage);
    return NextResponse.json(
      { error: "An unexpected error occurred", details: errorMessage },
      { status: 500 },
    );
  }
}
