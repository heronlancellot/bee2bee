/**
 * Supabase RAG System - Helper Functions
 *
 * Type-safe wrappers for the RAG database operations
 */

import { createClient } from '@supabase/supabase-js';

// ============================================================
// TYPES
// ============================================================

export type RepoStatus = 'pending' | 'indexing' | 'ready' | 'expired' | 'failed';
export type ChunkType = 'file' | 'function' | 'class' | 'interface' | 'module';
export type MessageRole = 'user' | 'assistant' | 'system';

export interface Repository {
  id: string;
  full_name: string;
  github_id?: number;
  description?: string;
  stars: number;
  forks: number;
  open_issues: number;
  language?: string;
  topics?: string[];
  license?: string;
  default_branch: string;
  status: RepoStatus;
  indexed_at?: string;
  indexing_started_at?: string;
  indexing_error?: string;
  last_interaction_at: string;
  expires_at?: string;
  total_files: number;
  total_chunks: number;
  total_embeddings: number;
  size_bytes: number;
  created_at: string;
  updated_at: string;
}

export interface UserRepository {
  id: string;
  user_id: string;
  repo_id: string;
  is_selected: boolean;
  added_at: string;
}

export interface FileMetadata {
  id: string;
  repo_id: string;
  file_path: string;
  file_hash: string;
  size_bytes?: number;
  lines?: number;
  language?: string;
  last_commit_sha?: string;
  last_commit_author?: string;
  last_commit_date?: string;
  last_modified?: string;
  indexed_at: string;
}

export interface CodeChunk {
  chunk_id: string;
  repo_id: string;
  file_path: string;
  file_hash: string;
  code: string;
  chunk_type: ChunkType;
  start_line?: number;
  end_line?: number;
  lines_of_code?: number;
  name?: string;
  signature?: string;
  docstring?: string;
  module?: string;
  created_at: string;
}

export interface Embedding {
  id: string;
  chunk_id: string;
  embedding: number[];
  model_name: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  user_id: string;
  role: MessageRole;
  content: string;
  repo_ids?: string[];
  sources?: ChatSource[];
  model_name?: string;
  tokens_used?: number;
  created_at: string;
}

export interface ChatSource {
  chunk_id: string;
  file_path: string;
  similarity: number;
  code?: string;
}

export interface SimilarChunk {
  chunk_id: string;
  repo_id: string;
  repo_full_name: string;
  file_path: string;
  code: string;
  chunk_type: ChunkType;
  name?: string;
  signature?: string;
  docstring?: string;
  similarity: number;
}

// ============================================================
// SUPABASE CLIENT
// ============================================================

// Initialize Supabase client (replace with your actual credentials)
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// ============================================================
// REPOSITORY OPERATIONS
// ============================================================

/**
 * Add a new repository for the current user
 */
export async function addRepository(
  fullName: string,
  githubId?: number,
  metadata?: Partial<Repository>
): Promise<Repository> {
  // 1. Check if repo already exists
  const { data: existingRepo } = await supabase
    .from('repositories')
    .select('id')
    .eq('full_name', fullName)
    .single();

  let repoId: string;

  if (existingRepo) {
    // Repo already indexed
    repoId = existingRepo.id;
  } else {
    // Insert new repo
    const { data: newRepo, error: repoError } = await supabase
      .from('repositories')
      .insert({
        full_name: fullName,
        github_id: githubId,
        status: 'pending',
        ...metadata,
      })
      .select()
      .single();

    if (repoError) throw repoError;
    repoId = newRepo.id;
  }

  // 2. Associate repo with user
  const { error: userRepoError } = await supabase
    .from('user_repositories')
    .insert({
      repo_id: repoId,
      is_selected: true, // Selected by default
    });

  // Ignore duplicate key error (user already added this repo)
  if (userRepoError && !userRepoError.message.includes('duplicate key')) {
    throw userRepoError;
  }

  // 3. Return full repo data
  const { data: repo, error: fetchError } = await supabase
    .from('repositories')
    .select('*')
    .eq('id', repoId)
    .single();

  if (fetchError) throw fetchError;
  return repo;
}

/**
 * Get all repositories for current user
 */
export async function getUserRepositories(includeExpired = false): Promise<(Repository & { is_selected: boolean })[]> {
  const query = supabase
    .from('user_selected_repos_view')
    .select('*')
    .order('added_at', { ascending: false });

  if (!includeExpired) {
    query.neq('status', 'expired');
  }

  const { data, error } = await query;

  if (error) throw error;
  return data || [];
}

/**
 * Toggle repository selection (checkbox)
 */
export async function toggleRepoSelection(repoId: string): Promise<boolean> {
  const { data, error } = await supabase
    .from('user_repositories')
    .update({ is_selected: supabase.sql`NOT is_selected` })
    .eq('repo_id', repoId)
    .select('is_selected')
    .single();

  if (error) throw error;
  return data.is_selected;
}

/**
 * Set repository selection state
 */
export async function setRepoSelection(repoId: string, isSelected: boolean): Promise<void> {
  const { error } = await supabase
    .from('user_repositories')
    .update({ is_selected: isSelected })
    .eq('repo_id', repoId);

  if (error) throw error;
}

/**
 * Get IDs of selected repositories
 */
export async function getSelectedRepoIds(): Promise<string[]> {
  const { data: user } = await supabase.auth.getUser();
  if (!user.user) throw new Error('Not authenticated');

  const { data, error } = await supabase.rpc('get_user_selected_repos', {
    user_uuid: user.user.id,
  });

  if (error) throw error;
  return data || [];
}

/**
 * Remove repository from user's library
 */
export async function removeRepository(repoId: string): Promise<void> {
  const { error } = await supabase
    .from('user_repositories')
    .delete()
    .eq('repo_id', repoId);

  if (error) throw error;
}

/**
 * Update repository interaction timestamp
 */
export async function updateRepoInteraction(repoId: string): Promise<void> {
  const { error } = await supabase.rpc('update_repo_interaction', {
    repo_uuid: repoId,
  });

  if (error) throw error;
}

// ============================================================
// RAG SEARCH OPERATIONS
// ============================================================

/**
 * Search for similar code chunks using embeddings
 *
 * @param queryEmbedding - Embedding vector from OpenAI (1536 dims)
 * @param threshold - Similarity threshold (0-1), default 0.7
 * @param limit - Max number of results, default 10
 */
export async function searchSimilarChunks(
  queryEmbedding: number[],
  threshold = 0.7,
  limit = 10
): Promise<SimilarChunk[]> {
  const { data: user } = await supabase.auth.getUser();
  if (!user.user) throw new Error('Not authenticated');

  const { data, error } = await supabase.rpc('search_similar_chunks', {
    user_uuid: user.user.id,
    query_embedding: queryEmbedding,
    match_threshold: threshold,
    match_count: limit,
  });

  if (error) throw error;
  return data || [];
}

/**
 * Generate embedding from text using OpenAI
 * (You'll need to implement this with your OpenAI API key)
 */
export async function generateEmbedding(text: string): Promise<number[]> {
  const OPENAI_API_KEY = process.env.NEXT_PUBLIC_OPENAI_API_KEY || '';

  const response = await fetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: 'text-embedding-3-small',
      input: text,
    }),
  });

  const json = await response.json();
  return json.data[0].embedding;
}

/**
 * Combined RAG search: generate embedding + search
 */
export async function ragSearch(
  query: string,
  threshold = 0.7,
  limit = 10
): Promise<SimilarChunk[]> {
  const embedding = await generateEmbedding(query);
  return searchSimilarChunks(embedding, threshold, limit);
}

// ============================================================
// CHAT OPERATIONS
// ============================================================

/**
 * Save user message
 */
export async function saveUserMessage(
  content: string,
  repoIds?: string[]
): Promise<ChatMessage> {
  const selectedRepos = repoIds || (await getSelectedRepoIds());

  const { data, error } = await supabase
    .from('chat_messages')
    .insert({
      role: 'user',
      content,
      repo_ids: selectedRepos,
    })
    .select()
    .single();

  if (error) throw error;
  return data;
}

/**
 * Save assistant message with sources
 */
export async function saveAssistantMessage(
  content: string,
  sources: ChatSource[],
  repoIds?: string[],
  modelName?: string,
  tokensUsed?: number
): Promise<ChatMessage> {
  const selectedRepos = repoIds || (await getSelectedRepoIds());

  const { data, error } = await supabase
    .from('chat_messages')
    .insert({
      role: 'assistant',
      content,
      repo_ids: selectedRepos,
      sources,
      model_name: modelName,
      tokens_used: tokensUsed,
    })
    .select()
    .single();

  if (error) throw error;
  return data;
}

/**
 * Get chat history for current user
 */
export async function getChatHistory(limit = 50): Promise<ChatMessage[]> {
  const { data, error } = await supabase
    .from('chat_messages')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(limit);

  if (error) throw error;
  return (data || []).reverse(); // Reverse to get chronological order
}

/**
 * Delete chat message
 */
export async function deleteChatMessage(messageId: string): Promise<void> {
  const { error } = await supabase
    .from('chat_messages')
    .delete()
    .eq('id', messageId);

  if (error) throw error;
}

/**
 * Clear all chat history for current user
 */
export async function clearChatHistory(): Promise<void> {
  const { data: user } = await supabase.auth.getUser();
  if (!user.user) throw new Error('Not authenticated');

  const { error } = await supabase
    .from('chat_messages')
    .delete()
    .eq('user_id', user.user.id);

  if (error) throw error;
}

// ============================================================
// FULL RAG CHAT FLOW
// ============================================================

/**
 * Complete RAG chat flow:
 * 1. Save user message
 * 2. Search similar chunks
 * 3. Generate LLM response with context
 * 4. Save assistant message
 */
export async function ragChat(
  userMessage: string,
  onProgress?: (status: string) => void
): Promise<{
  userMsg: ChatMessage;
  assistantMsg: ChatMessage;
  sources: SimilarChunk[];
}> {
  // 1. Save user message
  onProgress?.('Saving message...');
  const userMsg = await saveUserMessage(userMessage);

  // 2. Search similar chunks
  onProgress?.('Searching codebase...');
  const sources = await ragSearch(userMessage, 0.7, 5);

  // 3. Build context for LLM
  const context = sources
    .map((chunk, idx) => {
      return `[${idx + 1}] ${chunk.file_path}${chunk.name ? ` - ${chunk.name}` : ''}\n${chunk.code}`;
    })
    .join('\n\n---\n\n');

  // 4. Call LLM (replace with your LLM API)
  onProgress?.('Generating response...');
  const llmResponse = await callLLM(userMessage, context);

  // 5. Save assistant message
  const assistantMsg = await saveAssistantMessage(
    llmResponse.content,
    sources.map((s) => ({
      chunk_id: s.chunk_id,
      file_path: s.file_path,
      similarity: s.similarity,
    })),
    undefined,
    llmResponse.model,
    llmResponse.tokensUsed
  );

  return { userMsg, assistantMsg, sources };
}

/**
 * Call LLM with RAG context
 * (Replace with your actual LLM implementation)
 */
async function callLLM(
  userMessage: string,
  context: string
): Promise<{ content: string; model: string; tokensUsed: number }> {
  const OPENAI_API_KEY = process.env.NEXT_PUBLIC_OPENAI_API_KEY || '';

  const systemPrompt = `You are a helpful code assistant. Answer questions about the codebase using the provided context.

Context from codebase:
${context}

If the context doesn't contain relevant information, say so clearly.`;

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: 'gpt-4-turbo',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userMessage },
      ],
      temperature: 0.7,
    }),
  });

  const json = await response.json();

  return {
    content: json.choices[0].message.content,
    model: json.model,
    tokensUsed: json.usage.total_tokens,
  };
}

// ============================================================
// STATISTICS & ANALYTICS
// ============================================================

/**
 * Get user statistics
 */
export async function getUserStats(): Promise<{
  totalRepos: number;
  selectedRepos: number;
  totalMessages: number;
  totalTokens: number;
}> {
  const { data: user } = await supabase.auth.getUser();
  if (!user.user) throw new Error('Not authenticated');

  // Count repos
  const { count: totalRepos } = await supabase
    .from('user_repositories')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user.user.id);

  const { count: selectedRepos } = await supabase
    .from('user_repositories')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user.user.id)
    .eq('is_selected', true);

  // Count messages
  const { count: totalMessages } = await supabase
    .from('chat_messages')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user.user.id);

  // Sum tokens
  const { data: tokenData } = await supabase
    .from('chat_messages')
    .select('tokens_used')
    .eq('user_id', user.user.id);

  const totalTokens = (tokenData || []).reduce((sum, row) => sum + (row.tokens_used || 0), 0);

  return {
    totalRepos: totalRepos || 0,
    selectedRepos: selectedRepos || 0,
    totalMessages: totalMessages || 0,
    totalTokens,
  };
}

/**
 * Get most used chunks (from chat sources)
 */
export async function getMostUsedChunks(limit = 10): Promise<{
  chunk_id: string;
  file_path: string;
  times_used: number;
  avg_similarity: number;
}[]> {
  const { data: user } = await supabase.auth.getUser();
  if (!user.user) throw new Error('Not authenticated');

  // This requires a custom SQL query
  const { data, error } = await supabase.rpc('get_most_used_chunks', {
    user_uuid: user.user.id,
    limit_count: limit,
  });

  if (error) {
    console.error('getMostUsedChunks error:', error);
    return [];
  }

  return data || [];
}
