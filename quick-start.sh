#!/bin/bash
# quick-start.sh - Get SOL-Stack running in 2 minutes

set -e

echo "🚀 SOL-Stack Quick Start"
echo "=========================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found"

# Check if we're in the right directory
if [ ! -f "brain/app/main.py" ]; then
    echo "❌ Please run this script from the sol-stack root directory"
    exit 1
fi

echo "✅ In correct directory"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install minimal dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn pydantic psutil numpy

# Copy environment file
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment..."
    cp infra/.env.example .env
    echo "✏️  Edit .env file to add your API keys and settings"
fi

# Start brain service
echo "🧠 Starting SOL-Stack Brain service..."
echo ""
echo "🌐 Brain service will be available at: http://localhost:8000"
echo "📊 Health check: http://localhost:8000/health"
echo "👤 Profile: http://localhost:8000/profile/me"
echo ""
echo "💡 To test RAG: curl -X POST http://localhost:8000/rag/ingest -F 'text=Hello world' -F 'source=test'"
echo "💡 VS Code: Use Ctrl+Shift+P → 'Tasks: Run Task' → 'Escalate to Cloud Agent'"
echo ""
echo "🛑 Press Ctrl+C to stop"
echo ""

cd brain
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload