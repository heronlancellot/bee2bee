#!/usr/bin/env python3
"""
Test Communication Between Orchestrator and Agents
Shows exactly what messages are being sent and received
"""

import asyncio
import json
from datetime import datetime
from orchestrator import MultiAgentOrchestrator


async def test_communication():
    """Test if orchestrator can communicate with agents"""

    print("\n" + "="*70)
    print("🧪 TESTE DE COMUNICAÇÃO - ORCHESTRATOR → AGENTS")
    print("="*70)
    print()

    # Create orchestrator
    orchestrator = MultiAgentOrchestrator()

    print("📋 Configuração:")
    print(f"   User Profile:     {orchestrator.agent_addresses.get('user_profile')}")
    print(f"   Skill Matcher:    {orchestrator.agent_addresses.get('skill_matcher')}")
    print(f"   Bounty Estimator: {orchestrator.agent_addresses.get('bounty_estimator')}")
    print(f"   API Key:          {'✅ Configurada' if orchestrator.api_key else '❌ Faltando'}")
    print()

    # Prepare test queries
    print("="*70)
    print("📤 ENVIANDO QUERIES PARA OS AGENTES...")
    print("="*70)
    print()

    queries = {
        "user_profile": {
            "user_id": "test_user_123",
            "skills": ["Python", "JavaScript"],
            "years_experience": 3,
            "action": "get_profile"
        },
        "skill_matcher": {
            "user_skills": ["Python", "JavaScript"],
            "required_skills": ["Python", "asyncio", "FastAPI"]
        },
        "bounty_estimator": {
            "complexity_score": 6,
            "required_skills": ["Python", "asyncio"],
            "estimated_hours": 4,
            "repo_stars": 450
        }
    }

    print("🔄 Query 1: User Profile Agent")
    print(f"   Payload: {json.dumps(queries['user_profile'], indent=6)}")
    print()

    print("🔄 Query 2: Skill Matcher Agent")
    print(f"   Payload: {json.dumps(queries['skill_matcher'], indent=6)}")
    print()

    print("🔄 Query 3: Bounty Estimator Agent")
    print(f"   Payload: {json.dumps(queries['bounty_estimator'], indent=6)}")
    print()

    # Send queries
    print("="*70)
    print("⏳ AGUARDANDO RESPOSTAS DOS AGENTES...")
    print("="*70)
    print()

    start_time = datetime.now()

    responses = await orchestrator.query_all_agents_parallel(queries)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Analyze responses
    print()
    print("="*70)
    print("📥 RESULTADOS")
    print("="*70)
    print()

    print(f"⏱️  Tempo total: {duration:.2f} segundos")
    print()

    success_count = 0
    failed_count = 0

    for agent_name, response in responses.items():
        print(f"\n{'─'*70}")
        print(f"🤖 {agent_name.upper().replace('_', ' ')}")
        print(f"{'─'*70}")

        if response.get("success"):
            success_count += 1
            print(f"✅ Status: SUCESSO")
            print(f"📨 Resposta recebida:")
            print()

            # Try to parse and display nicely
            resp_data = response.get("response", {})
            if isinstance(resp_data, dict):
                print(json.dumps(resp_data, indent=2))
            else:
                print(str(resp_data)[:500])  # First 500 chars
        else:
            failed_count += 1
            print(f"❌ Status: FALHOU")
            print(f"⚠️  Erro: {response.get('error', 'Unknown error')}")

    # Summary
    print()
    print("="*70)
    print("📊 RESUMO")
    print("="*70)
    print()
    print(f"✅ Sucessos: {success_count}/3")
    print(f"❌ Falhas:   {failed_count}/3")
    print()

    if success_count == 3:
        print("🎉 TUDO FUNCIONANDO PERFEITAMENTE!")
        print()
        print("✨ Os 3 agentes responderam via Agentverse!")
        print("✨ A comunicação está OK!")
        print("✨ O orchestrator está funcionando!")
        print()
        return True
    elif success_count > 0:
        print("⚠️  PARCIALMENTE FUNCIONANDO")
        print()
        print(f"   {success_count} agente(s) responderam")
        print(f"   {failed_count} agente(s) falharam")
        print()
        print("🔍 Verifique:")
        print("   • Se todos os agentes estão rodando")
        print("   • Se todos têm mailbox no Agentverse")
        print("   • Os logs dos agentes que falharam")
        print()
        return False
    else:
        print("❌ NADA FUNCIONOU!")
        print()
        print("🔍 Problemas possíveis:")
        print("   • Agentes não estão rodando")
        print("   • Agentes sem mailbox no Agentverse")
        print("   • AGENTVERSE_API_KEY incorreta")
        print("   • Endereços dos agentes errados no .env")
        print()
        print("📝 Verifique:")
        print("   1. Os 3 agentes estão rodando? (portas 8009, 8010, 8011)")
        print("   2. Aparecem 'Mailbox access token acquired' nos logs?")
        print("   3. O .env tem a API key correta?")
        print()
        return False


async def test_find_matches_flow():
    """Test complete FIND_MATCHES flow"""

    print("\n" + "="*70)
    print("🎯 TESTE DO FLUXO COMPLETO - FIND_MATCHES")
    print("="*70)
    print()

    orchestrator = MultiAgentOrchestrator()

    user_query = {
        "user_id": "test_user",
        "skills": ["Python", "JavaScript", "React"],
        "years_experience": 3,
        "issue_query": "show me Python issues I can solve"
    }

    print("📋 Query do usuário:")
    print(f"   Skills: {', '.join(user_query['skills'])}")
    print(f"   Experience: {user_query['years_experience']} anos")
    print()

    print("⏳ Processando...")
    print()

    result = await orchestrator.find_perfect_matches(user_query)

    print("="*70)
    print("📋 RESPOSTA SINTETIZADA:")
    print("="*70)
    print()
    print(result)
    print()


async def main():
    """Run all tests"""

    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "TESTE DE COMUNICAÇÃO DOS AGENTES" + " "*21 + "║")
    print("╚" + "="*68 + "╝")

    # Test 1: Basic communication
    success = await test_communication()

    if success:
        # Test 2: Complete flow
        await test_find_matches_flow()

    print()
    print("="*70)
    print("🏁 TESTE FINALIZADO")
    print("="*70)
    print()


if __name__ == "__main__":
    print("\n⚠️  IMPORTANTE: Certifique-se de que os 3 agentes estão rodando!")
    print("   • User Profile Agent (porta 8009)")
    print("   • Skill Matcher Agent (porta 8010)")
    print("   • Bounty Estimator Agent (porta 8011)")
    print()
    input("Pressione ENTER para continuar...")

    asyncio.run(main())
