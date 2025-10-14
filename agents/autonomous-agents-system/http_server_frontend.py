#!/usr/bin/env python3
"""
HTTP Server for Frontend Integration
Connects Next.js frontend to autonomous agents system
Port 5001 - Compatible with existing frontend API
"""

import sys
import os
import json
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Add paths
sys.path.append(os.path.dirname(__file__))


class AutonomousAgentsHandler(BaseHTTPRequestHandler):
    """HTTP Handler for autonomous agents"""

    def _set_cors_headers(self):
        """Set CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/smart-agents':
            self.handle_get_capabilities()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/smart-agents':
            self.handle_smart_agents_query()
        else:
            self.send_error(404, "Not Found")

    def handle_get_capabilities(self):
        """GET /api/smart-agents - Return agent capabilities"""
        try:
            capabilities = {
                "agents": {
                    "user_profile": {
                        "name": "User Profile Agent",
                        "capabilities": ["profile_management", "skill_tracking", "preferences"],
                        "port": 8009,
                        "status": "active",
                        "reasoning": "metta"
                    },
                    "skill_matcher": {
                        "name": "Skill Matcher Agent",
                        "capabilities": ["skill_matching", "gap_analysis", "confidence_scoring"],
                        "port": 8010,
                        "status": "active",
                        "reasoning": "metta"
                    },
                    "bounty_estimator": {
                        "name": "Bounty Estimator Agent",
                        "capabilities": ["bounty_estimation", "complexity_analysis", "value_calculation"],
                        "port": 8011,
                        "status": "active",
                        "reasoning": "metta"
                    }
                },
                "count": 3,
                "status": "active"
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._set_cors_headers()
            self.end_headers()

            self.wfile.write(json.dumps(capabilities, indent=2).encode('utf-8'))

        except Exception as e:
            print(f"Error in GET: {e}")
            self.send_error(500, str(e))

    def handle_smart_agents_query(self):
        """POST /api/smart-agents - Query autonomous agents"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            message = data.get('message', '')
            user_id = data.get('user_id', 'anonymous')
            conversation_id = data.get('conversation_id', 'new_conversation')

            if not message:
                self.send_error(400, "Message is required")
                return

            print(f"\n📩 Received query: {message[:50]}...")

            # Detect intent
            intent = self.detect_intent(message)
            print(f"🎯 Intent: {intent}")

            # Process with autonomous agents
            if intent == "FIND_MATCHES":
                result = self.process_find_matches(message, user_id, conversation_id)
            else:
                result = self.process_general_chat(message, user_id, conversation_id)

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._set_cors_headers()
            self.end_headers()

            self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))

            print(f"✅ Response sent!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Error: {e}")
            self.send_error(500, f"Error: {str(e)}")

    def detect_intent(self, message: str) -> str:
        """Detect user intent with improved keyword matching"""
        message_lower = message.lower()

        # Keywords for FIND_MATCHES intent
        find_keywords = [
            "show", "find", "get", "search", "look", "fetch",
            "issues", "bounties", "bounty", "tasks", "projects",
            "python", "javascript", "typescript", "react", "node",
            "rust", "go", "java", "ruby", "php", "swift", "kotlin",
            "match", "suitable", "recommend", "suggest",
            "solve", "work on", "contribute"
        ]

        # Keywords for EXPLAIN_REASONING intent
        explain_keywords = [
            "why", "explain", "reasoning", "how", "what",
            "tell me", "describe", "elaborate"
        ]

        # Check for FIND_MATCHES intent
        if any(word in message_lower for word in find_keywords):
            return "FIND_MATCHES"

        # Check for EXPLAIN_REASONING intent
        elif any(word in message_lower for word in explain_keywords):
            return "EXPLAIN_REASONING"

        # Default to general_chat
        else:
            return "general_chat"

    def extract_skills(self, message: str) -> list:
        """Extract skills from message"""
        common_skills = ["Python", "JavaScript", "TypeScript", "React", "Node.js",
                         "Go", "Rust", "Java", "C++", "Ruby", "asyncio", "FastAPI"]

        found_skills = []
        message_lower = message.lower()

        for skill in common_skills:
            if skill.lower() in message_lower:
                found_skills.append(skill)

        return found_skills if found_skills else ["Python"]

    def process_find_matches(self, message: str, user_id: str, conversation_id: str) -> dict:
        """Process FIND_MATCHES intent - calls Orchestrator Agent REST endpoint"""

        import requests

        # Call Orchestrator Agent REST endpoint
        orchestrator_url = "http://localhost:8012/api/query"

        payload = {
            "message": message,
            "user_id": user_id,
            "conversation_id": conversation_id
        }

        try:
            response = requests.post(orchestrator_url, json=payload, timeout=15)

            if response.status_code == 200:
                result = response.json()

                return {
                    "response": result.get("response"),
                    "intent": result.get("intent"),
                    "intent_confidence": 0.9,
                    "agent_id": result.get("agent_id"),
                    "conversation_id": result.get("conversation_id"),
                    "metadata": {
                        "agents_consulted": ["user_profile", "skill_matcher", "bounty_estimator"],
                        "query_mode": "parallel_via_agentverse",
                        "reasoning_engine": "metta"
                    },
                    "timestamp": result.get("timestamp")
                }
            else:
                raise Exception(f"Orchestrator returned {response.status_code}")

        except Exception as e:
            print(f"❌ Error calling orchestrator: {e}")

            # Fallback response
            from datetime import datetime
            return {
                "response": f"⚠️ Could not reach orchestrator agent. Is it running on port 8012?\n\nError: {str(e)}",
                "intent": "error",
                "intent_confidence": 1.0,
                "agent_id": "http_server",
                "conversation_id": conversation_id,
                "metadata": {"error": str(e)},
                "timestamp": datetime.now().isoformat()
            }

    def process_general_chat(self, message: str, user_id: str, conversation_id: str) -> dict:
        """Process general chat"""
        from datetime import datetime

        return {
            "response": f"""🤖 **Autonomous Agents System**

I understand you asked: "{message}"

I coordinate 3 specialized autonomous agents with MeTTa reasoning:

**Try asking:**
• "Show me Python issues I can solve"
• "Find JavaScript bounties for me"
• "Match me with React projects"

**My Agents:**
- 👤 User Profile Agent (analyzes your skills)
- 🎯 Skill Matcher Agent (finds perfect matches)
- 💰 Bounty Estimator Agent (calculates values)

What would you like to do?""",
            "intent": "general_chat",
            "intent_confidence": 0.7,
            "agent_id": "orchestrator",
            "conversation_id": conversation_id,
            "metadata": {},
            "timestamp": datetime.now().isoformat()
        }

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def run_server(port=5001):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, AutonomousAgentsHandler)

    print("\n" + "="*60)
    print("🚀 AUTONOMOUS AGENTS HTTP SERVER")
    print("="*60)
    print(f"\n📡 Server running on: http://localhost:{port}")
    print(f"📍 API Endpoint: http://localhost:{port}/api/smart-agents")
    print(f"\n✅ Frontend Integration Ready!")
    print(f"\nThis server connects your Next.js frontend to:")
    print(f"  • User Profile Agent (port 8009)")
    print(f"  • Skill Matcher Agent (port 8010)")
    print(f"  • Bounty Estimator Agent (port 8011)")
    print(f"\n⚠️  Make sure the 3 agents are running before testing!")
    print(f"\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        httpd.server_close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Autonomous Agents HTTP Server for Frontend')
    parser.add_argument('--port', type=int, default=5001, help='Port to run server on (default: 5001)')
    args = parser.parse_args()

    run_server(args.port)
