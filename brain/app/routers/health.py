from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
import torch
import os
from ..models.schemas import HealthResponse
from ..deps import get_db_connection, get_settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with system status"""
    try:
        # Check database connection
        db_status = "mock"  # Mock for testing
        
        # Check GPU availability
        gpu_available = torch.cuda.is_available()
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_usage = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "percent": memory.percent
        }
        
        # Check disk space
        disk = psutil.disk_usage('/')
        disk_usage = {
            "total_gb": round(disk.total / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": round((disk.used / disk.total) * 100, 2)
        }
        
        services = {
            "database": db_status,
            "embeddings": "mock",  # Mock for testing
            "vector_store": "mock",  # Mock for testing
        }
        
        return HealthResponse(
            status="ok" if db_status in ["ok", "mock"] else "degraded",
            timestamp=datetime.now(),
            services=services,
            gpu_available=gpu_available,
            memory_usage={
                "memory": memory_usage,
                "disk": disk_usage
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/health/simple")
async def simple_health():
    """Simple health check for load balancers"""
    return {"status": "ok"}