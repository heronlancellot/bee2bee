"""
Slaanesh - Creative Problem Solving Agent with HTTP endpoint
"""

import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from llm_integration import create_llm
from shared_memory import shared_memory

# Config
AGENT_ID = "slaanesh"
AGENT_NAME = "Slaanesh"
SPECIALIZATION = "Creative Problem Solving and Innovation"

# LLM instance
llm = None

# Flask app
app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "agent": AGENT_NAME,
        "specialization": SPECIALIZATION,
        "status": "online",
        "llm_ready": llm is not None
    })


@app.route('/query', methods=['POST'])
def handle_query():
    """Handle incoming queries via HTTP"""
    try:
        data = request.json
        query_text = data.get('query')
        context = data.get('context')
        conversation_id = data.get('conversation_id')

        print(f"\n[{AGENT_NAME}] Received query:")
        print(f"  Query: {query_text[:50]}...")
        print(f"  Conversation: {conversation_id}")

        if not query_text:
            return jsonify({"error": "Query is required"}), 400

        # Get context from shared memory
        context_data = shared_memory.get_relevant_context(
            query=query_text,
            agent_id=AGENT_ID
        )

        # Get conversation history
        history = []
        if conversation_id:
            history = shared_memory.get_conversation_history(
                conversation_id,
                limit=5
            )

        # Generate response with LLM
        if llm:
            print(f"[{AGENT_NAME}] Generating LLM response...")

            import asyncio
            result = asyncio.run(llm.generate_agent_response(
                agent_name=AGENT_NAME,
                agent_specialization=SPECIALIZATION,
                query=query_text,
                context=context,
                conversation_history=history,
                shared_knowledge=context_data.get('knowledge', [])
            ))

            if result['success']:
                response_text = result['response']
                confidence = result.get('confidence', 0.7)
                print(f"[{AGENT_NAME}] ✓ Response generated (confidence: {confidence:.2f})")
            else:
                response_text = f"[{AGENT_NAME}] Error: {result.get('error')}"
                confidence = 0.3
                print(f"[{AGENT_NAME}] ✗ LLM error: {result.get('error')}")
        else:
            response_text = f"[{AGENT_NAME}] Hello! I'm {AGENT_NAME}, specialized in {SPECIALIZATION}. However, my LLM is not available right now."
            confidence = 0.2
            print(f"[{AGENT_NAME}] ⚠ LLM not available, using fallback")

        # Store in memory
        if conversation_id:
            shared_memory.store_conversation_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response_text,
                agent_id=AGENT_ID
            )

        print(f"[{AGENT_NAME}] ✓ Query completed\n")

        return jsonify({
            "response": response_text,
            "agent_name": AGENT_NAME,
            "confidence": confidence,
            "conversation_id": conversation_id
        })

    except Exception as e:
        print(f"[{AGENT_NAME}] ✗ Error: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            "response": f"[{AGENT_NAME}] An error occurred",
            "agent_name": AGENT_NAME,
            "confidence": 0.0,
            "error": str(e)
        }), 500


def initialize():
    """Initialize LLM and metadata"""
    global llm

    print(f"Starting {AGENT_NAME}...")

    # Initialize LLM
    try:
        llm = create_llm()
        print(f"✓ LLM initialized")
    except Exception as e:
        print(f"✗ LLM failed: {e}")

    # Store metadata
    shared_memory.update_agent_metadata(AGENT_ID, {
        "name": AGENT_NAME,
        "specialization": SPECIALIZATION,
        "status": "online"
    })

    print(f"✓ {AGENT_NAME} ready!")


if __name__ == "__main__":
    initialize()

    print("=" * 60)
    print(f"{AGENT_NAME} HTTP Server")
    print("=" * 60)
    print(f"Server: http://localhost:8001")
    print(f"Query endpoint: POST http://localhost:8001/query")
    print("=" * 60)

    app.run(host='0.0.0.0', port=8001, debug=False)
