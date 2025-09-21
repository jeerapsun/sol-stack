import os
import psycopg2
from psycopg2.extras import RealDictCursor
from functools import lru_cache
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@lru_cache()
def get_settings():
    """Get application settings from environment variables"""
    return {
        "postgres_host": os.getenv("POSTGRES_HOST", "localhost"),
        "postgres_port": int(os.getenv("POSTGRES_PORT", "5432")),
        "postgres_db": os.getenv("POSTGRES_DB", "agi_db"),
        "postgres_user": os.getenv("POSTGRES_USER", "agi"),
        "postgres_password": os.getenv("POSTGRES_PASSWORD", "agi_031244585"),
        "embed_backend": os.getenv("EMBED_BACKEND", "bge-m3"),
        "vector_backend": os.getenv("VECTOR_BACKEND", "faiss"),
        "data_inbox": os.getenv("DATA_INBOX", "/app/data/inbox"),
        "faiss_index_path": os.getenv("FAISS_INDEX_PATH", "/app/data/faiss.index"),
        "zep_api_key": os.getenv("ZEP_API_KEY"),
        "zep_base_url": os.getenv("ZEP_BASE_URL"),
    }

def get_db_connection():
    """Get PostgreSQL database connection (mock for testing)"""
    settings = get_settings()
    # For testing without actual database
    return None

def get_embedder():
    """Get embedding model instance"""
    settings = get_settings()
    backend = settings["embed_backend"]
    
    if backend == "bge-m3":
        from .embed.bge_m3 import BGE_M3Embedder
        return BGE_M3Embedder()
    elif backend == "nomic":
        from .embed.nomic_embed import NomicEmbedder
        return NomicEmbedder()
    else:
        raise ValueError(f"Unknown embedding backend: {backend}")

def get_vector_store():
    """Get vector store instance"""
    settings = get_settings()
    backend = settings["vector_backend"]
    
    if backend == "faiss":
        from .stores.faiss_store import FAISSStore
        return FAISSStore(settings["faiss_index_path"])
    elif backend == "pgvector":
        from .stores.pgvector_store import PgVectorStore
        return PgVectorStore()
    else:
        raise ValueError(f"Unknown vector backend: {backend}")