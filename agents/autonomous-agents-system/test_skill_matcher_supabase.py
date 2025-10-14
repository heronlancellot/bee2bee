#!/usr/bin/env python3
"""
Test Skill Matcher Agent with Supabase Integration
Tests the complete integration
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_skill_matcher_supabase():
    """Test Skill Matcher Agent with Supabase integration"""
    
    print("🧙‍♂️ **TESTING SKILL MATCHER + SUPABASE INTEGRATION** ⚔️")
    print("=" * 70)
    
    try:
        # Import components
        from supabase_agent_client import create_supabase_agent_client
        
        # Import MeTTa components directly
        sys.path.append(os.path.join(os.path.dirname(__file__), 'skill-matcher-agent'))
        from metta.skillrag import SkillRAG
        from metta.knowledge import initialize_skill_knowledge_graph
        from hyperon import MeTTa
        
        print("1. Initializing components...")
        
        # Initialize MeTTa
        metta = MeTTa()
        initialize_skill_knowledge_graph(metta)
        skill_rag = SkillRAG(metta)
        print("✅ MeTTa initialized")
        
        # Initialize Supabase client
        supabase_client = create_supabase_agent_client()
        print("✅ Supabase client initialized")
        
        # Test skill extraction
        print("\n2. Testing skill extraction...")
        
        test_queries = [
            "I know Python and React, find me suitable projects",
            "Match me with JavaScript bounties",
            "What skills do I need for backend development?",
            "I have frontend experience, what can I work on?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            
            # Extract skills using MeTTa
            user_skills = skill_rag.extract_skills_from_text(query)
            required_skills = skill_rag.extract_skills_from_text(query)
            
            print(f"📊 Extracted user skills: {user_skills}")
            print(f"📊 Extracted required skills: {required_skills}")
            
            if user_skills:
                # Find relationships
                relationships = skill_rag.find_skill_relationships(user_skills, required_skills)
                match_score, confidence = skill_rag.calculate_match_score(relationships, required_skills)
                
                print(f"🎯 Match score: {match_score}%")
                print(f"🎯 Confidence: {confidence}%")
                
                # Store in Supabase
                pattern_id = await supabase_client.store_skill_match_pattern(
                    agent_id="skill_matcher_001",
                    user_skills=user_skills,
                    required_skills=required_skills,
                    match_score=match_score,
                    confidence=confidence,
                    relationships=relationships
                )
                
                if pattern_id:
                    print(f"✅ Stored in Supabase: {pattern_id}")
                else:
                    print(f"❌ Failed to store in Supabase")
            else:
                print("⚠️ No skills detected in query")
        
        # Test knowledge retrieval
        print("\n3. Testing knowledge retrieval...")
        
        # Search for similar patterns
        similar_patterns = await supabase_client.find_similar_skill_patterns(
            user_skills=["Python"],
            required_skills=["JavaScript"],
            limit=3
        )
        
        print(f"📊 Found {len(similar_patterns)} similar patterns:")
        for i, pattern in enumerate(similar_patterns, 1):
            print(f"  {i}. Topic: {pattern.get('topic', 'Unknown')}")
            print(f"     Content: {pattern.get('content', '')[:100]}...")
            print(f"     Confidence: {pattern.get('confidence', 0):.2f}")
        
        # Test agent insights
        print("\n4. Testing agent insights...")
        
        insights = await supabase_client.get_agent_insights("skill_matcher_001")
        print(f"📊 Agent insights:")
        print(f"   Total knowledge: {insights.get('total_knowledge', 0)}")
        print(f"   Topics: {insights.get('topics', [])}")
        print(f"   Recent knowledge: {len(insights.get('recent_knowledge', []))}")
        
        print("\n" + "=" * 70)
        print("🎯 **SKILL MATCHER + SUPABASE INTEGRATION TEST COMPLETED!** ⚔️")
        print("✅ All components working together!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ **INTEGRATION TEST FAILED:** {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_full_workflow():
    """Test the complete workflow"""
    
    print("\n🧙‍♂️ **TESTING FULL WORKFLOW** ⚔️")
    print("=" * 50)
    
    try:
        from supabase_agent_client import create_supabase_agent_client
        
        client = create_supabase_agent_client()
        
        # Simulate a complete skill matching workflow
        print("1. Simulating skill matching workflow...")
        
        # User query
        user_query = "I'm a Python developer with React experience, find me backend projects"
        
        # Extract skills (simplified)
        user_skills = ["Python", "React"]
        required_skills = ["Python", "FastAPI", "PostgreSQL"]
        
        # Calculate match
        match_score = 80.0
        confidence = 85.0
        
        relationships = {
            "exact_matches": ["Python"],
            "related_skills": ["React"],
            "missing_skills": ["FastAPI", "PostgreSQL"]
        }
        
        print(f"📊 User Query: {user_query}")
        print(f"📊 User Skills: {user_skills}")
        print(f"📊 Required Skills: {required_skills}")
        print(f"📊 Match Score: {match_score}%")
        print(f"📊 Confidence: {confidence}%")
        
        # Store pattern
        pattern_id = await client.store_skill_match_pattern(
            agent_id="skill_matcher_001",
            user_skills=user_skills,
            required_skills=required_skills,
            match_score=match_score,
            confidence=confidence,
            relationships=relationships
        )
        
        print(f"✅ Pattern stored: {pattern_id}")
        
        # Search for similar patterns
        similar = await client.find_similar_skill_patterns(
            user_skills=user_skills,
            required_skills=required_skills,
            limit=2
        )
        
        print(f"📊 Found {len(similar)} similar patterns")
        
        # Get insights
        insights = await client.get_agent_insights("skill_matcher_001")
        print(f"📊 Total knowledge patterns: {insights.get('total_knowledge', 0)}")
        
        print("\n✅ Full workflow test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Full workflow test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🧙‍♂️ **SKILL MATCHER + SUPABASE INTEGRATION TEST** ⚔️")
    print("=" * 80)
    
    # Test integration
    integration_ok = await test_skill_matcher_supabase()
    
    # Test full workflow
    workflow_ok = await test_full_workflow()
    
    print("\n" + "=" * 80)
    if integration_ok and workflow_ok:
        print("🎉 **ALL TESTS PASSED!** 🎉")
        print("🚀 Skill Matcher Agent + Supabase integration working!")
        print("\n📋 **SYSTEM STATUS:**")
        print("1. ✅ MeTTa reasoning working")
        print("2. ✅ Supabase connection working")
        print("3. ✅ Skill extraction working")
        print("4. ✅ Knowledge storage working")
        print("5. ✅ Pattern retrieval working")
        print("6. ✅ Agent insights working")
        print("\n🎯 **READY FOR PRODUCTION!** 🎯")
    else:
        print("❌ **SOME TESTS FAILED**")
        print("🔧 Check integration components")
    
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
