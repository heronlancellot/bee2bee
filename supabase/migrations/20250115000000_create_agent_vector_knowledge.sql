-- Agent Knowledge Vector Database Migration
-- Integrates pg-vector with existing Supabase schema for semantic search
-- Migration: 20250115000000_create_agent_vector_knowledge.sql

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema for agent knowledge (if not exists)
CREATE SCHEMA IF NOT EXISTS agent_knowledge;

-- Agent registry table (extends existing agent_knowledge table)
CREATE TABLE IF NOT EXISTS agent_knowledge.agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    agent_type VARCHAR(100) NOT NULL, -- 'skill_matcher', 'bounty_estimator', 'user_profile'
    port INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Knowledge patterns table with vector embeddings
CREATE TABLE IF NOT EXISTS agent_knowledge.knowledge_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agent_knowledge.agents(id) ON DELETE CASCADE,
    pattern_type VARCHAR(100) NOT NULL, -- 'skill_match', 'bounty_estimation', 'user_profile'
    
    -- Semantic content for embedding
    semantic_text TEXT NOT NULL,
    embedding VECTOR(1536), -- OpenAI ada-002 dimension
    
    -- Structured data
    pattern_data JSONB NOT NULL,
    
    -- Performance metrics
    success_score FLOAT DEFAULT 0.0,
    confidence_score FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_success_score CHECK (success_score >= 0 AND success_score <= 1),
    CONSTRAINT valid_confidence_score CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- Knowledge relationships table
CREATE TABLE IF NOT EXISTS agent_knowledge.knowledge_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_pattern_id UUID REFERENCES agent_knowledge.knowledge_patterns(id) ON DELETE CASCADE,
    target_pattern_id UUID REFERENCES agent_knowledge.knowledge_patterns(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL, -- 'similar', 'prerequisite', 'alternative', 'conflict'
    strength FLOAT DEFAULT 0.5, -- Relationship strength 0-1
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_strength CHECK (strength >= 0 AND strength <= 1),
    CONSTRAINT no_self_relationship CHECK (source_pattern_id != target_pattern_id)
);

-- Query logs for optimization
CREATE TABLE IF NOT EXISTS agent_knowledge.query_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_text TEXT NOT NULL,
    query_embedding VECTOR(1536),
    agent_id UUID REFERENCES agent_knowledge.agents(id),
    results_count INTEGER DEFAULT 0,
    response_time_ms INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge synthesis cache
CREATE TABLE IF NOT EXISTS agent_knowledge.synthesis_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_hash VARCHAR(64) UNIQUE NOT NULL, -- SHA256 of query
    query_text TEXT NOT NULL,
    synthesis_result JSONB NOT NULL,
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '1 hour'),
    
    CONSTRAINT valid_cache_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_patterns_agent_type ON agent_knowledge.knowledge_patterns(agent_id, pattern_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_patterns_embedding ON agent_knowledge.knowledge_patterns USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_knowledge_patterns_success ON agent_knowledge.knowledge_patterns(success_score DESC);
CREATE INDEX IF NOT EXISTS idx_knowledge_patterns_usage ON agent_knowledge.knowledge_patterns(usage_count DESC);
CREATE INDEX IF NOT EXISTS idx_knowledge_patterns_created ON agent_knowledge.knowledge_patterns(created_at DESC);

-- Relationship indexes
CREATE INDEX IF NOT EXISTS idx_relationships_source ON agent_knowledge.knowledge_relationships(source_pattern_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON agent_knowledge.knowledge_relationships(target_pattern_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON agent_knowledge.knowledge_relationships(relationship_type);

-- Query log indexes
CREATE INDEX IF NOT EXISTS idx_query_logs_agent ON agent_knowledge.query_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_created ON agent_knowledge.query_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_query_logs_success ON agent_knowledge.query_logs(success);

-- Cache indexes
CREATE INDEX IF NOT EXISTS idx_synthesis_cache_hash ON agent_knowledge.synthesis_cache(query_hash);
CREATE INDEX IF NOT EXISTS idx_synthesis_cache_expires ON agent_knowledge.synthesis_cache(expires_at);

-- Functions for automatic updates
CREATE OR REPLACE FUNCTION agent_knowledge.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic timestamp updates
DROP TRIGGER IF EXISTS trigger_agents_updated_at ON agent_knowledge.agents;
CREATE TRIGGER trigger_agents_updated_at
    BEFORE UPDATE ON agent_knowledge.agents
    FOR EACH ROW EXECUTE FUNCTION agent_knowledge.update_updated_at();

DROP TRIGGER IF EXISTS trigger_patterns_updated_at ON agent_knowledge.knowledge_patterns;
CREATE TRIGGER trigger_patterns_updated_at
    BEFORE UPDATE ON agent_knowledge.knowledge_patterns
    FOR EACH ROW EXECUTE FUNCTION agent_knowledge.update_updated_at();

-- Function to increment usage count
CREATE OR REPLACE FUNCTION agent_knowledge.increment_usage(pattern_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE agent_knowledge.knowledge_patterns 
    SET usage_count = usage_count + 1,
        last_accessed_at = NOW()
    WHERE id = pattern_id;
END;
$$ LANGUAGE plpgsql;

-- Function for semantic search
CREATE OR REPLACE FUNCTION agent_knowledge.semantic_search(
    query_embedding VECTOR(1536),
    pattern_type_filter VARCHAR(100) DEFAULT NULL,
    agent_type_filter VARCHAR(100) DEFAULT NULL,
    limit_count INTEGER DEFAULT 10,
    similarity_threshold FLOAT DEFAULT 0.7
)
RETURNS TABLE (
    pattern_id UUID,
    semantic_text TEXT,
    pattern_data JSONB,
    similarity_score FLOAT,
    agent_name VARCHAR(255),
    success_score FLOAT,
    confidence_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        kp.id,
        kp.semantic_text,
        kp.pattern_data,
        1 - (kp.embedding <=> query_embedding) AS similarity_score,
        a.agent_name,
        kp.success_score,
        kp.confidence_score
    FROM agent_knowledge.knowledge_patterns kp
    JOIN agent_knowledge.agents a ON kp.agent_id = a.id
    WHERE 
        (pattern_type_filter IS NULL OR kp.pattern_type = pattern_type_filter)
        AND (agent_type_filter IS NULL OR a.agent_type = agent_type_filter)
        AND (1 - (kp.embedding <=> query_embedding)) >= similarity_threshold
    ORDER BY kp.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function for knowledge synthesis
CREATE OR REPLACE FUNCTION agent_knowledge.synthesize_knowledge(
    query_text TEXT,
    query_embedding VECTOR(1536),
    synthesis_type VARCHAR(100) DEFAULT 'comprehensive'
)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    skill_patterns JSONB;
    bounty_patterns JSONB;
    profile_patterns JSONB;
BEGIN
    -- Get patterns by type
    SELECT jsonb_agg(
        jsonb_build_object(
            'pattern_id', pattern_id,
            'semantic_text', semantic_text,
            'pattern_data', pattern_data,
            'similarity_score', similarity_score,
            'agent_name', agent_name,
            'success_score', success_score,
            'confidence_score', confidence_score
        )
    ) INTO skill_patterns
    FROM agent_knowledge.semantic_search(query_embedding, 'skill_match', NULL, 5, 0.6);
    
    SELECT jsonb_agg(
        jsonb_build_object(
            'pattern_id', pattern_id,
            'semantic_text', semantic_text,
            'pattern_data', pattern_data,
            'similarity_score', similarity_score,
            'agent_name', agent_name,
            'success_score', success_score,
            'confidence_score', confidence_score
        )
    ) INTO bounty_patterns
    FROM agent_knowledge.semantic_search(query_embedding, 'bounty_estimation', NULL, 5, 0.6);
    
    SELECT jsonb_agg(
        jsonb_build_object(
            'pattern_id', pattern_id,
            'semantic_text', semantic_text,
            'pattern_data', pattern_data,
            'similarity_score', similarity_score,
            'agent_name', agent_name,
            'success_score', success_score,
            'confidence_score', confidence_score
        )
    ) INTO profile_patterns
    FROM agent_knowledge.semantic_search(query_embedding, 'user_profile', NULL, 5, 0.6);
    
    -- Build synthesis result
    result := jsonb_build_object(
        'query', query_text,
        'synthesis_type', synthesis_type,
        'timestamp', NOW(),
        'skill_patterns', COALESCE(skill_patterns, '[]'::jsonb),
        'bounty_patterns', COALESCE(bounty_patterns, '[]'::jsonb),
        'profile_patterns', COALESCE(profile_patterns, '[]'::jsonb),
        'total_patterns', 
            COALESCE(jsonb_array_length(skill_patterns), 0) +
            COALESCE(jsonb_array_length(bounty_patterns), 0) +
            COALESCE(jsonb_array_length(profile_patterns), 0)
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Insert initial agents
INSERT INTO agent_knowledge.agents (agent_id, agent_name, agent_type, port) VALUES
('skill_matcher_001', 'Intelligent Skill Matcher Agent', 'skill_matcher', 8010),
('bounty_estimator_001', 'Bounty Estimator Agent', 'bounty_estimator', 8011),
('user_profile_001', 'User Profile Agent', 'user_profile', 8009),
('knowledge_synthesizer_001', 'Knowledge Synthesizer Agent', 'knowledge_synthesizer', 8013)
ON CONFLICT (agent_id) DO NOTHING;

-- Create views for easy access
CREATE OR REPLACE VIEW agent_knowledge.pattern_summary AS
SELECT 
    a.agent_name,
    a.agent_type,
    kp.pattern_type,
    COUNT(*) as pattern_count,
    AVG(kp.success_score) as avg_success_score,
    AVG(kp.confidence_score) as avg_confidence_score,
    SUM(kp.usage_count) as total_usage,
    MAX(kp.created_at) as latest_pattern
FROM agent_knowledge.knowledge_patterns kp
JOIN agent_knowledge.agents a ON kp.agent_id = a.id
GROUP BY a.agent_name, a.agent_type, kp.pattern_type;

-- Performance monitoring view
CREATE OR REPLACE VIEW agent_knowledge.performance_metrics AS
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    agent_id,
    COUNT(*) as query_count,
    AVG(response_time_ms) as avg_response_time,
    COUNT(*) FILTER (WHERE success = true) * 100.0 / COUNT(*) as success_rate
FROM agent_knowledge.query_logs
GROUP BY DATE_TRUNC('hour', created_at), agent_id
ORDER BY hour DESC;

-- Enable Row Level Security for agent knowledge tables
ALTER TABLE agent_knowledge.agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_knowledge.knowledge_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_knowledge.knowledge_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_knowledge.query_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_knowledge.synthesis_cache ENABLE ROW LEVEL SECURITY;

-- RLS Policies for agent knowledge (allow all for now - can be restricted later)
CREATE POLICY "Allow all operations on agents" ON agent_knowledge.agents FOR ALL USING (true);
CREATE POLICY "Allow all operations on knowledge_patterns" ON agent_knowledge.knowledge_patterns FOR ALL USING (true);
CREATE POLICY "Allow all operations on knowledge_relationships" ON agent_knowledge.knowledge_relationships FOR ALL USING (true);
CREATE POLICY "Allow all operations on query_logs" ON agent_knowledge.query_logs FOR ALL USING (true);
CREATE POLICY "Allow all operations on synthesis_cache" ON agent_knowledge.synthesis_cache FOR ALL USING (true);

-- Comments
COMMENT ON SCHEMA agent_knowledge IS 'Vector database schema for agent knowledge sharing and semantic search';
COMMENT ON TABLE agent_knowledge.agents IS 'Registry of all autonomous agents in the system';
COMMENT ON TABLE agent_knowledge.knowledge_patterns IS 'Knowledge patterns with vector embeddings for semantic search';
COMMENT ON TABLE agent_knowledge.knowledge_relationships IS 'Relationships between knowledge patterns for learning';
COMMENT ON TABLE agent_knowledge.query_logs IS 'Query logs for performance monitoring and optimization';
COMMENT ON TABLE agent_knowledge.synthesis_cache IS 'Cache for knowledge synthesis results';
