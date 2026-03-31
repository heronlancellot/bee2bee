# Supabase Setup

## Prerequisites

Install Supabase CLI:

```bash
npm install -g supabase
```

Or use `npx` directly (recommended):

```bash
npx supabase --version
```

## Local Development

### 0. Enable local mode (IMPORTANT!)

In `frontend/.env.local`, uncomment the line:
```
NEXT_PUBLIC_USE_LOCAL_SUPABASE=true
```

### 1. Start Supabase

```bash
npx supabase start
```

This starts all services locally (Postgres, Auth, Storage, etc.). First run will download Docker images.

### 2. Apply Migrations

```bash
npx supabase db reset
```

This command:
- Resets the local database (⚠️ deletes all data)
- Applies all migrations in `supabase/migrations/`
- Runs seed file if exists (`supabase/seed.sql`)

### 3. Check Status

```bash
npx supabase status
```

Shows all running services and their local URLs.

### 4. Stop Services

```bash
npx supabase stop
```

## Working with Migrations

### Create New Migration

```bash
npx supabase migration new <migration_name>
```

Example:
```bash
npx supabase migration new create_user_table
```

This creates: `supabase/migrations/<timestamp>_create_user_table.sql`

### Apply Migrations Locally

After creating or modifying migrations:

```bash
npx supabase db reset
```

⚠️ **Note:** This resets the entire database. For non-destructive updates during development, you can manually run the migration:

```bash
npx supabase db push --local
```

### Generate TypeScript Types

```bash
npx supabase gen types typescript --local > frontend/src/integrations/supabase/types.ts
```

Run this after any schema changes to update types.

## Remote Project (Production)

### 1. Login

```bash
npx supabase login
```

### 2. Link Project

```bash
npx supabase link --project-ref <your-project-id>
```

Get your project ID from: https://supabase.com/dashboard/project/_/settings/general

### 3. Push to Production

```bash
npx supabase db push
```

⚠️ **Be careful:** This applies migrations to your production database!

### 4. Pull from Production

```bash
npx supabase db pull
```

Downloads the production schema to create migrations locally.

## Common Commands

```bash
# Local development
npx supabase start              # Start local services
npx supabase stop               # Stop local services
npx supabase status             # Check running services
npx supabase db reset           # Reset database and apply migrations

# Migrations
npx supabase migration new <name>  # Create new migration
npx supabase db diff              # Show differences between local and database

# Remote/Production
npx supabase db push             # Apply migrations to remote
npx supabase db pull             # Pull schema from remote
```

## Project Structure

```
supabase/
├── config.toml          # Supabase configuration
├── migrations/          # SQL migration files (timestamped)
│   ├── 20250118000000_create_rag_system.sql
│   └── ...
└── seed.sql            # (Optional) Seed data for development
```

## Environment Variables

Create `frontend/.env.local`:

```env
# For local development
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-local-anon-key>

# For production (get from Supabase dashboard)
# NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
# NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-production-anon-key>
```

Get local keys from `npx supabase status` output.

## Tips

- **Migration files:** Must follow pattern `<timestamp>_<name>.sql`
- **Reset vs Push:** Use `reset` for local dev (destructive), `push` for incremental changes
- **Type safety:** Always regenerate types after schema changes
- **RLS:** Service role key bypasses Row Level Security - never expose it client-side