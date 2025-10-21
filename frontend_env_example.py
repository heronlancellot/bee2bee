# frontend_env_example.py - Frontend Environment Configuration Example
"""
🧙‍♂️ FRONTEND ENVIRONMENT CONFIGURATION EXAMPLE ⚔️

Configuração para integrar frontend Next.js com Supreme Unified Orchestrator
"""

FRONTEND_ENV_EXAMPLE = """# .env.local - Frontend Environment Configuration

# Supreme Unified Orchestrator Backend
SUPREME_ORCHESTRATOR_URL=http://localhost:8020

# Legacy Python Server (for backward compatibility)
PYTHON_SERVER_URL=http://localhost:5001

# Agents API URL (for other integrations)
AGENTS_API_URL=http://localhost:5001

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key_here

# AgentVerse Configuration (if using)
AGENTVERSE_API_KEY=your_agentverse_api_key_here

# OpenAI Configuration (if using)
OPENAI_API_KEY=your_openai_api_key_here
"""

print("🧙‍♂️ FRONTEND ENVIRONMENT CONFIGURATION ⚔️")
print("="*60)
print("Copy the following to frontend/.env.local:")
print(FRONTEND_ENV_EXAMPLE)
print("="*60)
print("🎯 CONFIGURATION STEPS:")
print("1. Create frontend/.env.local file")
print("2. Copy the configuration above")
print("3. Update SUPREME_ORCHESTRATOR_URL=http://localhost:8020")
print("4. Configure Supabase credentials")
print("5. Start frontend: npm run dev")
print("="*60)



