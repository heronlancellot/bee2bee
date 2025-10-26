# RAG System - SQL Queries Reference

## Índice

1. [Operações de Repositórios](#operações-de-repositórios)
2. [Seleção de Repos pelo Usuário](#seleção-de-repos-pelo-usuário)
3. [Busca Semântica (RAG)](#busca-semântica-rag)
4. [Indexação Incremental](#indexação-incremental)
5. [Chat e Interações](#chat-e-interações)
6. [Manutenção e Limpeza](#manutenção-e-limpeza)
7. [Estatísticas e Analytics](#estatísticas-e-analytics)

---

## Operações de Repositórios

### Adicionar Novo Repositório

```sql
-- 1. Inserir repositório (inicialmente com status 'pending')
INSERT INTO public.repositories (full_name, github_id, description, language)
VALUES (
  'facebook/react',
  10270250,
  'The library for web and native user interfaces',
  'JavaScript'
)
RETURNING id, full_name, status;

-- 2. Associar ao usuário
INSERT INTO public.user_repositories (user_id, repo_id, is_selected)
VALUES (
  auth.uid(),  -- ID do usuário logado
  'repo-uuid-from-previous-insert',
  true  -- Selecionado por padrão
);
```

### Atualizar Status do Repositório

```sql
-- Marcar como "indexando"
UPDATE public.repositories
SET status = 'indexing', indexing_started_at = NOW()
WHERE full_name = 'facebook/react';

-- Marcar como "ready" após indexação completa
UPDATE public.repositories
SET status = 'ready', indexed_at = NOW(), expires_at = NOW() + INTERVAL '30 days'
WHERE full_name = 'facebook/react';

-- Marcar como "failed" se indexação falhar
UPDATE public.repositories
SET status = 'failed', indexing_error = 'GitHub API rate limit exceeded'
WHERE full_name = 'facebook/react';
```

### Buscar Repositórios por Status

```sql
-- Repos prontos para uso
SELECT id, full_name, language, stars, total_chunks, expires_at
FROM public.repositories
WHERE status = 'ready'
ORDER BY stars DESC;

-- Repos pendentes de indexação
SELECT id, full_name, created_at
FROM public.repositories
WHERE status = 'pending'
ORDER BY created_at ASC;

-- Repos expirados (precisam re-indexar)
SELECT id, full_name, expires_at, last_interaction_at
FROM public.repositories
WHERE status = 'expired'
ORDER BY expires_at DESC;
```

---

## Seleção de Repos pelo Usuário

### Listar Repos do Usuário (Com Checkbox Status)

```sql
-- Usando a view helper
SELECT *
FROM public.user_selected_repos_view
WHERE user_id = auth.uid()
ORDER BY added_at DESC;

-- Ou com query manual
SELECT
  ur.id,
  ur.is_selected,  -- Checkbox status
  ur.added_at,
  r.full_name,
  r.description,
  r.stars,
  r.language,
  r.status,
  r.total_chunks,
  r.expires_at
FROM public.user_repositories ur
JOIN public.repositories r ON ur.repo_id = r.id
WHERE ur.user_id = auth.uid()
ORDER BY ur.added_at DESC;
```

### Selecionar/Desselecionar Repositório (Checkbox)

```sql
-- Marcar como selecionado (checkbox ON)
UPDATE public.user_repositories
SET is_selected = true
WHERE user_id = auth.uid()
  AND repo_id = 'repo-uuid';

-- Desmarcar (checkbox OFF)
UPDATE public.user_repositories
SET is_selected = false
WHERE user_id = auth.uid()
  AND repo_id = 'repo-uuid';

-- Toggle (inverter estado)
UPDATE public.user_repositories
SET is_selected = NOT is_selected
WHERE user_id = auth.uid()
  AND repo_id = 'repo-uuid';
```

### Obter Repos Selecionados (Array de IDs)

```sql
-- Usando função helper
SELECT public.get_user_selected_repos(auth.uid());
-- Retorna: {uuid1, uuid2, uuid3}

-- Ou com query manual
SELECT ARRAY_AGG(repo_id)
FROM public.user_repositories
WHERE user_id = auth.uid()
  AND is_selected = true;
```

---

## Busca Semântica (RAG)

### Buscar Chunks Similares (Função Principal)

```sql
-- Busca semântica nos repos selecionados pelo usuário
SELECT *
FROM public.search_similar_chunks(
  auth.uid(),                    -- user_id
  '[0.123, -0.456, ...]'::vector(1536),  -- query_embedding (do OpenAI)
  0.7,                           -- similarity threshold (0-1)
  10                             -- max results
);

-- Resultado:
-- chunk_id | repo_id | repo_full_name | file_path | code | similarity
-- ---------+---------+----------------+-----------+------+------------
-- chunk123 | uuid... | facebook/react | src/...   | ...  | 0.92
```

### Busca Manual (Sem Função Helper)

```sql
-- Para debugging ou queries customizadas
WITH selected_repos AS (
  SELECT repo_id
  FROM public.user_repositories
  WHERE user_id = auth.uid()
    AND is_selected = true
)
SELECT
  c.chunk_id,
  c.file_path,
  c.code,
  c.name,
  c.signature,
  r.full_name as repo_name,
  1 - (e.embedding <=> '[0.1,0.2,...]'::vector(1536)) as similarity
FROM public.embeddings e
JOIN public.code_chunks c ON e.chunk_id = c.chunk_id
JOIN public.repositories r ON c.repo_id = r.id
WHERE c.repo_id IN (SELECT repo_id FROM selected_repos)
  AND r.status = 'ready'
  AND 1 - (e.embedding <=> '[0.1,0.2,...]'::vector(1536)) > 0.7
ORDER BY e.embedding <=> '[0.1,0.2,...]'::vector(1536)
LIMIT 10;
```

### Buscar em Repo Específico

```sql
-- Busca apenas no repo "facebook/react"
SELECT
  c.chunk_id,
  c.file_path,
  c.code,
  c.name,
  1 - (e.embedding <=> $1::vector(1536)) as similarity
FROM public.embeddings e
JOIN public.code_chunks c ON e.chunk_id = c.chunk_id
JOIN public.repositories r ON c.repo_id = r.id
WHERE r.full_name = 'facebook/react'
  AND r.status = 'ready'
  AND 1 - (e.embedding <=> $1::vector(1536)) > 0.7
ORDER BY e.embedding <=> $1::vector(1536)
LIMIT 5;
```

---

## Indexação Incremental

### Inserir Metadata de Arquivo

```sql
INSERT INTO public.file_metadata (
  repo_id,
  file_path,
  file_hash,
  size_bytes,
  lines,
  language
)
VALUES (
  'repo-uuid',
  'src/components/Button.tsx',
  'abc123def456...', -- SHA256 hash
  5120,
  150,
  'TypeScript'
)
ON CONFLICT (repo_id, file_path)
DO UPDATE SET
  file_hash = EXCLUDED.file_hash,
  size_bytes = EXCLUDED.size_bytes,
  lines = EXCLUDED.lines,
  indexed_at = NOW();
```

### Detectar Arquivos Modificados

```sql
-- Comparar hashes para encontrar arquivos que mudaram
WITH new_scan AS (
  -- Dados do novo scan (vindos do Bee2Bee Metadata)
  SELECT * FROM (VALUES
    ('src/auth.js', 'abc123'),
    ('src/utils.js', 'xyz789'),  -- Hash diferente!
    ('src/config.js', 'new999')  -- Arquivo novo
  ) AS t(file_path, file_hash)
)
SELECT
  n.file_path,
  n.file_hash as new_hash,
  m.file_hash as old_hash,
  CASE
    WHEN m.file_hash IS NULL THEN 'added'
    WHEN m.file_hash != n.file_hash THEN 'modified'
    ELSE 'unchanged'
  END as status
FROM new_scan n
LEFT JOIN public.file_metadata m
  ON m.file_path = n.file_path
  AND m.repo_id = 'repo-uuid'
WHERE m.file_hash IS NULL OR m.file_hash != n.file_hash;
```

### Deletar Chunks de Arquivo Modificado

```sql
-- Antes de re-indexar, deleta chunks antigos do arquivo
DELETE FROM public.code_chunks
WHERE repo_id = 'repo-uuid'
  AND file_path = 'src/utils.js'
  AND file_hash = 'old-hash-value';

-- Embeddings são deletados automaticamente (ON DELETE CASCADE)
```

### Inserir Novos Chunks e Embeddings

```sql
-- 1. Inserir chunk
INSERT INTO public.code_chunks (
  chunk_id,
  repo_id,
  file_path,
  file_hash,
  code,
  chunk_type,
  name,
  signature,
  start_line,
  end_line
)
VALUES (
  'react_usestate_abc123',
  'repo-uuid',
  'src/hooks/useState.js',
  'abc123',
  'function useState(initialValue) { ... }',
  'function',
  'useState',
  'useState(initialValue: any): [any, Function]',
  45,
  120
);

-- 2. Inserir embedding
INSERT INTO public.embeddings (chunk_id, embedding, model_name)
VALUES (
  'react_usestate_abc123',
  '[0.123, -0.456, ...]'::vector(1536),
  'text-embedding-3-small'
);
```

---

## Chat e Interações

### Salvar Mensagem de Chat

```sql
-- Mensagem do usuário
INSERT INTO public.chat_messages (
  user_id,
  role,
  content,
  repo_ids  -- Repos que estavam selecionados
)
VALUES (
  auth.uid(),
  'user',
  'How does authentication work in this codebase?',
  ARRAY['repo-uuid-1', 'repo-uuid-2']::UUID[]
);

-- Mensagem do assistente (com sources)
INSERT INTO public.chat_messages (
  user_id,
  role,
  content,
  repo_ids,
  sources,  -- Chunks usados para RAG
  model_name,
  tokens_used
)
VALUES (
  auth.uid(),
  'assistant',
  'Authentication is handled in src/auth/index.ts...',
  ARRAY['repo-uuid-1', 'repo-uuid-2']::UUID[],
  '[
    {
      "chunk_id": "auth_login_func",
      "file_path": "src/auth/index.ts",
      "similarity": 0.92
    }
  ]'::jsonb,
  'gpt-4-turbo',
  1250
);
```

### Obter Histórico de Chat

```sql
-- Últimas 50 mensagens do usuário
SELECT
  id,
  role,
  content,
  repo_ids,
  sources,
  created_at
FROM public.chat_messages
WHERE user_id = auth.uid()
ORDER BY created_at DESC
LIMIT 50;
```

### Atualizar Interação do Repo (Manual)

```sql
-- Atualiza last_interaction_at e estende expiração
SELECT public.update_repo_interaction('repo-uuid');

-- Ou para múltiplos repos
SELECT public.update_repo_interaction(repo_id)
FROM public.user_repositories
WHERE user_id = auth.uid()
  AND is_selected = true;
```

---

## Manutenção e Limpeza

### Marcar Repos Expirados (Manual)

```sql
-- Normalmente executado via cron, mas pode rodar manualmente
SELECT public.mark_expired_repos();
-- Retorna: número de repos marcados como expirados
```

### Limpar Repos Expirados

```sql
-- Deleta repos expirados há mais de 7 dias (padrão)
SELECT * FROM public.cleanup_expired_repos();
-- Retorna: (deleted_repos, deleted_chunks, deleted_embeddings)

-- Deleta repos expirados há mais de 30 dias
SELECT * FROM public.cleanup_expired_repos(30);
```

### Verificar Saúde do Sistema

```sql
-- Status geral dos repos
SELECT
  status,
  COUNT(*) as count,
  SUM(total_chunks) as total_chunks,
  SUM(total_embeddings) as total_embeddings
FROM public.repositories
GROUP BY status;

-- Repos próximos de expirar (próximos 7 dias)
SELECT
  full_name,
  last_interaction_at,
  expires_at,
  expires_at - NOW() as time_until_expiration
FROM public.repositories
WHERE status = 'ready'
  AND expires_at < NOW() + INTERVAL '7 days'
ORDER BY expires_at ASC;
```

### Reindexar Repo Manualmente

```sql
-- 1. Marcar como pending para re-indexação
UPDATE public.repositories
SET status = 'pending', indexing_error = NULL
WHERE full_name = 'facebook/react';

-- 2. Deletar dados antigos
DELETE FROM public.file_metadata WHERE repo_id = 'repo-uuid';
-- Cascading deletes code_chunks and embeddings

-- 3. Processo de indexação via n8n vai detectar status='pending'
```

---

## Estatísticas e Analytics

### Dashboard de Uso por Usuário

```sql
-- Estatísticas do usuário
SELECT
  COUNT(DISTINCT ur.repo_id) as total_repos,
  COUNT(DISTINCT ur.repo_id) FILTER (WHERE ur.is_selected) as selected_repos,
  COUNT(DISTINCT cm.id) as total_messages,
  SUM(cm.tokens_used) as total_tokens
FROM public.user_repositories ur
LEFT JOIN public.chat_messages cm ON cm.user_id = ur.user_id
WHERE ur.user_id = auth.uid()
GROUP BY ur.user_id;
```

### Repos Mais Populares

```sql
-- Repos mais adicionados pelos usuários
SELECT
  r.full_name,
  r.stars,
  r.language,
  COUNT(DISTINCT ur.user_id) as user_count,
  r.total_chunks,
  r.status
FROM public.repositories r
JOIN public.user_repositories ur ON ur.repo_id = r.id
GROUP BY r.id
ORDER BY user_count DESC, r.stars DESC
LIMIT 20;
```

### Chunks Mais Consultados

```sql
-- Chunks que aparecem mais nos sources das mensagens
SELECT
  source->>'chunk_id' as chunk_id,
  source->>'file_path' as file_path,
  COUNT(*) as times_used,
  AVG((source->>'similarity')::float) as avg_similarity
FROM public.chat_messages,
     jsonb_array_elements(sources) as source
WHERE user_id = auth.uid()
GROUP BY source->>'chunk_id', source->>'file_path'
ORDER BY times_used DESC
LIMIT 10;
```

### Custos de Embeddings

```sql
-- Estimativa de custo (OpenAI text-embedding-3-small = $0.02 / 1M tokens)
-- Assumindo ~500 tokens por chunk
SELECT
  r.full_name,
  r.total_embeddings,
  (r.total_embeddings * 500 * 0.02 / 1000000)::decimal(10,4) as estimated_cost_usd
FROM public.repositories r
WHERE r.status = 'ready'
ORDER BY r.total_embeddings DESC
LIMIT 20;
```

---

## Exemplos de Integração Frontend

### TypeScript/JavaScript (Supabase Client)

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// 1. Adicionar repositório
async function addRepository(fullName: string) {
  const { data: repo, error: repoError } = await supabase
    .from('repositories')
    .insert({ full_name: fullName, status: 'pending' })
    .select()
    .single();

  if (repoError) throw repoError;

  const { error: userRepoError } = await supabase
    .from('user_repositories')
    .insert({
      repo_id: repo.id,
      is_selected: true
    });

  if (userRepoError) throw userRepoError;

  return repo;
}

// 2. Buscar chunks similares (RAG)
async function searchSimilarChunks(queryEmbedding: number[], threshold = 0.7, limit = 10) {
  const { data, error } = await supabase.rpc('search_similar_chunks', {
    user_uuid: (await supabase.auth.getUser()).data.user?.id,
    query_embedding: queryEmbedding,
    match_threshold: threshold,
    match_count: limit
  });

  if (error) throw error;
  return data;
}

// 3. Salvar mensagem de chat
async function saveChatMessage(
  role: 'user' | 'assistant',
  content: string,
  repoIds: string[],
  sources?: any
) {
  const { data, error } = await supabase
    .from('chat_messages')
    .insert({
      role,
      content,
      repo_ids: repoIds,
      sources: sources || null
    })
    .select()
    .single();

  if (error) throw error;
  return data;
}

// 4. Toggle checkbox de repo
async function toggleRepoSelection(repoId: string) {
  const { data, error } = await supabase
    .from('user_repositories')
    .update({ is_selected: supabase.raw('NOT is_selected') })
    .eq('repo_id', repoId)
    .select()
    .single();

  if (error) throw error;
  return data;
}

// 5. Obter repos selecionados
async function getSelectedRepos() {
  const { data, error } = await supabase.rpc('get_user_selected_repos', {
    user_uuid: (await supabase.auth.getUser()).data.user?.id
  });

  if (error) throw error;
  return data; // Array de UUIDs
}
```

---

## Troubleshooting

### Problema: Busca vetorial muito lenta

```sql
-- Verificar se índice HNSW existe
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'embeddings'
  AND indexname LIKE '%hnsw%';

-- Se não existir, criar:
CREATE INDEX idx_embeddings_hnsw ON public.embeddings
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
```

### Problema: Repos não estão expirando

```sql
-- Verificar se cron job está ativo
SELECT * FROM cron.job WHERE jobname = 'mark-expired-repos-daily';

-- Executar manualmente
SELECT public.mark_expired_repos();
```

### Problema: Embeddings inconsistentes

```sql
-- Verificar chunks sem embeddings
SELECT c.chunk_id, c.file_path
FROM public.code_chunks c
LEFT JOIN public.embeddings e ON c.chunk_id = e.chunk_id
WHERE e.id IS NULL
LIMIT 10;

-- Contar embeddings órfãos (sem chunk)
SELECT COUNT(*)
FROM public.embeddings e
LEFT JOIN public.code_chunks c ON e.chunk_id = c.chunk_id
WHERE c.chunk_id IS NULL;
```

---

## Referências

- [Supabase Vector Documentation](https://supabase.com/docs/guides/ai/vector-columns)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
