from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class MemoryLogRequest(BaseModel):
    user_query: str
    response: str
    intent: Optional[str] = None
    meta: Optional[Dict[str, Any]] = {}

class MemorySearchRequest(BaseModel):
    query: str
    k: int = 5

class RAGIngestRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class RAGQueryRequest(BaseModel):
    query: str
    k: int = 5
    route_hint: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]
    gpu_available: bool
    memory_usage: Dict[str, Any]

class ProfileResponse(BaseModel):
    agent_id: str
    routing_policy: Dict[str, Any]
    available_models: List[str]
    vector_backend: str
    embed_backend: str

class RAGSearchResult(BaseModel):
    content: str
    source: str
    score: float
    metadata: Dict[str, Any]

class RAGQueryResponse(BaseModel):
    answer: str
    references: List[RAGSearchResult]
    context_used: str
    model_used: str