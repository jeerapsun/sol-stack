# quick-start.ps1 - Get SOL-Stack running in 2 minutes

Write-Host "🚀 SOL-Stack Quick Start" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 3 is required. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Check if we're in the right directory
if (!(Test-Path "brain/app/main.py")) {
    Write-Host "❌ Please run this script from the sol-stack root directory" -ForegroundColor Red
    exit 1
}

Write-Host "✅ In correct directory" -ForegroundColor Green

# Create virtual environment
if (!(Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install minimal dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install fastapi uvicorn pydantic psutil numpy

# Copy environment file
if (!(Test-Path ".env")) {
    Write-Host "⚙️  Setting up environment..." -ForegroundColor Yellow
    Copy-Item "infra\.env.example" ".env"
    Write-Host "✏️  Edit .env file to add your API keys and settings" -ForegroundColor Yellow
}

# Start brain service
Write-Host ""
Write-Host "🧠 Starting SOL-Stack Brain service..." -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Brain service will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "📊 Health check: http://localhost:8000/health" -ForegroundColor Green
Write-Host "👤 Profile: http://localhost:8000/profile/me" -ForegroundColor Green
Write-Host ""
Write-Host "💡 To test RAG:" -ForegroundColor Yellow
Write-Host "   curl -X POST http://localhost:8000/rag/ingest -F 'text=Hello world' -F 'source=test'"
Write-Host "💡 VS Code: Use Ctrl+Shift+P → 'Tasks: Run Task' → 'Escalate to Cloud Agent'" -ForegroundColor Yellow
Write-Host ""
Write-Host "🛑 Press Ctrl+C to stop" -ForegroundColor Red
Write-Host ""

Set-Location brain
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload