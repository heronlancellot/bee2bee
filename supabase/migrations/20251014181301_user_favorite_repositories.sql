CREATE TABLE public.user_favorite_repositories (
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  repository_id BIGINT NOT NULL REFERENCES public.repositories(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  PRIMARY KEY (user_id, repository_id)
);

ALTER TABLE public.user_favorite_repositories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own favorite repositories."
  ON public.user_favorite_repositories FOR ALL
  USING (auth.uid() = user_id);