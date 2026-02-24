#!/bin/bash

# MLBB AI Coach Setup Script

set -e

echo "🎮 MLBB AI Coach - Setup Script"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✓ Virtual environment created"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate  (on Linux/Mac)"
echo "  venv\\Scripts\\activate     (on Windows)"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys:"
    echo "  - ANTHROPIC_API_KEY"
    echo "  - GOOGLE_API_KEY"
    echo "  - PINECONE_API_KEY"
    echo ""
else
    echo "✓ .env file already exists"
fi

echo "================================"
echo "Next steps:"
echo "1. Activate the virtual environment"
echo "2. Install dependencies: pip install -r requirements.txt"
echo "3. Configure your .env file with API keys"
echo "4. Run the data ingestion script: python scripts/ingest_data.py"
echo "5. Start the server: uvicorn app.main:app --reload"
echo ""
echo "For Docker deployment:"
echo "  docker-compose up -d"
echo ""
echo "📚 See README.md for more details"
