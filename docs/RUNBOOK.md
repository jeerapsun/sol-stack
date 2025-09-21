# SOL-Stack Runbook: Local + Cloud Agent Architecture

## Overview
This runbook provides step-by-step instructions for operating the SOL-Stack Local + Cloud agent architecture.

## Quick Start

### 1. Initial Setup
```powershell
# Navigate to project directory
cd /path/to/sol-stack

# Run bootstrap script to start all services
./infra/scripts/bootstrap.ps1
```

### 2. Service URLs
After successful startup, services will be available at:

- **Brain FastAPI**: http://localhost:8000
- **n8n Workflow Manager**: http://localhost:5678  
- **Ollama API**: http://localhost:11434
- **OpenWebUI**: http://localhost:3000
- **PostgreSQL**: localhost:5432

### 3. Health Checks
```bash
# Check brain service
curl http://localhost:8000/health

# Check n8n
curl http://localhost:5678/healthz

# Check ollama
curl http://localhost:11434/api/tags
```

## Core Operations

### RAG Content Ingestion
```bash
# Ingest text file
curl -X POST http://localhost:8000/rag/ingest \
  -F "file=@document.pdf" \
  -F "source=manual_upload"

# Ingest from URL
curl -X POST http://localhost:8000/rag/ingest \
  -F "url=https://example.com/article" \
  -F "source=web_scrape"
```

### Memory Logging
```bash
# Log conversation
curl -X POST http://localhost:8000/memory/log \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "How do I deploy to cloud?",
    "response": "Use the cloud deployment scripts...",
    "intent": "deployment",
    "meta": {"confidence": 0.9}
  }'
```

### RAG Queries
```bash
# Query with context retrieval
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to deploy the brain service?",
    "k": 5,
    "route_hint": "local"
  }'
```

## VS Code Integration

### Escalate to Cloud Agent
1. Select text in editor containing the task description
2. Run command: `Terminal: Run Task`
3. Choose: **Escalate to Cloud Agent**
4. The task will be sent to n8n for cloud processing

### Available Tasks
- **Start SOL-Stack**: Bootstrap all services
- **Test Brain API**: Quick health check
- **Escalate to Cloud Agent**: Send task to cloud

## Maintenance

### Daily Backup
```powershell
# Manual backup
./infra/scripts/backup_pg.ps1

# Scheduled backup (add to Task Scheduler)
schtasks /create /tn "SOL-Stack Backup" /tr "C:\path\to\backup_pg.ps1" /sc daily /st 02:00
```

### GPU Monitoring
```powershell
# Check GPU temperature
./infra/scripts/gpu_watch.ps1

# Set up monitoring (run every 5 minutes)
schtasks /create /tn "GPU Monitor" /tr "C:\path\to\gpu_watch.ps1" /sc minute /mo 5
```

### Log Monitoring
```bash
# View brain service logs
docker logs brain

# View n8n logs
docker logs n8n

# View postgres logs
docker logs pg-local
```

## Troubleshooting

### Service Won't Start
1. Check port conflicts: `netstat -ano | findstr :8000`
2. Check Docker status: `docker ps`
3. Check logs: `docker logs <service_name>`

### Database Connection Issues
1. Verify PostgreSQL is running: `docker ps | grep postgres`
2. Test connection: `psql -h localhost -U agi -d agi_db`
3. Check environment variables in `.env`

### GPU Not Detected
1. Verify NVIDIA drivers: `nvidia-smi`
2. Check Docker GPU support: `docker run --gpus all nvidia/cuda:11.0-base nvidia-smi`
3. Update Docker Desktop to latest version

### RAG Ingestion Fails
1. Check embedding model status: `curl http://localhost:8000/health`
2. Verify file permissions on data directories
3. Check available disk space

## Performance Optimization

### Memory Usage
- Monitor with: `docker stats`
- Adjust embedding model size based on available RAM
- Use swap file for large datasets

### GPU Utilization  
- Monitor with: `nvidia-smi -l 1`
- Batch embedding operations for efficiency
- Consider mixed precision for larger models

### Storage Management
- Regular cleanup of old embeddings
- Compress backup files
- Monitor disk usage: `df -h`

## Security

### Environment Variables
- Never commit `.env` files
- Use strong passwords for database
- Rotate API keys regularly

### Network Security
- Bind services to localhost only in production
- Use VPN for remote access
- Enable firewall rules

### Data Protection
- Encrypt sensitive embeddings
- Regular backup verification
- Secure backup storage

## Emergency Procedures

### Complete System Reset
```powershell
# Stop all services
docker compose down

# Remove data (WARNING: destructive)
docker volume prune

# Restart from scratch
./infra/scripts/bootstrap.ps1
```

### Backup Restoration
```powershell
# Stop services
docker compose down

# Restore database
psql -h localhost -U agi -d agi_db < backup_file.sql

# Restart services
docker compose up -d
```

## Monitoring Dashboard

Access system metrics at:
- Brain API health: http://localhost:8000/health
- Memory stats: http://localhost:8000/memory/stats  
- RAG stats: http://localhost:8000/rag/stats
- Admin dashboard: http://localhost:8000/admin/stats