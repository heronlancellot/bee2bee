-- Agent Knowledge Base Migration
-- Tables for smart agents to share knowledge and learn from each other

-- Agent Knowledge Base (shared learning)
CREATE TABLE IF NOT EXISTS public.agent_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    confidence NUMERIC(3,2) DEFAULT 0.7,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    access_count INTEGER DEFAULT 0
);

-- Conversations (chat history)
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT,
    messages JSONB DEFAULT '[]',
    intent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Profiles extension (for agent matching)
-- Note: This extends the existing profiles table with agent-specific data
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS skills TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}';

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_knowledge_agent ON public.agent_knowledge(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_knowledge_created ON public.agent_knowledge(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON public.conversations(user_id);

-- Comments
COMMENT ON TABLE public.agent_knowledge IS 'Shared knowledge base for all agents to learn from each other';
COMMENT ON TABLE public.conversations IS 'Chat history with intent tracking for agent orchestration';
