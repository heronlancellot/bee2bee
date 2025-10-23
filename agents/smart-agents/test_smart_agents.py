#!/usr/bin/env python3
"""
Test script for Smart Agents
Run this to test the smart agents functionality
"""

import sys
import os

# Add the current directory to Python path for relative imports
sys.path.append(os.path.dirname(__file__))

from orchestrator import process_user_query


def test_intent_classification():
    """Test intent classification"""
    print("🧪 Testing Intent Classification...")
    
    test_queries = [
        "Analyze this repository: https://github.com/heronlancellot/bee2bee",
        "I need someone who knows Python and React",
        "How much should I pay for this bug fix?",
        "Update my profile with new skills",
        "Hello, how are you?"
    ]
    
    for query in test_queries:
        result = process_user_query(query, user_id="test_user")
        print(f"Query: {query}")
        print(f"Intent: {result['intent']} (confidence: {result['intent_confidence']:.2f})")
        print(f"Agent: {result['agent_id']}")
        print("-" * 50)


def test_repo_analysis():
    """Test repository analysis"""
    print("\n🔍 Testing Repository Analysis...")
    
    query = "Analyze this repository: https://github.com/heronlancellot/bee2bee"
    result = process_user_query(query, user_id="test_user")
    
    print(f"Response: {result['response'][:200]}...")
    print(f"Metadata: {result['metadata']}")


def test_skill_matching():
    """Test skill matching"""
    print("\n🎯 Testing Skill Matching...")
    
    query = "I need a developer who knows Python, React, and Docker"
    result = process_user_query(query, user_id="test_user")
    
    print(f"Response: {result['response'][:200]}...")
    print(f"Metadata: {result['metadata']}")


def test_bounty_estimation():
    """Test bounty estimation"""
    print("\n💰 Testing Bounty Estimation...")
    
    query = "How much should I pay for a React component that takes 2 days to build?"
    result = process_user_query(query, user_id="test_user")
    
    print(f"Response: {result['response'][:200]}...")
    print(f"Metadata: {result['metadata']}")


def test_user_profile():
    """Test user profile management"""
    print("\n👤 Testing User Profile...")
    
    query = "Show my profile"
    result = process_user_query(query, user_id="test_user")
    
    print(f"Response: {result['response'][:200]}...")
    print(f"Metadata: {result['metadata']}")


def main():
    """Run all tests"""
    print("🚀 Starting Smart Agents Tests...\n")
    
    try:
        test_intent_classification()
        test_repo_analysis()
        test_skill_matching()
        test_bounty_estimation()
        test_user_profile()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
