# Supabase Setup

## First Time Setup

1. Login to Supabase CLI:
   ```bash
   npx supabase login
   ```

   Useful flags:
   - `--token <access-token>` - Direct login with token

2. Link remote project:
   ```bash
   pnpm supabase:link
   ```

3. Pull existing migrations from remote:
   ```bash
   pnpm supabase:pull
   ```

   This syncs the remote schema to your local migrations folder.

   Useful flags:
   - `--schema <schema>` - Pull specific schema only (default: all)

4. Apply local migrations to remote:
   ```bash
   pnpm supabase:push
   ```

   Useful flags:
   - `--include-all` - Include all migrations (bypasses version checks)
   - `--schema <schema>` - Push specific schema only (default: public)

5. Generate types:
   ```bash
   pnpm supabase:gen-types
   ```

   This generates TypeScript types from your database schema into `frontend/src/integrations/supabase/types.ts`.

   Useful flags:
   - `--schema <schema>` - Generate types for specific schema (e.g., `public`, `auth`, `storage`)
   - `--local` - Generate from local database instead of remote

## Project Structure

```
supabase/
├── config.toml          # Supabase project configuration
├── migrations/          # Database migrations (timestamped SQL files)
└── seed.sql             # Seed data for local development

frontend/src/integrations/supabase/
├── client.ts           # Supabase client (local/remote toggle)
├── types.ts            # Auto-generated TypeScript types
├── hooks/              # React hooks for auth
└── index.ts            # Barrel exports
```

### Client Configuration

The Supabase client (`frontend/src/integrations/supabase/client.ts`) supports both local and remote environments:

- **Remote** (default): Uses environment variables from `.env.local`
- **Local**: Add `NEXT_PUBLIC_USE_LOCAL_SUPABASE=true` to `.env.local`

The ANON key is public by design and safe to commit. Never commit:
- `.env` or `.env.local` (contains secrets)
- `service_role` key (bypasses Row Level Security)

## Local Development (Optional)

1. Start local Supabase:
   ```bash
   pnpm supabase:start
   ```

2. Enable local mode in `.env.local`:
   ```env
   NEXT_PUBLIC_USE_LOCAL_SUPABASE=true
   ```

3. Restart your dev server

**Useful commands:**
```bash
pnpm supabase:stop   # Stop local Supabase
pnpm supabase:status # Check running services
```

## Migrations

### Create New Migration

```bash
pnpm supabase:migration migration_name
```

This creates a new timestamped SQL file in `supabase/migrations/`.

### Migration Workflow

1. Create migration: `pnpm supabase:migration add_new_table`
2. Edit the generated SQL file in `supabase/migrations/`
3. Apply to remote: `pnpm supabase:push`
4. Regenerate types: `pnpm supabase:gen-types`

### Useful Migration Commands

```bash
pnpm supabase:diff      # Show diff between local and remote
pnpm supabase:reset     # Reset local database (destructive!)
```

## Environment Variables

Copy `frontend/.env.example` to `frontend/.env.local` and fill in the variables:

```env
NEXT_PUBLIC_SUPABASE_URL=your-project-url.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Set to 'true' to use local Supabase instance (default: false)
# NEXT_PUBLIC_USE_LOCAL_SUPABASE=true
```
