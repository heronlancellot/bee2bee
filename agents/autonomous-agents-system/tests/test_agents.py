#!/usr/bin/env python3
"""
Test script to verify all autonomous agents are working
"""

import asyncio
import json
from orchestrator import MultiAgentOrchestrator


async def test_individual_agents():
    """Test each agent individually"""
    print("\n" + "="*60)
    print("🧪 TESTING INDIVIDUAL AGENTS")
    print("="*60 + "\n")

    orchestrator = MultiAgentOrchestrator()

    # Test 1: User Profile Agent
    print("1️⃣ Testing User Profile Agent...")
    print("-" * 40)
    user_profile_query = {
        "user_id": "test_user_123",
        "skills": ["Python", "JavaScript", "React"],
        "years_experience": 3,
        "action": "get_profile"
    }

    result = await orchestrator.query_agent("user_profile", user_profile_query)
    if result.get("success"):
        print("✅ User Profile Agent: WORKING")
        print(f"Response preview: {str(result.get('response', {}))[:200]}...")
    else:
        print(f"❌ User Profile Agent: FAILED - {result.get('error')}")

    print("\n")

    # Test 2: Skill Matcher Agent
    print("2️⃣ Testing Skill Matcher Agent...")
    print("-" * 40)
    skill_match_query = {
        "user_skills": ["Python", "JavaScript"],
        "required_skills": ["Python", "asyncio", "FastAPI"]
    }

    result = await orchestrator.query_agent("skill_matcher", skill_match_query)
    if result.get("success"):
        print("✅ Skill Matcher Agent: WORKING")
        print(f"Response preview: {str(result.get('response', {}))[:200]}...")
    else:
        print(f"❌ Skill Matcher Agent: FAILED - {result.get('error')}")

    print("\n")

    # Test 3: Bounty Estimator Agent
    print("3️⃣ Testing Bounty Estimator Agent...")
    print("-" * 40)
    bounty_query = {
        "complexity_score": 6,
        "required_skills": ["Python", "asyncio"],
        "estimated_hours": 4,
        "repo_stars": 450
    }

    result = await orchestrator.query_agent("bounty_estimator", bounty_query)
    if result.get("success"):
        print("✅ Bounty Estimator Agent: WORKING")
        print(f"Response preview: {str(result.get('response', {}))[:200]}...")
    else:
        print(f"❌ Bounty Estimator Agent: FAILED - {result.get('error')}")

    print("\n")


async def test_parallel_queries():
    """Test parallel agent queries (the main feature!)"""
    print("\n" + "="*60)
    print("🚀 TESTING PARALLEL QUERIES")
    print("="*60 + "\n")

    orchestrator = MultiAgentOrchestrator()

    queries = {
        "user_profile": {
            "user_id": "user123",
            "skills": ["Python", "JavaScript"],
            "years_experience": 3,
            "action": "get_profile"
        },
        "skill_matcher": {
            "user_skills": ["Python", "JavaScript"],
            "required_skills": ["Python", "asyncio", "debugging"]
        },
        "bounty_estimator": {
            "complexity_score": 6,
            "required_skills": ["Python", "asyncio"],
            "estimated_hours": 4,
            "repo_stars": 450
        }
    }

    print("Querying all 3 agents IN PARALLEL...")
    print("-" * 40)

    responses = await orchestrator.query_all_agents_parallel(queries)

    print(f"\n✅ Received {len(responses)} responses\n")

    for agent_name, response in responses.items():
        if response.get("success"):
            print(f"  ✅ {agent_name}: SUCCESS")
        else:
            print(f"  ❌ {agent_name}: FAILED - {response.get('error')}")

    print("\n")


async def test_find_matches_flow():
    """Test complete FIND_MATCHES flow"""
    print("\n" + "="*60)
    print("🎯 TESTING FIND_MATCHES FLOW (Complete Synthesis)")
    print("="*60 + "\n")

    orchestrator = MultiAgentOrchestrator()

    user_query = {
        "user_id": "user123",
        "skills": ["Python", "JavaScript", "React"],
        "years_experience": 3,
        "issue_query": "show me Python issues I can solve"
    }

    print("User Query:", json.dumps(user_query, indent=2))
    print("\n" + "-" * 60 + "\n")

    result = await orchestrator.find_perfect_matches(user_query)

    print("\n📋 SYNTHESIZED RESPONSE:")
    print("=" * 60)
    print(result)
    print("=" * 60)


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "AUTONOMOUS AGENTS - SYSTEM TEST" + " "*16 + "║")
    print("╚" + "="*58 + "╝")

    try:
        # Test 1: Individual agents
        await test_individual_agents()

        # Test 2: Parallel queries
        await test_parallel_queries()

        # Test 3: Complete flow
        await test_find_matches_flow()

        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
