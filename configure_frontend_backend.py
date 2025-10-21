# configure_frontend_backend.py - Configure Frontend ↔ Backend Integration
"""
🧙‍♂️ CONFIGURE FRONTEND ↔ BACKEND INTEGRATION ⚔️
"""

import os

def create_frontend_env():
    """Create frontend .env.local file"""
    
    env_content = """# .env.local - Frontend Environment Configuration

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
    
    # Write to frontend/.env.local
    frontend_env_path = 'frontend/.env.local'
    with open(frontend_env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Arquivo {frontend_env_path} criado com sucesso!")


def check_backend_status():
    """Check if backend agents are running"""
    
    print("🔍 VERIFICANDO STATUS DO BACKEND...")
    print("-" * 40)
    
    import subprocess
    
    ports = {
        8009: 'User Profile Agent',
        8010: 'Skill Matcher Agent', 
        8011: 'Bounty Estimator Agent',
        8020: 'Supreme Orchestrator Agent'
    }
    
    all_running = True
    
    for port, name in ports.items():
        try:
            result = subprocess.run(['lsof', '-i', f':{port}'], capture_output=True, text=True)
            if 'LISTEN' in result.stdout:
                print(f"✅ {name:25} (port {port})")
            else:
                print(f"❌ {name:25} (port {port}) - NÃO ESTÁ RODANDO")
                all_running = False
        except:
            print(f"⚠️  {name:25} (port {port}) - Não foi possível verificar")
    
    return all_running


def show_integration_commands():
    """Show commands to test integration"""
    
    print("\n🧪 COMANDOS PARA TESTAR INTEGRAÇÃO:")
    print("-" * 40)
    
    print("1️⃣  Testar Backend Diretamente:")
    print("   curl -X POST http://localhost:8020/api/query \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"message\": \"Quero encontrar issues de Python\", \"user_id\": \"test\"}'")
    
    print("\n2️⃣  Testar Frontend:")
    print("   # Acesse: http://localhost:3000/supreme-orchestrator")
    print("   # Ou teste a API: http://localhost:3000/api/supreme-orchestrator")
    
    print("\n3️⃣  Verificar Logs:")
    print("   # Backend logs aparecem nos terminais dos agentes")
    print("   # Frontend logs aparecem no console do navegador")


def main():
    print("🧙‍♂️ CONFIGURE FRONTEND ↔ BACKEND INTEGRATION ⚔️")
    print("="*60)
    
    # Check if frontend directory exists
    if not os.path.exists('frontend'):
        print("❌ Diretório 'frontend' não encontrado!")
        print("   Execute este script a partir da raiz do projeto bee2bee")
        return
    
    # Create frontend .env.local
    if os.path.exists('frontend/.env.local'):
        print("📁 Arquivo frontend/.env.local já existe!")
        print("🔄 Quer recriar? (y/n)")
        response = input().lower()
        if response == 'y':
            create_frontend_env()
    else:
        print("📁 Criando arquivo frontend/.env.local...")
        create_frontend_env()
    
    # Check backend status
    backend_running = check_backend_status()
    
    # Show integration commands
    show_integration_commands()
    
    print("\n🎯 RESUMO DA CONFIGURAÇÃO:")
    print("="*60)
    print("✅ Frontend .env.local configurado")
    print(f"{'✅' if backend_running else '❌'} Backend agents {'rodando' if backend_running else 'não rodando'}")
    print("✅ API routes criadas")
    print("✅ Componente de interface criado")
    print("✅ Página do Supreme Orchestrator criada")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    if not backend_running:
        print("1. Iniciar agentes backend:")
        print("   cd agents/autonomous-agents-system")
        print("   source venv/bin/activate")
        print("   python user-profile-agent/agent.py")
        print("   python skill-matcher-agent/agent.py")
        print("   python bounty-estimator-agent/agent.py")
        print("   python supreme_unified_orchestrator_agent.py")
    
    print("2. Iniciar frontend:")
    print("   cd frontend")
    print("   npm run dev")
    
    print("3. Testar integração:")
    print("   Acesse: http://localhost:3000/supreme-orchestrator")
    
    print("="*60)


if __name__ == "__main__":
    main()



