"""
Example Queries for Testing the Consensus Layer

This file contains example queries and expected behaviors
for testing the new multi-agent consensus system.
"""

from orchestrator import process_user_query
import json


def print_result(title: str, result: dict):
    """Pretty print a result"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")
    print(f"Intent: {result.get('intent', 'unknown')}")
    print(f"Intent Confidence: {result.get('intent_confidence', 0):.2f}")
    print(f"Agent: {result.get('agent_id', 'unknown')}")
    print(f"\nResponse:\n{result.get('response', 'No response')}")

    if 'agents_consulted' in result.get('metadata', {}):
        print(f"\nAgents Consulted: {result['metadata']['agents_consulted']}")

    print(f"\n{'='*60}\n")


def example_1_find_matches():
    """
    Example 1: FIND_MATCHES intent
    Should query multiple agents in parallel and synthesize results
    """

    query = "show me Python issues I can solve"

    context = {
        "user_skills": ["Python", "JavaScript", "React", "Django"],
        "preferences": {
            "min_bounty": 50,
            "max_bounty": 200,
            "max_hours_per_week": 20,
            "preferred_languages": ["Python", "JavaScript"]
        }
    }

    result = process_user_query(
        query=query,
        user_id="user123",
        context=context
    )

    print_result("Example 1: Find Matches (Consensus Layer)", result)


def example_2_explain_reasoning():
    """
    Example 2: EXPLAIN_REASONING intent
    Should explain why a match was made with detailed reasoning
    """

    query = "why is issue #23 perfect for me?"

    context = {
        "issue_id": "23",
        "repo": "python-async-tools",
        "user_skills": ["Python", "asyncio", "debugging"],
        "user_history": {
            "completed_bounties": 5,
            "avg_complexity": 5.5,
            "similar_issues_solved": 3
        }
    }

    result = process_user_query(
        query=query,
        user_id="user123",
        context=context
    )

    print_result("Example 2: Explain Reasoning", result)


def example_3_comprehensive_analysis():
    """
    Example 3: COMPREHENSIVE_ANALYSIS intent
    Should query ALL agents and provide holistic analysis
    """

    query = "give me a comprehensive analysis"

    context = {
        "repo_url": "https://github.com/example/repo",
        "user_skills": ["Python", "JavaScript", "Docker"],
        "target": "full_profile_and_opportunities"
    }

    result = process_user_query(
        query=query,
        user_id="user123",
        context=context
    )

    print_result("Example 3: Comprehensive Analysis", result)


def example_4_single_agent():
    """
    Example 4: Single agent query (traditional routing)
    Should route to a single agent without consensus layer
    """

    query = "analyze this repository: https://github.com/example/repo"

    context = {
        "repo_url": "https://github.com/example/repo"
    }

    result = process_user_query(
        query=query,
        user_id="user123",
        context=context
    )

    print_result("Example 4: Single Agent (Repo Analysis)", result)


def example_5_skill_matching():
    """
    Example 5: Single agent skill matching
    """

    query = "match my skills with Python and React requirements"

    context = {
        "required_skills": ["Python", "React", "TypeScript"],
        "user_skills": ["Python", "JavaScript", "React"]
    }

    result = process_user_query(
        query=query,
        user_id="user123",
        context=context
    )

    print_result("Example 5: Skill Matching", result)


def example_6_bounty_estimation():
    """
    Example 6: Bounty estimation
    """

    query = "estimate the bounty for a Python API integration project"

    context = {
        "project_details": {
            "technologies": ["Python", "FastAPI", "PostgreSQL"],
            "complexity": "moderate",
            "timeline": {"weeks": 2}
        }
    }

    result = process_user_query(
        query=query,
        user_id="user123",
        context=context
    )

    print_result("Example 6: Bounty Estimation", result)


def example_7_complex_query():
    """
    Example 7: Complex query combining multiple aspects
    """

    query = "find me the best Python bounties under $100 that I can do in less than 10 hours"

    context = {
        "user_skills": ["Python", "Django", "PostgreSQL", "REST APIs"],
        "preferences": {
            "min_bounty": 50,
            "max_bounty": 100,
            "max_hours": 10,
            "preferred_languages": ["Python"]
        },
        "user_history": {
            "completed_bounties": 8,
            "avg_complexity": 6,
            "total_earned": 3500
        }
    }

    result = process_user_query(
        query=query,
        user_id="user123",
        context=context
    )

    print_result("Example 7: Complex Query (Consensus Layer)", result)


def run_all_examples():
    """Run all examples"""

    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        CONSENSUS LAYER EXAMPLES                              ║
║        Testing Multi-Agent Intelligent System                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    try:
        example_1_find_matches()
        example_2_explain_reasoning()
        example_3_comprehensive_analysis()
        example_4_single_agent()
        example_5_skill_matching()
        example_6_bounty_estimation()
        example_7_complex_query()

        print("\n✅ All examples completed!")
        print("\n💡 TIP: Set OPENAI_API_KEY environment variable for intelligent synthesis!")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run all examples
    run_all_examples()

    # Or run individual examples:
    # example_1_find_matches()
    # example_2_explain_reasoning()
    # example_7_complex_query()
