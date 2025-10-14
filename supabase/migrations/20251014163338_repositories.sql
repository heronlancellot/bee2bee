CREATE TABLE public.repositories (
  id BIGINT PRIMARY KEY,
  -- Foreign key to the user who first indexed this repository
  user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  -- Core GitHub metadata
  name TEXT NOT NULL,
  full_name TEXT NOT NULL UNIQUE,
  owner TEXT NOT NULL,
  description TEXT,
  is_private BOOLEAN NOT NULL DEFAULT FALSE,
  language TEXT,
  stars INT NOT NULL DEFAULT 0,
  default_branch TEXT,
  branches TEXT[], 

  -- Analysis Insights (cached from agent)
  complexity_score INT CHECK (complexity_score >= 0 AND complexity_score <= 100),
  complexity_tier TEXT, 
  size_category TEXT, 
  difficulty_tier TEXT, 
  project_type TEXT,  
  tech_domains TEXT[],

  indexed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.repositories IS 'Stores cached data and AI analysis insights for GitHub repositories.';
COMMENT ON COLUMN public.repositories.id IS 'The unique integer ID from the GitHub API.';
COMMENT ON COLUMN public.repositories.indexed_at IS 'Timestamp of the last successful analysis/indexing.';

CREATE INDEX idx_repositories_user_id ON public.repositories(user_id);
CREATE INDEX idx_repositories_full_name ON public.repositories(full_name);

ALTER TABLE public.repositories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Repositories are viewable by everyone."
  ON public.repositories FOR SELECT
  USING (true);

CREATE POLICY "Users can insert repositories."
  ON public.repositories FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Users can update repositories they added."
  ON public.repositories FOR UPDATE
  USING (auth.uid() = user_id);