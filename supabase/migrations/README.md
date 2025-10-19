# Supabase Migrations - RepoMind

## Como Aplicar Migrations

### Desenvolvimento Local

```bash
# 1. Certifique-se de que Supabase CLI está instalado
supabase --version

# 2. Link com seu projeto (primeira vez)
supabase link --project-ref your-project-ref

# 3. Aplicar todas migrations
supabase db push

# Ou aplicar migration específica
supabase migration up --db-url your-database-url
```

### Produção (Supabase Dashboard)

1. Acesse: https://supabase.com/dashboard/project/YOUR_PROJECT/database/migrations
2. Clique em "Create Migration"
3. Cole o conteúdo do arquivo `20250118000000_create_rag_system.sql`
4. Clique em "Run Migration"

---

## Migrations Disponíveis

### 20251012185955_create_profiles.sql
**Descrição:** Cria tabela de perfis de usuários com integração GitHub OAuth
**Tabelas:** `profiles`
**Funções:** `handle_new_user()`, `handle_updated_at()`
**Status:** ✅ Aplicada

### 20251012195726_support_email_auth.sql
**Descrição:** Adiciona suporte para autenticação via email/senha
**Modificações:** Torna campos GitHub opcionais na tabela `profiles`
**Status:** ✅ Aplicada

### 20250118000000_create_rag_system.sql
**Descrição:** Sistema completo de RAG para indexação de repositórios
**Tabelas:** 6 (repositories, user_repositories, file_metadata, code_chunks, embeddings, chat_messages)
**Funções:** 5 (search_similar_chunks, update_repo_interaction, mark_expired_repos, etc.)
**Triggers:** 3 (auto-update timestamps, interaction tracking, expiration calculation)
**Índices:** HNSW (pgvector), B-tree, GIN
**Cron Jobs:** 1 (mark expired repos daily)
**Status:** 🆕 Nova - pronta para aplicar

---

## Migration: create_rag_system.sql

### ✨ Características

- ✅ **Expiração Global:** Repos expiram após 30 dias sem interação de QUALQUER usuário
- ✅ **Sidebar Checkboxes:** Estilo NotebookLM - selecionar quais repos entram no contexto
- ✅ **pgvector 0.7.0:** Índices HNSW para busca vetorial ultra-rápida
- ✅ **Indexação Incremental:** Hash-based change detection (SHA256)
- ✅ **RLS Completo:** Row Level Security em todas as tabelas
- ✅ **Cron Automático:** Marca repos expirados diariamente às 3 AM UTC

### 📊 Estrutura de Dados

```
┌─────────────────────────────────────────────────────────────┐
│                      REPOSITORIES                           │
│  (Catálogo global de repos indexados)                      │
│  • full_name, github_id, description                       │
│  • status (pending, indexing, ready, expired, failed)      │
│  • last_interaction_at, expires_at                         │
└───────────────┬─────────────────────────────────────────────┘
                │ N:N
                v
┌─────────────────────────────────────────────────────────────┐
│                   USER_REPOSITORIES                         │
│  (Quais repos cada user adicionou)                         │
│  • user_id, repo_id                                        │
│  • is_selected (checkbox do sidebar)                       │
└───────────────┬─────────────────────────────────────────────┘
                │ 1:N
                v
┌─────────────────────────────────────────────────────────────┐
│                    FILE_METADATA                            │
│  (Metadata de arquivos - 1 linha por arquivo)              │
│  • file_path, file_hash (SHA256)                           │
│  • size, lines, language                                   │
└───────────────┬─────────────────────────────────────────────┘
                │ 1:N
                v
┌─────────────────────────────────────────────────────────────┐
│                     CODE_CHUNKS                             │
│  (Chunks de código - N linhas por arquivo)                 │
│  • code, chunk_type (function, class, file)                │
│  • name, signature, docstring                              │
└───────────────┬─────────────────────────────────────────────┘
                │ 1:1
                v
┌─────────────────────────────────────────────────────────────┐
│                      EMBEDDINGS                             │
│  (Vetores para busca semântica)                            │
│  • embedding VECTOR(1536)                                  │
│  • model_name (text-embedding-3-small)                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    CHAT_MESSAGES                            │
│  (Histórico de conversas)                                  │
│  • user_id, role, content                                  │
│  • repo_ids (quais repos estavam selecionados)             │
│  • sources (chunks usados para RAG)                        │
└─────────────────────────────────────────────────────────────┘
```

### 🔧 Funções Principais

#### `search_similar_chunks(user_uuid, query_embedding, threshold, limit)`
**Uso:** Busca semântica RAG
**Retorna:** Chunks similares filtrados pelos repos selecionados pelo usuário
**Exemplo:**
```sql
SELECT * FROM public.search_similar_chunks(
  auth.uid(),
  '[0.1,0.2,...]'::vector(1536),
  0.7,
  10
);
```

#### `update_repo_interaction(repo_uuid)`
**Uso:** Atualiza last_interaction_at e estende expiração
**Chamado:** Automaticamente em chat messages, ou manualmente
**Exemplo:**
```sql
SELECT public.update_repo_interaction('repo-uuid');
```

#### `mark_expired_repos()`
**Uso:** Marca repos como expirados (30 dias sem interação)
**Chamado:** Cron diário às 3 AM UTC
**Retorna:** Número de repos marcados
**Exemplo:**
```sql
SELECT public.mark_expired_repos();
-- Retorna: 5 (repos marcados como expirados)
```

#### `cleanup_expired_repos(days_expired)`
**Uso:** Deleta repos expirados há X dias (padrão: 7)
**⚠️ DESTRUTIVO:** Usa com cuidado!
**Retorna:** (deleted_repos, deleted_chunks, deleted_embeddings)
**Exemplo:**
```sql
SELECT * FROM public.cleanup_expired_repos(30);
-- Retorna: (3, 1250, 1250) - deletou 3 repos
```

#### `get_user_selected_repos(user_uuid)`
**Uso:** Retorna array de repo IDs selecionados (checkboxes ON)
**Retorna:** UUID[]
**Exemplo:**
```sql
SELECT public.get_user_selected_repos(auth.uid());
-- Retorna: {uuid1, uuid2, uuid3}
```

### ⏰ Cron Jobs

```sql
-- Executado diariamente às 3 AM UTC
mark-expired-repos-daily
├─ Função: public.mark_expired_repos()
├─ Frequência: 0 3 * * * (cron expression)
└─ Ação: Marca repos com status='expired' se expires_at < NOW()
```

### 🔒 Row Level Security (RLS)

| Tabela | Política | Descrição |
|--------|----------|-----------|
| **repositories** | SELECT público | Qualquer user vê repos ready |
| | ALL service_role | Apenas service role modifica |
| **user_repositories** | CRUD próprio | User vê/modifica apenas seus repos |
| **file_metadata** | SELECT público | Leitura pública |
| | ALL service_role | Escrita apenas service role |
| **code_chunks** | SELECT público | Leitura pública |
| | ALL service_role | Escrita apenas service role |
| **embeddings** | SELECT público | Leitura pública (busca RAG) |
| | ALL service_role | Escrita apenas service role |
| **chat_messages** | CRUD próprio | User vê apenas suas mensagens |

### 📈 Índices

```sql
-- Busca vetorial (HNSW - mais rápido que IVF)
idx_embeddings_hnsw (embedding) USING hnsw

-- Queries de repos
idx_repositories_status (status)
idx_repositories_full_name (full_name)
idx_repositories_expires_at (expires_at) WHERE status='ready'

-- Queries de usuário
idx_user_repos_selected (user_id, is_selected) WHERE is_selected=true

-- Indexação incremental
idx_file_metadata_file_hash (file_hash)
idx_chunks_file_hash (file_hash)

-- Chat e JSONB
idx_chat_messages_sources (sources) USING GIN
idx_repositories_topics (topics) USING GIN
```

---

## Workflow de Uso

### 1️⃣ Usuário Adiciona Repositório

```sql
-- Frontend chama:
INSERT INTO repositories (full_name) VALUES ('facebook/react');
INSERT INTO user_repositories (repo_id, is_selected) VALUES (..., true);

-- Status inicial: 'pending'
-- Backend (n8n) detecta e indexa via Bee2Bee nodes
```

### 2️⃣ Indexação (Backend n8n)

```
Bee2Bee Metadata → file_metadata (com hashes)
Bee2Bee Indexer  → code_chunks + embeddings
Update status    → 'ready'
Set expires_at   → NOW() + 30 dias
```

### 3️⃣ Usuário Faz Pergunta no Chat

```typescript
// Frontend:
1. Gera embedding da pergunta (OpenAI)
2. Chama search_similar_chunks(user_id, embedding)
   - Filtra apenas repos com is_selected=true
   - Retorna top-K chunks
3. Envia chunks + pergunta para LLM
4. Salva resposta em chat_messages
   - Trigger atualiza last_interaction_at automaticamente!
```

### 4️⃣ Sistema Marca Repos Expirados

```
Cron (3 AM UTC) → mark_expired_repos()
  └─ UPDATE repositories SET status='expired'
     WHERE expires_at < NOW()

User interage → update_repo_interaction()
  └─ Repo volta para status='ready' automaticamente
```

### 5️⃣ Limpeza de Repos Antigos (Manual)

```sql
-- Admin executa mensalmente:
SELECT * FROM cleanup_expired_repos(30);
-- Deleta repos expirados há mais de 30 dias
```

---

## Verificação Pós-Migration

```sql
-- 1. Verificar extensões
SELECT extname, extversion
FROM pg_extension
WHERE extname IN ('vector', 'pg_cron');

-- Esperado:
-- vector  | 0.7.0
-- pg_cron | 1.x

-- 2. Verificar tabelas
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'repositories',
    'user_repositories',
    'file_metadata',
    'code_chunks',
    'embeddings',
    'chat_messages'
  );

-- Esperado: 6 tabelas

-- 3. Verificar funções
SELECT routine_name
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name LIKE '%repo%';

-- Esperado: 5 funções

-- 4. Verificar índice HNSW
SELECT indexname
FROM pg_indexes
WHERE tablename = 'embeddings'
  AND indexname LIKE '%hnsw%';

-- Esperado: idx_embeddings_hnsw

-- 5. Verificar cron job
SELECT jobname, schedule
FROM cron.job
WHERE jobname = 'mark-expired-repos-daily';

-- Esperado: schedule = '0 3 * * *'
```

---

## Próximos Passos

1. ✅ Aplicar migration no Supabase
2. ✅ Verificar instalação (queries acima)
3. 🔄 Conectar n8n com banco (workflow de indexação)
4. 🔄 Implementar frontend (repo selection UI)
5. 🔄 Testar busca RAG com OpenAI embeddings
6. 🔄 Configurar monitoramento de expiração

---

## Documentação Adicional

- **Queries SQL:** Ver `/docs/RAG_SYSTEM_QUERIES.md`
- **Conceitos de Indexação:** Ver `/bee2bee-indexer-repo/docs/06-INCREMENTAL-INDEXING.md`
- **API Reference:** (TODO)

---

## Troubleshooting

### Erro: "extension vector does not exist"

```sql
-- Habilitar extensão manualmente:
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;
```

### Erro: "pg_cron not available"

- pg_cron só está disponível em projetos Supabase com Postgres 15+
- Alternativa: Desabilitar cron e executar `mark_expired_repos()` manualmente via API

### Performance lenta em busca vetorial

```sql
-- Recriar índice HNSW com parâmetros diferentes:
DROP INDEX idx_embeddings_hnsw;
CREATE INDEX idx_embeddings_hnsw ON public.embeddings
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 32, ef_construction = 128);  -- Melhor recall, mais lento build
```

---

## Contato

Para dúvidas sobre a migration, consulte:
- Documentação Supabase: https://supabase.com/docs
- pgvector GitHub: https://github.com/pgvector/pgvector
