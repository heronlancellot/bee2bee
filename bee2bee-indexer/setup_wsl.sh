#!/bin/bash
# Setup script for bee2bee-indexer in WSL

echo "🐝 Bee2Bee Indexer - WSL Setup"
echo "=============================="
echo ""

# Install pip if needed
if ! command -v pip3 &> /dev/null; then
    echo "📦 Installing pip..."
    sudo apt update
    sudo apt install -y python3-pip python3-venv
fi

# Create venv
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate venv
echo "✅ Activating venv..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the test:"
echo "  source venv/bin/activate"
echo "  python test_without_chroma.py"
