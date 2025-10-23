"""
Flask API Server using direct HTTP calls to agents
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Agent HTTP endpoints
AGENT_ENDPOINTS = {
    "sigmar": "http://localhost:8000",
    "slaanesh": "http://localhost:8001"
}

# Agent metadata
AGENTS = {
    "sigmar": {
        "name": "Sigmar",
        "specialization": "Strategic Analysis and Planning"
    },
    "slaanesh": {
        "name": "Slaanesh",
        "specialization": "Creative Problem Solving and Innovation"
    }
}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    agent_status = {}
    for agent_id, endpoint in AGENT_ENDPOINTS.items():
        try:
            resp = requests.get(f"{endpoint}/", timeout=2)
            agent_status[agent_id] = "online" if resp.status_code else "offline"
        except:
            agent_status[agent_id] = "offline"

    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": agent_status
    })


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get list of available agents"""
    agent_list = []

    for agent_id, agent_info in AGENTS.items():
        # Try to check if agent is online
        try:
            resp = requests.get(f"{AGENT_ENDPOINTS[agent_id]}/", timeout=1)
            status = "online"
        except:
            status = "offline"

        agent_list.append({
            "id": agent_id,
            "name": agent_info["name"],
            "specialization": agent_info["specialization"],
            "endpoint": AGENT_ENDPOINTS[agent_id],
            "status": status
        })

    return jsonify({
        "agents": agent_list,
        "count": len(agent_list)
    })


@app.route('/api/chat/send', methods=['POST'])
def send_message():
    """Send a message to one or more agents via HTTP"""
    try:
        data = request.json

        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400

        message = data['message']
        target_agents = data.get('agents', list(AGENTS.keys()))
        context = data.get('context')
        conversation_id = data.get('conversation_id', str(uuid.uuid4()))

        print(f"\n[API] New request:")
        print(f"  Message: {message}")
        print(f"  Agents: {target_agents}")
        print(f"  Conversation: {conversation_id}")

        # Query each agent via direct HTTP
        responses = []

        for agent_id in target_agents:
            if agent_id not in AGENTS:
                continue

            endpoint = AGENT_ENDPOINTS.get(agent_id)
            if not endpoint:
                responses.append({
                    "agent_id": agent_id,
                    "agent_name": AGENTS[agent_id]["name"],
                    "response": f"[{AGENTS[agent_id]['name']}] Endpoint not configured",
                    "confidence": 0.0,
                    "error": "No endpoint"
                })
                continue

            try:
                print(f"\n[API] Querying {agent_id} at {endpoint}...")

                # Send POST request to agent
                response = requests.post(
                    f"{endpoint}/query",
                    json={
                        "query": message,
                        "context": context,
                        "conversation_id": conversation_id
                    },
                    timeout=30.0
                )

                print(f"[API] Response status: {response.status_code}")

                if response.status_code == 200:
                    response_data = response.json()
                    print(f"[API] Response data: {response_data}")

                    responses.append({
                        "agent_id": agent_id,
                        "agent_name": response_data.get("agent_name", AGENTS[agent_id]["name"]),
                        "response": response_data.get("response", "No response"),
                        "confidence": response_data.get("confidence", 0.5),
                        "conversation_id": response_data.get("conversation_id")
                    })
                else:
                    responses.append({
                        "agent_id": agent_id,
                        "agent_name": AGENTS[agent_id]["name"],
                        "response": f"[{AGENTS[agent_id]['name']}] HTTP {response.status_code}",
                        "confidence": 0.0,
                        "error": f"HTTP {response.status_code}"
                    })

            except requests.Timeout:
                print(f"[API] Timeout querying {agent_id}")
                responses.append({
                    "agent_id": agent_id,
                    "agent_name": AGENTS[agent_id]["name"],
                    "response": f"[{AGENTS[agent_id]['name']}] Request timeout",
                    "confidence": 0.0,
                    "error": "Timeout"
                })
            except Exception as e:
                print(f"[API] Error querying {agent_id}: {e}")
                responses.append({
                    "agent_id": agent_id,
                    "agent_name": AGENTS[agent_id]["name"],
                    "response": f"[{AGENTS[agent_id]['name']}] Connection failed",
                    "confidence": 0.0,
                    "error": str(e)
                })

        print(f"\n[API] Completed with {len(responses)} responses\n")

        return jsonify({
            "success": True,
            "conversation_id": conversation_id,
            "responses": responses,
            "message": "Queries completed"
        })

    except Exception as e:
        print(f"[API] Error in send_message: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get conversation history"""
    try:
        from shared_memory import shared_memory
        messages = shared_memory.get_conversation_history(conversation_id)

        return jsonify({
            "success": True,
            "conversation_id": conversation_id,
            "messages": messages,
            "message_count": len(messages)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Agent HTTP API Server")
    print("=" * 60)
    print(f"Server: http://localhost:5001")
    print()
    print("Agent endpoints:")
    for agent_id, endpoint in AGENT_ENDPOINTS.items():
        print(f"  - {AGENTS[agent_id]['name']}: {endpoint}")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5001, debug=True)
