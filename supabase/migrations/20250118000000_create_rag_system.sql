-- ============================================================
-- RepoMind RAG System - Complete Migration
-- ============================================================
-- Description: Complete database schema for repository indexing,
--              embeddings storage, and RAG-based chat system
-- Features:
--   - Global repository expiration (30 days inactivity)
--   - NotebookLM-style source selection (checkboxes)
--   - pgvector 0.7.0 with HNSW indexes
--   - Incremental indexing with hash-based change detection
-- ============================================================

-- ============================================================
-- EXTENSIONS
-- ============================================================

-- Enable pgvector for embeddings storage
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;

-- Enable pg_cron for scheduled tasks (marking expired repos)
CREATE EXTENSION IF NOT EXISTS pg_cron WITH SCHEMA extensions;


-- ============================================================
-- CUSTOM TYPES
-- ============================================================

-- Repository indexing status
CREATE TYPE public.repo_status AS ENUM (
  'pending',      -- Added but not yet indexed
  'indexing',     -- Currently being indexed
  'ready',        -- Fully indexed and ready for queries
  'expired',      -- Expired due to inactivity (30 days)
  'failed'        -- Indexing failed
);

-- Code chunk types
CREATE TYPE public.chunk_type AS ENUM (
  'file',         -- Entire file (for small files)
  'function',     -- Function/method
  'class',        -- Class definition
  'interface',    -- Interface/type definition
  'module'        -- Module-level chunk
);

-- Chat message roles
CREATE TYPE public.message_role AS ENUM (
  'user',
  'assistant',
  'system'
);


-- ============================================================
-- TABLE 1: REPOSITORIES
-- ============================================================
-- Stores indexed GitHub repositories (shared across all users)
-- Expires after 30 days without ANY user interaction

CREATE TABLE public.repositories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- GitHub identifiers
  full_name TEXT NOT NULL UNIQUE,           -- "facebook/react"
  github_id BIGINT UNIQUE,                  -- GitHub's numeric ID

  -- Repository metadata (from GitHub API or Bee2Bee Metadata)
  description TEXT,
  stars INTEGER DEFAULT 0,
  forks INTEGER DEFAULT 0,
  open_issues INTEGER DEFAULT 0,
  language TEXT,                            -- Primary language
  topics TEXT[],                            -- Array of topics
  license TEXT,
  default_branch TEXT DEFAULT 'main',

  -- Indexing status
  status public.repo_status DEFAULT 'pending',
  indexed_at TIMESTAMPTZ,                   -- When indexing completed
  indexing_started_at TIMESTAMPTZ,          -- When indexing started
  indexing_error TEXT,                      -- Error message if failed

  -- Expiration tracking (GLOBAL across all users)
  last_interaction_at TIMESTAMPTZ DEFAULT NOW(),  -- Updated on ANY user interaction
  expires_at TIMESTAMPTZ,                         -- Calculated: last_interaction + 30 days

  -- Stats
  total_files INTEGER DEFAULT 0,
  total_chunks INTEGER DEFAULT 0,
  total_embeddings INTEGER DEFAULT 0,
  size_bytes BIGINT DEFAULT 0,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_repositories_status ON public.repositories(status);
CREATE INDEX idx_repositories_full_name ON public.repositories(full_name);
CREATE INDEX idx_repositories_github_id ON public.repositories(github_id);
CREATE INDEX idx_repositories_expires_at ON public.repositories(expires_at) WHERE status = 'ready';
CREATE INDEX idx_repositories_topics ON public.repositories USING GIN(topics);

-- Comments
COMMENT ON TABLE public.repositories IS 'Indexed GitHub repositories with global expiration (30 days)';
COMMENT ON COLUMN public.repositories.last_interaction_at IS 'Updated when ANY user interacts (chat, search, view)';
COMMENT ON COLUMN public.repositories.expires_at IS 'Automatically calculated as last_interaction_at + 30 days';


-- ============================================================
-- TABLE 2: USER_REPOSITORIES
-- ============================================================
-- Many-to-many relationship: users ↔ repositories
-- Tracks which repos each user has added and which are selected for context

CREATE TABLE public.user_repositories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Relationships
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  repo_id UUID NOT NULL REFERENCES public.repositories(id) ON DELETE CASCADE,

  -- Selection state (NotebookLM-style checkbox)
  is_selected BOOLEAN DEFAULT true,         -- Checkbox in sidebar

  -- Metadata
  added_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  UNIQUE(user_id, repo_id)                  -- User can add same repo only once
);

-- Indexes
CREATE INDEX idx_user_repos_user_id ON public.user_repositories(user_id);
CREATE INDEX idx_user_repos_repo_id ON public.user_repositories(repo_id);
CREATE INDEX idx_user_repos_selected ON public.user_repositories(user_id, is_selected) WHERE is_selected = true;

-- Comments
COMMENT ON TABLE public.user_repositories IS 'User repository selections with NotebookLM-style checkboxes';
COMMENT ON COLUMN public.user_repositories.is_selected IS 'Whether repo is included in chat context (sidebar checkbox)';


-- ============================================================
-- TABLE 3: FILE_METADATA
-- ============================================================
-- Stores metadata about files (1 row per file)
-- Used for incremental indexing (hash-based change detection)

CREATE TABLE public.file_metadata (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Relationships
  repo_id UUID NOT NULL REFERENCES public.repositories(id) ON DELETE CASCADE,

  -- File identification
  file_path TEXT NOT NULL,                  -- "src/components/Button.tsx"
  file_hash TEXT NOT NULL,                  -- SHA256 hash for change detection

  -- File information
  size_bytes INTEGER,
  lines INTEGER,
  language TEXT,

  -- Git metadata (optional)
  last_commit_sha TEXT,
  last_commit_author TEXT,
  last_commit_date TIMESTAMPTZ,

  -- Timestamps
  last_modified TIMESTAMPTZ,
  indexed_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  UNIQUE(repo_id, file_path)
);

-- Indexes
CREATE INDEX idx_file_metadata_repo_id ON public.file_metadata(repo_id);
CREATE INDEX idx_file_metadata_file_hash ON public.file_metadata(file_hash);
CREATE INDEX idx_file_metadata_file_path ON public.file_metadata(repo_id, file_path);
CREATE INDEX idx_file_metadata_language ON public.file_metadata(language);

-- Comments
COMMENT ON TABLE public.file_metadata IS 'File-level metadata for incremental indexing';
COMMENT ON COLUMN public.file_metadata.file_hash IS 'SHA256 hash for detecting content changes';


-- ============================================================
-- TABLE 4: CODE_CHUNKS
-- ============================================================
-- Stores code chunks extracted from files (N chunks per file)

CREATE TABLE public.code_chunks (
  chunk_id TEXT PRIMARY KEY,                -- "repo_file_func_hash"

  -- Relationships
  repo_id UUID NOT NULL REFERENCES public.repositories(id) ON DELETE CASCADE,
  file_path TEXT NOT NULL,
  file_hash TEXT NOT NULL,                  -- Same as file_metadata.file_hash

  -- Chunk content
  code TEXT NOT NULL,
  chunk_type public.chunk_type DEFAULT 'file',

  -- Location in file
  start_line INTEGER,
  end_line INTEGER,
  lines_of_code INTEGER,

  -- Code metadata
  name TEXT,                                -- Function/class name
  signature TEXT,                           -- Full signature
  docstring TEXT,                           -- Documentation
  module TEXT,                              -- Module/namespace

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Foreign key (optional, for referential integrity)
  FOREIGN KEY (repo_id, file_path) REFERENCES public.file_metadata(repo_id, file_path) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_chunks_repo_id ON public.code_chunks(repo_id);
CREATE INDEX idx_chunks_file_path ON public.code_chunks(file_path);
CREATE INDEX idx_chunks_file_hash ON public.code_chunks(file_hash);
CREATE INDEX idx_chunks_type ON public.code_chunks(chunk_type);
CREATE INDEX idx_chunks_name ON public.code_chunks(name) WHERE name IS NOT NULL;

-- Comments
COMMENT ON TABLE public.code_chunks IS 'Code chunks (functions, classes, files) ready for embedding';
COMMENT ON COLUMN public.code_chunks.file_hash IS 'Links to file_metadata for incremental updates';


-- ============================================================
-- TABLE 5: EMBEDDINGS
-- ============================================================
-- Stores vector embeddings for semantic search

CREATE TABLE public.embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Relationship
  chunk_id TEXT NOT NULL REFERENCES public.code_chunks(chunk_id) ON DELETE CASCADE,

  -- Vector (OpenAI text-embedding-3-small = 1536 dimensions)
  embedding VECTOR(1536) NOT NULL,

  -- Metadata
  model_name TEXT DEFAULT 'text-embedding-3-small',
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  UNIQUE(chunk_id)                          -- 1 embedding per chunk
);

-- Indexes for vector similarity search (pgvector 0.7.0 HNSW)
CREATE INDEX idx_embeddings_hnsw ON public.embeddings
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- Regular index for chunk_id lookups
CREATE INDEX idx_embeddings_chunk_id ON public.embeddings(chunk_id);

-- Comments
COMMENT ON TABLE public.embeddings IS 'Vector embeddings for RAG similarity search';
COMMENT ON COLUMN public.embeddings.embedding IS 'OpenAI text-embedding-3-small (1536 dims)';
COMMENT ON INDEX idx_embeddings_hnsw IS 'HNSW index for fast cosine similarity search';


-- ============================================================
-- TABLE 6: CHAT_MESSAGES
-- ============================================================
-- Stores chat message history between users and repo agents

CREATE TABLE public.chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Relationships
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Message content
  role public.message_role NOT NULL,
  content TEXT NOT NULL,

  -- Context (which repos were selected when this message was sent)
  repo_ids UUID[],                          -- Array of repo IDs in context

  -- Sources (for assistant messages - which chunks were used)
  sources JSONB,                            -- [{ chunk_id, file_path, score }]

  -- Metadata
  model_name TEXT,                          -- LLM model used (for assistant)
  tokens_used INTEGER,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_chat_messages_user_id ON public.chat_messages(user_id);
CREATE INDEX idx_chat_messages_created_at ON public.chat_messages(created_at DESC);
CREATE INDEX idx_chat_messages_repo_ids ON public.chat_messages USING GIN(repo_ids);
CREATE INDEX idx_chat_messages_sources ON public.chat_messages USING GIN(sources);

-- Comments
COMMENT ON TABLE public.chat_messages IS 'Chat history with RAG context tracking';
COMMENT ON COLUMN public.chat_messages.repo_ids IS 'Repos that were selected (checked) when message was sent';
COMMENT ON COLUMN public.chat_messages.sources IS 'Source chunks used for RAG (assistant messages only)';


-- ============================================================
-- FUNCTIONS
-- ============================================================

-- ------------------------------------------------------------
-- Function: update_repo_interaction
-- Description: Updates last_interaction_at and recalculates expires_at
-- Triggered by: Chat messages, search queries, repo views
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.update_repo_interaction(repo_uuid UUID)
RETURNS void AS $$
BEGIN
  UPDATE public.repositories
  SET
    last_interaction_at = NOW(),
    expires_at = NOW() + INTERVAL '30 days',
    status = CASE
      WHEN status = 'expired' THEN 'pending'  -- Revive expired repos
      ELSE status
    END
  WHERE id = repo_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.update_repo_interaction IS 'Updates repo last_interaction_at and extends expiration';


-- ------------------------------------------------------------
-- Function: mark_expired_repos
-- Description: Marks repos as expired if no interaction for 30 days
-- Scheduled: Daily via pg_cron
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.mark_expired_repos()
RETURNS TABLE(expired_count INTEGER) AS $$
DECLARE
  affected_rows INTEGER;
BEGIN
  UPDATE public.repositories
  SET status = 'expired'
  WHERE status = 'ready'
    AND expires_at < NOW();

  GET DIAGNOSTICS affected_rows = ROW_COUNT;

  RETURN QUERY SELECT affected_rows;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.mark_expired_repos IS 'Cron job: marks repos expired after 30 days inactivity';


-- ------------------------------------------------------------
-- Function: cleanup_expired_repos
-- Description: Deletes data from expired repos (manual trigger)
-- Warning: Destructive! Only call when sure no users need the data
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.cleanup_expired_repos(days_expired INTEGER DEFAULT 7)
RETURNS TABLE(deleted_repos INTEGER, deleted_chunks INTEGER, deleted_embeddings INTEGER) AS $$
DECLARE
  repos_deleted INTEGER;
  chunks_deleted INTEGER;
  embeddings_deleted INTEGER;
  expired_repo_ids UUID[];
BEGIN
  -- Find repos expired for more than X days
  SELECT ARRAY_AGG(id) INTO expired_repo_ids
  FROM public.repositories
  WHERE status = 'expired'
    AND expires_at < NOW() - (days_expired || ' days')::INTERVAL;

  -- Count chunks before deletion
  SELECT COUNT(*) INTO chunks_deleted
  FROM public.code_chunks
  WHERE repo_id = ANY(expired_repo_ids);

  -- Count embeddings before deletion
  SELECT COUNT(*) INTO embeddings_deleted
  FROM public.embeddings e
  JOIN public.code_chunks c ON e.chunk_id = c.chunk_id
  WHERE c.repo_id = ANY(expired_repo_ids);

  -- Delete repositories (cascades to chunks, embeddings, etc.)
  DELETE FROM public.repositories
  WHERE id = ANY(expired_repo_ids);

  GET DIAGNOSTICS repos_deleted = ROW_COUNT;

  RETURN QUERY SELECT repos_deleted, chunks_deleted, embeddings_deleted;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.cleanup_expired_repos IS 'Deletes repos expired for X days (default 7)';


-- ------------------------------------------------------------
-- Function: get_user_selected_repos
-- Description: Returns array of repo IDs that user has selected (checkbox)
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.get_user_selected_repos(user_uuid UUID)
RETURNS UUID[] AS $$
DECLARE
  selected_repo_ids UUID[];
BEGIN
  SELECT ARRAY_AGG(repo_id) INTO selected_repo_ids
  FROM public.user_repositories
  WHERE user_id = user_uuid
    AND is_selected = true;

  RETURN COALESCE(selected_repo_ids, ARRAY[]::UUID[]);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.get_user_selected_repos IS 'Returns array of repo IDs selected by user';


-- ------------------------------------------------------------
-- Function: search_similar_chunks
-- Description: Semantic search in user's selected repos
-- Parameters:
--   - user_uuid: User ID
--   - query_embedding: Query vector (1536 dims)
--   - match_threshold: Similarity threshold (0-1)
--   - match_count: Max results to return
-- Returns: Chunks with similarity scores, filtered by selected repos
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.search_similar_chunks(
  user_uuid UUID,
  query_embedding VECTOR(1536),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 10
)
RETURNS TABLE(
  chunk_id TEXT,
  repo_id UUID,
  repo_full_name TEXT,
  file_path TEXT,
  code TEXT,
  chunk_type public.chunk_type,
  name TEXT,
  signature TEXT,
  docstring TEXT,
  similarity FLOAT
) AS $$
DECLARE
  selected_repos UUID[];
BEGIN
  -- Get user's selected repos
  selected_repos := public.get_user_selected_repos(user_uuid);

  -- If no repos selected, return empty
  IF ARRAY_LENGTH(selected_repos, 1) IS NULL THEN
    RETURN;
  END IF;

  -- Perform similarity search
  RETURN QUERY
  SELECT
    c.chunk_id,
    c.repo_id,
    r.full_name as repo_full_name,
    c.file_path,
    c.code,
    c.chunk_type,
    c.name,
    c.signature,
    c.docstring,
    1 - (e.embedding <=> query_embedding) as similarity
  FROM public.embeddings e
  JOIN public.code_chunks c ON e.chunk_id = c.chunk_id
  JOIN public.repositories r ON c.repo_id = r.id
  WHERE c.repo_id = ANY(selected_repos)
    AND r.status = 'ready'  -- Only search in ready repos
    AND 1 - (e.embedding <=> query_embedding) > match_threshold
  ORDER BY e.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.search_similar_chunks IS 'RAG similarity search filtered by user selected repos';


-- ============================================================
-- TRIGGERS
-- ============================================================

-- ------------------------------------------------------------
-- Trigger: Auto-update updated_at timestamp
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_repositories
  BEFORE UPDATE ON public.repositories
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_updated_at();


-- ------------------------------------------------------------
-- Trigger: Update repo interaction on chat message
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.trigger_update_repo_interaction()
RETURNS TRIGGER AS $$
DECLARE
  repo_uuid UUID;
BEGIN
  -- Update last_interaction_at for all repos in context
  FOREACH repo_uuid IN ARRAY NEW.repo_ids
  LOOP
    PERFORM public.update_repo_interaction(repo_uuid);
  END LOOP;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_chat_message_insert
  AFTER INSERT ON public.chat_messages
  FOR EACH ROW
  EXECUTE FUNCTION public.trigger_update_repo_interaction();

COMMENT ON TRIGGER on_chat_message_insert ON public.chat_messages IS 'Updates repo interaction timestamp when user sends chat message';


-- ------------------------------------------------------------
-- Trigger: Calculate expires_at when repo becomes ready
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.trigger_calculate_expiration()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'ready' AND OLD.status != 'ready' THEN
    NEW.indexed_at = NOW();
    NEW.expires_at = NOW() + INTERVAL '30 days';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_repo_status_ready
  BEFORE UPDATE ON public.repositories
  FOR EACH ROW
  WHEN (NEW.status = 'ready' AND OLD.status IS DISTINCT FROM 'ready')
  EXECUTE FUNCTION public.trigger_calculate_expiration();

COMMENT ON TRIGGER on_repo_status_ready ON public.repositories IS 'Sets indexed_at and expires_at when repo becomes ready';


-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================

-- Enable RLS on all tables
ALTER TABLE public.repositories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_repositories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.code_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;


-- ------------------------------------------------------------
-- RLS: repositories
-- All users can view indexed repos (they're public!)
-- Only service role can modify
-- ------------------------------------------------------------

CREATE POLICY "Anyone can view ready repositories"
  ON public.repositories FOR SELECT
  USING (status = 'ready');

CREATE POLICY "Service role can manage repositories"
  ON public.repositories FOR ALL
  USING (auth.role() = 'service_role');


-- ------------------------------------------------------------
-- RLS: user_repositories
-- Users can only see/modify their own repository selections
-- ------------------------------------------------------------

CREATE POLICY "Users can view their own repo selections"
  ON public.user_repositories FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own repo selections"
  ON public.user_repositories FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own repo selections"
  ON public.user_repositories FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own repo selections"
  ON public.user_repositories FOR DELETE
  USING (auth.uid() = user_id);


-- ------------------------------------------------------------
-- RLS: file_metadata, code_chunks, embeddings
-- Public read (users can search across all indexed repos)
-- Service role only for writes
-- ------------------------------------------------------------

CREATE POLICY "Anyone can view file metadata"
  ON public.file_metadata FOR SELECT
  USING (true);

CREATE POLICY "Service role can manage file metadata"
  ON public.file_metadata FOR ALL
  USING (auth.role() = 'service_role');

CREATE POLICY "Anyone can view code chunks"
  ON public.code_chunks FOR SELECT
  USING (true);

CREATE POLICY "Service role can manage code chunks"
  ON public.code_chunks FOR ALL
  USING (auth.role() = 'service_role');

CREATE POLICY "Anyone can view embeddings"
  ON public.embeddings FOR SELECT
  USING (true);

CREATE POLICY "Service role can manage embeddings"
  ON public.embeddings FOR ALL
  USING (auth.role() = 'service_role');


-- ------------------------------------------------------------
-- RLS: chat_messages
-- Users can only see their own messages
-- ------------------------------------------------------------

CREATE POLICY "Users can view their own chat messages"
  ON public.chat_messages FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own chat messages"
  ON public.chat_messages FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own chat messages"
  ON public.chat_messages FOR DELETE
  USING (auth.uid() = user_id);


-- ============================================================
-- SCHEDULED JOBS (pg_cron)
-- ============================================================

-- Mark expired repos daily at 3 AM UTC
SELECT cron.schedule(
  'mark-expired-repos-daily',
  '0 3 * * *',  -- Every day at 3 AM
  $$SELECT public.mark_expired_repos()$$
);

COMMENT ON EXTENSION pg_cron IS 'Scheduled task: mark_expired_repos() runs daily at 3 AM UTC';


-- ============================================================
-- HELPER VIEWS (Optional - for easier queries)
-- ============================================================

-- View: User's selected repos with stats
CREATE OR REPLACE VIEW public.user_selected_repos_view AS
SELECT
  ur.user_id,
  ur.repo_id,
  ur.is_selected,
  ur.added_at,
  r.full_name,
  r.description,
  r.stars,
  r.language,
  r.status,
  r.total_files,
  r.total_chunks,
  r.last_interaction_at,
  r.expires_at
FROM public.user_repositories ur
JOIN public.repositories r ON ur.repo_id = r.id;

COMMENT ON VIEW public.user_selected_repos_view IS 'User repo selections with full repo details';


-- ============================================================
-- GRANTS (Optional - for specific service accounts)
-- ============================================================

-- Grant usage on schema to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO anon;

-- Grant execute on functions to authenticated users
GRANT EXECUTE ON FUNCTION public.get_user_selected_repos TO authenticated;
GRANT EXECUTE ON FUNCTION public.search_similar_chunks TO authenticated;
GRANT EXECUTE ON FUNCTION public.update_repo_interaction TO authenticated;

-- Service role gets full access
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO service_role;


-- ============================================================
-- INITIAL DATA (Optional)
-- ============================================================

-- You can add seed data here if needed
-- Example: INSERT INTO public.repositories (full_name, status) VALUES ('facebook/react', 'pending');


-- ============================================================
-- MIGRATION COMPLETE
-- ============================================================

-- Verify installation
DO $$
BEGIN
  RAISE NOTICE '✅ RAG System migration completed successfully!';
  RAISE NOTICE '📊 Tables created: 6 (repositories, user_repositories, file_metadata, code_chunks, embeddings, chat_messages)';
  RAISE NOTICE '🔧 Functions created: 5 (update_repo_interaction, mark_expired_repos, cleanup_expired_repos, get_user_selected_repos, search_similar_chunks)';
  RAISE NOTICE '⚡ Triggers created: 3 (updated_at, update_interaction, calculate_expiration)';
  RAISE NOTICE '🔒 RLS enabled on all tables';
  RAISE NOTICE '⏰ Cron job scheduled: mark_expired_repos (daily 3 AM UTC)';
  RAISE NOTICE '🎯 Next steps:';
  RAISE NOTICE '   1. Test connection: SELECT * FROM public.repositories LIMIT 1;';
  RAISE NOTICE '   2. Add a repo: INSERT INTO public.repositories (full_name) VALUES (''facebook/react'');';
  RAISE NOTICE '   3. Test search: SELECT public.search_similar_chunks(auth.uid(), ''[0.1,0.2,...]''::vector(1536), 0.7, 10);';
END $$;
