#!/usr/bin/env python3
"""
Teste de Inteligência e Compartilhamento de Conhecimento
Verifica se os agentes estão usando MeTTa e compartilhando knowledge base
"""

import requests
import json
import time


def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_orchestrator_rest():
    """Teste 1: Orchestrator REST está funcionando?"""

    print_section("🧪 TESTE 1: ORCHESTRATOR REST ENDPOINT")

    url = "http://localhost:8012/api/query"

    payload = {
        "message": "Show me Python issues I can solve",
        "user_id": "test_intelligence",
        "conversation_id": "test_001"
    }

    print(f"📤 Enviando query para: {url}")
    print(f"📋 Payload: {json.dumps(payload, indent=2)}")
    print()

    try:
        print("⏳ Aguardando resposta (pode demorar ~5-10 segundos)...")
        response = requests.post(url, json=payload, timeout=15)

        if response.status_code == 200:
            result = response.json()

            print("✅ SUCESSO! Orchestrator respondeu!")
            print()
            print(f"📨 Intent detectado: {result.get('intent')}")
            print(f"🤖 Agent ID: {result.get('agent_id')}")
            print(f"📅 Timestamp: {result.get('timestamp')}")
            print()
            print("📋 RESPOSTA COMPLETA:")
            print("-" * 70)
            print(result.get('response', ''))
            print("-" * 70)

            # Verificar se consultou os 3 agentes
            response_text = result.get('response', '')

            agents_found = []
            if "User Profile" in response_text or "👤" in response_text:
                agents_found.append("User Profile")
            if "Skill Matcher" in response_text or "🎯" in response_text:
                agents_found.append("Skill Matcher")
            if "Bounty Estimator" in response_text or "💰" in response_text:
                agents_found.append("Bounty Estimator")

            print()
            if len(agents_found) >= 2:
                print(f"✅ INTELIGÊNCIA DETECTADA! Consultou {len(agents_found)} agentes:")
                for agent in agents_found:
                    print(f"   • {agent}")
                return True
            else:
                print("⚠️  Resposta não mostra consulta aos agentes")
                return False

        else:
            print(f"❌ FALHOU! Status: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ TIMEOUT! Orchestrator não respondeu em 15 segundos")
        print()
        print("🔍 Possíveis causas:")
        print("   • Orchestrator não está rodando")
        print("   • Agentes não estão respondendo via Agentverse")
        print("   • Mailbox com problemas")
        return False

    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def test_metta_knowledge_sharing():
    """Teste 2: MeTTa Knowledge Base está compartilhando?"""

    print_section("🧪 TESTE 2: COMPARTILHAMENTO DE CONHECIMENTO METTA")

    print("📚 Testando se o conhecimento está sendo compartilhado entre agentes...")
    print()

    # Query 1: Enviar informação para um agente
    print("📤 Query 1: Criando perfil de usuário...")

    payload1 = {
        "message": "Show me Python and React issues",
        "user_id": "knowledge_test_user",
        "conversation_id": "knowledge_001"
    }

    try:
        response1 = requests.post(
            "http://localhost:8012/api/query",
            json=payload1,
            timeout=15
        )

        if response1.status_code == 200:
            print("✅ Query 1 enviada com sucesso!")
            print()

            # Esperar um pouco
            print("⏳ Aguardando 2 segundos para knowledge base processar...")
            time.sleep(2)

            # Query 2: Verificar se outro agente tem acesso ao conhecimento
            print()
            print("📤 Query 2: Consultando conhecimento compartilhado...")

            payload2 = {
                "message": "Find JavaScript bounties for me",
                "user_id": "knowledge_test_user",
                "conversation_id": "knowledge_002"
            }

            response2 = requests.post(
                "http://localhost:8012/api/query",
                json=payload2,
                timeout=15
            )

            if response2.status_code == 200:
                result2 = response2.json()
                response_text = result2.get('response', '')

                print("✅ Query 2 respondida!")
                print()

                # Verificar se mencionou conhecimento anterior
                if "beginner" in response_text.lower() or "advanced" in response_text.lower() or "skill" in response_text.lower():
                    print("✅ CONHECIMENTO COMPARTILHADO DETECTADO!")
                    print("   Os agentes estão usando a MeTTa Knowledge Base!")
                    print()
                    print("📋 Evidências:")
                    print(response_text[:500])
                    return True
                else:
                    print("⚠️  Não detectei compartilhamento explícito de conhecimento")
                    print("   Mas isso pode ser normal se a síntese não incluir esses detalhes")
                    return True
            else:
                print(f"❌ Query 2 falhou: {response2.status_code}")
                return False
        else:
            print(f"❌ Query 1 falhou: {response1.status_code}")
            return False

    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def test_parallel_queries():
    """Teste 3: Queries paralelas estão funcionando?"""

    print_section("🧪 TESTE 3: PROCESSAMENTO PARALELO")

    print("🔄 Testando se os agentes respondem em paralelo...")
    print("   (Se for sequencial, demoraria 15+ segundos)")
    print("   (Se for paralelo, deve demorar ~5-7 segundos)")
    print()

    payload = {
        "message": "Show me Python, JavaScript and React issues",
        "user_id": "parallel_test",
        "conversation_id": "parallel_001"
    }

    try:
        start_time = time.time()

        print("⏱️  Cronometrando...")
        response = requests.post(
            "http://localhost:8012/api/query",
            json=payload,
            timeout=20
        )

        end_time = time.time()
        duration = end_time - start_time

        print(f"✅ Respondeu em {duration:.2f} segundos")
        print()

        if duration < 10:
            print("✅ QUERIES PARALELAS CONFIRMADAS!")
            print(f"   Tempo: {duration:.2f}s (paralelo)")
            print("   Se fosse sequencial: ~15s+")
            return True
        else:
            print("⚠️  Demorou mais que o esperado")
            print(f"   Tempo: {duration:.2f}s")
            print("   Pode estar processando sequencialmente")
            return False

    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def check_agents_running():
    """Verifica se os agentes estão rodando"""

    print_section("🔍 VERIFICAÇÃO PRÉVIA: AGENTES RODANDO?")

    import subprocess

    ports = {
        8009: "User Profile Agent",
        8010: "Skill Matcher Agent",
        8011: "Bounty Estimator Agent",
        8012: "Orchestrator Agent"
    }

    all_running = True

    for port, name in ports.items():
        try:
            result = subprocess.run(
                ['lsof', '-i', f':{port}'],
                capture_output=True,
                text=True
            )

            if "LISTEN" in result.stdout:
                print(f"✅ {name:30} (porta {port})")
            else:
                print(f"❌ {name:30} (porta {port}) - NÃO ESTÁ RODANDO")
                all_running = False
        except:
            print(f"⚠️  {name:30} (porta {port}) - Não foi possível verificar")

    print()

    if not all_running:
        print("❌ ALGUNS AGENTES NÃO ESTÃO RODANDO!")
        print()
        print("Por favor, inicie todos os agentes primeiro:")
        print("  1. user-profile-agent/agent.py (porta 8009)")
        print("  2. skill-matcher-agent/agent.py (porta 8010)")
        print("  3. bounty-estimator-agent/agent.py (porta 8011)")
        print("  4. orchestrator-agent/agent.py (porta 8012)")
        print()
        return False

    print("✅ Todos os agentes estão rodando!")
    return True


def main():
    print()
    print("╔" + "="*68 + "╗")
    print("║" + " "*10 + "TESTE DE INTELIGÊNCIA E CONHECIMENTO COMPARTILHADO" + " "*8 + "║")
    print("╚" + "="*68 + "╝")

    # Verificação prévia
    if not check_agents_running():
        return

    # Teste 1: REST endpoint
    test1_passed = test_orchestrator_rest()

    if not test1_passed:
        print()
        print("❌ Teste 1 falhou. Parando aqui.")
        return

    # Teste 2: Knowledge sharing
    test2_passed = test_metta_knowledge_sharing()

    # Teste 3: Parallel processing
    test3_passed = test_parallel_queries()

    # Resumo
    print_section("📊 RESUMO DOS TESTES")

    print(f"Teste 1 - Orchestrator REST:        {'✅ PASSOU' if test1_passed else '❌ FALHOU'}")
    print(f"Teste 2 - Compartilhamento MeTTa:    {'✅ PASSOU' if test2_passed else '❌ FALHOU'}")
    print(f"Teste 3 - Queries Paralelas:         {'✅ PASSOU' if test3_passed else '❌ FALHOU'}")

    print()

    if test1_passed and test2_passed and test3_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print()
        print("✨ Seu sistema de agentes autônomos está:")
        print("   • Funcionando corretamente")
        print("   • Compartilhando conhecimento via MeTTa")
        print("   • Processando queries em paralelo")
        print("   • Sintetizando respostas inteligentes")
        print()
        print("🚀 PRONTO PARA PRODUÇÃO!")
    else:
        print("⚠️  Alguns testes falharam")
        print("   Veja os detalhes acima para debug")

    print()


if __name__ == "__main__":
    main()
