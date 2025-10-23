#!/usr/bin/env python3
"""
Bridge HTTP → Mailbox
Conecta frontend HTTP com orchestrator_uagents mailbox
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import tempfile
import subprocess

# Add paths
sys.path.append(os.path.dirname(__file__))

class BridgeHandler(BaseHTTPRequestHandler):
    """HTTP Handler que conecta com orchestrator_uagents"""

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

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/query':
            self.handle_query()
        else:
            self.send_error(404, "Not Found")

    def handle_query(self):
        """Handle query requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            message = data.get('message', '')
            user_id = data.get('user_id', 'anonymous')
            conversation_id = data.get('conversation_id', 'new_conversation')

            if not message:
                self.send_error(400, "Message is required")
                return

            print(f"\n📩 Bridge received query: {message[:50]}...")

            # Call orchestrator_uagents via mailbox
            result = self.call_orchestrator_uagents(message, user_id, conversation_id)

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._set_cors_headers()
            self.end_headers()

            self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))

            print(f"✅ Bridge response sent!")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Bridge error: {e}")
            self.send_error(500, f"Error: {str(e)}")

    def call_orchestrator_uagents(self, message: str, user_id: str, conversation_id: str) -> dict:
        """Call orchestrator_uagents via mailbox communication"""
        
        try:
            # Create query data
            query_data = {
                "message": message,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "skills": self.extract_skills(message),
                "years_experience": 3,
                "issue_query": message
            }

            # Create temporary file with query
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(query_data, f)
                query_file = f.name

            # Run orchestrator_uagents.py with timeout
            result = subprocess.run([
                'python', 'orchestrator_uagents.py', '--query-file', query_file
            ], 
            capture_output=True, 
            text=True, 
            timeout=60,  # Increased timeout to 60 seconds
            cwd=os.path.dirname(__file__)
            )

            # Clean up temp file
            os.unlink(query_file)

            if result.returncode == 0:
                # Parse the output to extract the synthesized response
                output_lines = result.stdout.split('\n')
                
                # Find the synthesized response section
                response_started = False
                response_lines = []
                
                for line in output_lines:
                    if "📋 SYNTHESIZED RESPONSE:" in line:
                        response_started = True
                        continue
                    elif response_started and line.strip():
                        if line.startswith("="):
                            break
                        response_lines.append(line)

                synthesized_response = '\n'.join(response_lines).strip()
                
                if not synthesized_response:
                    synthesized_response = "# 🎯 Agent Response\n\n" + result.stdout

                return {
                    "response": synthesized_response,
                    "intent": "FIND_MATCHES",
                    "agent_id": "orchestrator_uagents",
                    "conversation_id": conversation_id,
                    "metadata": {
                        "agents_consulted": ["user_profile", "skill_matcher", "bounty_estimator"],
                        "query_mode": "mailbox_via_uagents",
                        "reasoning_engine": "metta"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise Exception(f"Orchestrator failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            return {
                "response": "# ⏰ Timeout Error\n\n**The agents took too long to respond!**\n\nThis might mean:\n- Agents are not running\n- Network issues\n- AgentVerse API problems\n\n**Try again in a moment!**",
                "intent": "FIND_MATCHES",
                "agent_id": "orchestrator_uagents",
                "conversation_id": conversation_id,
                "metadata": {"error": "timeout"},
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "response": f"# ❌ Error\n\n**Error calling orchestrator:** {str(e)}\n\n**This means the orchestrator_uagents.py is not working correctly!**",
                "intent": "FIND_MATCHES", 
                "agent_id": "orchestrator_uagents",
                "conversation_id": conversation_id,
                "metadata": {"error": str(e)},
                "timestamp": datetime.now().isoformat()
            }

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


def run_bridge(port=8012):
    """Run the bridge server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, BridgeHandler)
    
    print("🌉 Starting HTTP → Mailbox Bridge...")
    print(f"📡 Bridge API: http://localhost:{port}/api/query")
    print(f"🌐 Port: {port}")
    print("\nFeatures:")
    print("  1. Receives HTTP requests from frontend")
    print("  2. Calls orchestrator_uagents via mailbox")
    print("  3. Returns HTTP responses to frontend")
    print("\nStarting server...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Bridge stopped!")
        httpd.shutdown()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='HTTP → Mailbox Bridge')
    parser.add_argument('--port', type=int, default=8012, help='Port to run on')
    args = parser.parse_args()
    
    run_bridge(args.port)
