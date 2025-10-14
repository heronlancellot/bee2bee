#!/bin/bash
# Smart Agents Startup Script

echo "🚀 Starting Smart Agents System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."
python -c "import requests" 2>/dev/null || {
    echo "📥 Installing requests..."
    pip install requests
}

# Start Python server in background
echo "🌐 Starting Python HTTP server..."
python smart_agents_server.py --port 5001 &
PYTHON_PID=$!

# Wait a moment for server to start
sleep 2

# Check if server is running
if curl -s http://localhost:5001/api/smart-agents > /dev/null 2>&1; then
    echo "✅ Python server is running on http://localhost:5001"
else
    echo "❌ Failed to start Python server"
    kill $PYTHON_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎯 Smart Agents System is ready!"
echo "📡 API Endpoint: http://localhost:5001/api/smart-agents"
echo "🌐 Frontend: http://localhost:3000/smart-agents"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $PYTHON_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT

# Keep script running
wait $PYTHON_PID
