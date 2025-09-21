from fastapi import APIRouter
from ..models.schemas import ProfileResponse
from ..deps import get_settings
import socket

router = APIRouter()

@router.get("/me", response_model=ProfileResponse)
async def get_profile():
    """Get current agent profile and routing policies"""
    settings = get_settings()
    
    # Determine available models based on configuration
    available_models = []
    
    # Local models (Ollama)
    try:
        import requests
        ollama_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if ollama_response.status_code == 200:
            models = ollama_response.json().get("models", [])
            available_models.extend([model["name"] for model in models])
    except:
        available_models.append("qwen2.5-coder:7b")  # Default assumption
    
    # Cloud models (could be expanded)
    available_models.extend([
        "openai/gpt-4o-mini",
        "anthropic/claude-3.7-sonnet"
    ])
    
    # Routing policy
    routing_policy = {
        "local_preference": ["code", "refactor", "debug", "quick"],
        "cloud_preference": ["legal", "longform", "critical", "research"],
        "fallback_threshold_seconds": 25,
        "max_local_tokens": 4096,
        "confidence_threshold": 0.7
    }
    
    return ProfileResponse(
        agent_id=f"sol-brain-{socket.gethostname()}",
        routing_policy=routing_policy,
        available_models=available_models,
        vector_backend=settings["vector_backend"],
        embed_backend=settings["embed_backend"]
    )