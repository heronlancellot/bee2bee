#!/usr/bin/env python3
"""
Simple HTTP Server for Smart Agents
This allows the frontend to call the Python agents via HTTP
"""

import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Add the smart-agents directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'smart-agents'))

# Use new autonomous agents orchestrator
from orchestrator_autonomous import process_user_query


class SmartAgentsHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/smart-agents':
            self.handle_smart_agents()
        else:
            self.send_error(404, "Not Found")
    
    def do_GET(self):
        if self.path == '/api/smart-agents':
            self.handle_get_capabilities()
        else:
            self.send_error(404, "Not Found")
    
    def handle_smart_agents(self):
        """Handle POST requests to smart agents"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract parameters
            message = data.get('message', '')
            user_id = data.get('user_id', 'anonymous')
            conversation_id = data.get('conversation_id')
            context = data.get('context', {})
            
            if not message:
                self.send_error(400, "Message is required")
                return
            
            # Process query through smart agents
            result = process_user_query(
                query=message,
                user_id=user_id,
                conversation_id=conversation_id,
                context=context
            )
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response_data = json.dumps(result, indent=2)
            self.wfile.write(response_data.encode('utf-8'))
            
        except Exception as e:
            print(f"Error processing request: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def handle_get_capabilities(self):
        """Handle GET requests for agent capabilities"""
        try:
            from orchestrator_autonomous import get_bridge

            bridge = get_bridge()
            capabilities = bridge.get_agent_capabilities()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = json.dumps({
                "agents": capabilities,
                "count": len(capabilities),
                "status": "active"
            }, indent=2)
            self.wfile.write(response_data.encode('utf-8'))
            
        except Exception as e:
            print(f"Error getting capabilities: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass


def run_server(port=5001):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SmartAgentsHandler)
    
    print(f"🚀 Smart Agents Server running on http://localhost:{port}")
    print(f"📡 API Endpoint: http://localhost:{port}/api/smart-agents")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Agents HTTP Server')
    parser.add_argument('--port', type=int, default=5001, help='Port to run server on')
    args = parser.parse_args()
    
    run_server(args.port)
