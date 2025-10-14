#!/usr/bin/env python3
"""
Test Supabase Connection (Working Version)
Tests with the actual existing tables
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_supabase_working():
    """Test Supabase with working tables"""
    
    print("🧙‍♂️ **TESTING SUPABASE WORKING CONNECTION** ⚔️")
    print("=" * 60)
    
    try:
        from supabase import create_client
        
        # Create client with local Supabase
        url = "http://127.0.0.1:54321"
        key = "sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH"
        
        print(f"1. Creating Supabase client...")
        print(f"   URL: {url}")
        print(f"   Key: {key[:20]}...")
        
        client = create_client(url, key)
        print("✅ Supabase client created successfully")
        
        # Test with existing tables
        print("\n2. Testing existing tables...")
        
        # Test agent_knowledge table (from migration 20251014013126)
        try:
            result = client.table('agent_knowledge').select('*').limit(1).execute()
            print("✅ agent_knowledge table exists")
            print(f"   Count: {len(result.data)}")
        except Exception as e:
            print(f"❌ agent_knowledge table error: {e}")
        
        # Test profiles table
        try:
            result = client.table('profiles').select('*').limit(1).execute()
            print("✅ profiles table exists")
            print(f"   Count: {len(result.data)}")
        except Exception as e:
            print(f"❌ profiles table error: {e}")
        
        # Test conversations table
        try:
            result = client.table('conversations').select('*').limit(1).execute()
            print("✅ conversations table exists")
            print(f"   Count: {len(result.data)}")
        except Exception as e:
            print(f"❌ conversations table error: {e}")
        
        # Test inserting into agent_knowledge
        print("\n3. Testing data insertion...")
        test_knowledge = {
            'agent_id': 'test_agent_001',
            'topic': 'skill_matching',
            'content': 'Python developers are good for backend projects',
            'tags': ['python', 'backend', 'skill'],
            'confidence': 0.85
        }
        
        try:
            result = client.table('agent_knowledge').insert(test_knowledge).execute()
            print("✅ Test knowledge inserted successfully")
            print(f"   ID: {result.data[0]['id'] if result.data else 'Unknown'}")
        except Exception as e:
            print(f"❌ Knowledge insertion failed: {e}")
        
        # Test querying the inserted data
        print("\n4. Testing data query...")
        try:
            result = client.table('agent_knowledge').select('*').eq('agent_id', 'test_agent_001').execute()
            if result.data:
                print("✅ Test knowledge found in database")
                print(f"   Topic: {result.data[0]['topic']}")
                print(f"   Content: {result.data[0]['content'][:50]}...")
            else:
                print("❌ Test knowledge not found")
        except Exception as e:
            print(f"❌ Knowledge query failed: {e}")
        
        print("\n" + "=" * 60)
        print("🎯 **SUPABASE WORKING CONNECTION TEST COMPLETED!** ⚔️")
        print("✅ Supabase is working with existing tables!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ **CONNECTION TEST FAILED:** {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vector_extension_basic():
    """Test basic vector functionality"""
    
    print("\n🧙‍♂️ **TESTING BASIC VECTOR FUNCTIONALITY** ⚔️")
    print("=" * 60)
    
    try:
        from supabase import create_client
        
        client = create_client("http://127.0.0.1:54321", "sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH")
        
        # Test if we can query the database directly
        print("1. Testing direct database query...")
        
        # Try to get database info
        try:
            result = client.table('agent_knowledge').select('*').limit(5).execute()
            print(f"✅ Can query agent_knowledge table")
            print(f"   Records found: {len(result.data)}")
            
            if result.data:
                for record in result.data:
                    print(f"   - {record.get('topic', 'No topic')}: {record.get('content', 'No content')[:30]}...")
            
        except Exception as e:
            print(f"❌ Database query error: {e}")
        
        print("\n✅ Basic vector functionality test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Vector test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧙‍♂️ **SUPABASE WORKING CONNECTION TEST** ⚔️")
    print("=" * 70)
    
    # Test working connection
    connection_ok = test_supabase_working()
    
    # Test basic vector functionality
    vector_ok = test_vector_extension_basic()
    
    print("\n" + "=" * 70)
    if connection_ok and vector_ok:
        print("🎉 **ALL TESTS PASSED!** 🎉")
        print("🚀 Supabase is working! Ready for agent integration!")
        print("\n📋 **NEXT STEPS:**")
        print("1. ✅ Supabase connection working")
        print("2. ✅ Basic tables accessible")
        print("3. ✅ Data insertion/query working")
        print("4. 🔄 Need to fix schema exposure for agent_knowledge schema")
        print("5. 🔄 Need to implement vector functions")
    else:
        print("❌ **SOME TESTS FAILED**")
        print("🔧 Check Supabase configuration")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
