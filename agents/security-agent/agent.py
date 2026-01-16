"""
Security Agent

Analyzes GitHub repositories for security vulnerabilities:
- Dependency scanning (OSV.dev API)
- Exposed credentials detection (future)
- Security best practices (future)
"""

from uagents import Agent
from protocols.chat import chat_proto
from protocols.security import security_proto
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Initialize agent
agent = Agent(
    name="Security Analyzer",
    seed="security_analyzer_nectardao_2025",
    port=8008,
    mailbox=True,
    publish_agent_details=True
)

# Register protocols
agent.include(chat_proto, publish_manifest=True)  # For frontend/ASI-1
agent.include(security_proto, publish_manifest=True)  # For inter-agent communication

if __name__ == "__main__":
    agent.run()
