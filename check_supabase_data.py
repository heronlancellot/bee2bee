#!/usr/bin/env python3
"""
Script to check Supabase data
"""

import requests
import json

# Supabase local configuration
SUPABASE_URL = "http://127.0.0.1:54321"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"

def check_table(table_name):
    """Check data in a specific table"""
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 {table_name.upper()} TABLE:")
            print(f"   Records: {len(data)}")
            if data:
                print(f"   Sample record: {json.dumps(data[0], indent=2)}")
            else:
                print("   No records found")
        else:
            print(f"❌ Error checking {table_name}: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception checking {table_name}: {e}")

def main():
    print("🔍 Checking Supabase Local Data...")
    
    # Check conversations table
    check_table("conversations")
    
    # Check agent_knowledge table
    check_table("agent_knowledge")
    
    # Check profiles table
    check_table("profiles")

if __name__ == "__main__":
    main()
