#!/usr/bin/env pwsh
# bootstrap.ps1 - ONE-TIME SETUP SCRIPT
param([string]$EnvFile = ".env")

Set-Location (Split-Path $PSScriptRoot -Parent)

if (!(Test-Path $EnvFile)) {
    Copy-Item ".env.example" $EnvFile
    Write-Host "Created $EnvFile from template. Please edit it with your settings." -ForegroundColor Yellow
}

Write-Host "Checking system requirements..." -ForegroundColor Cyan

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Error "Docker not found. Please install Docker Desktop."
    exit 1
}

# Check GPU support
try {
    nvidia-smi | Out-Null
    Write-Host "✓ NVIDIA GPU detected" -ForegroundColor Green
} catch {
    Write-Warning "NVIDIA GPU not detected. Ollama will run on CPU."
}

# Check available ports
$ports = @(5678, 11434, 5432, 8000, 3000)
foreach ($port in $ports) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($connection) {
        Write-Warning "Port $port is already in use"
    } else {
        Write-Host "✓ Port $port available" -ForegroundColor Green
    }
}

Write-Host "Starting SOL-Stack services..." -ForegroundColor Cyan
docker compose --env-file $EnvFile up -d --build

Write-Host @"
🚀 SOL-Stack is starting up!

Services will be available at:
- n8n Workflow Manager: http://localhost:5678
- Ollama API: http://localhost:11434
- Brain FastAPI: http://localhost:8000
- OpenWebUI: http://localhost:3000
- PostgreSQL: localhost:5432

Wait a few minutes for all services to initialize.
"@ -ForegroundColor Green