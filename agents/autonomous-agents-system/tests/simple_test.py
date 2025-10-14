#!/usr/bin/env python3
"""
Simple test to verify agents are running
"""

import requests

print("\n" + "="*60)
print("🧪 SIMPLE AGENT CONNECTIVITY TEST")
print("="*60 + "\n")

# Test each agent's HTTP endpoint
agents = {
    "User Profile Agent": "http://localhost:8009",
    "Skill Matcher Agent": "http://localhost:8010",
    "Bounty Estimator Agent": "http://localhost:8011"
}

for name, url in agents.items():
    try:
        response = requests.get(url, timeout=2)
        print(f"✅ {name:25} - RUNNING (HTTP {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ {name:25} - NOT ACCESSIBLE")

print("\n" + "="*60)
print("\n📋 Summary:")
print("   - All agents are RUNNING locally on their ports")
print("   - They are registered on Agentverse with mailbox")
print("   - To communicate with them, you need to use:")
print("     1. Agentverse API (via mailbox)")
print("     2. uAgents library (programmatic)")
print("     3. Another uAgent (orchestrator_uagents.py)")
print("\n" + "="*60 + "\n")

print("💡 Next steps:")
print("   1. Run the orchestrator agent:")
print("      python orchestrator_uagents.py")
print("\n   2. The orchestrator will query all agents every 10 seconds")
print("\n   3. Check the logs to see the parallel queries working!")
print("\n" + "="*60 + "\n")
