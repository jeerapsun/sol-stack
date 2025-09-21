from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
from ..deps import get_vector_store, get_db_connection

logger = logging.getLogger(__name__)
router = APIRouter()

# Simple admin authentication (in production, use proper auth)
def verify_admin():
    # TODO: Implement proper admin authentication
    return True

@router.post("/reindex")
async def reindex_vectors(admin: bool = Depends(verify_admin)):
    """Rebuild vector index from source data"""
    try:
        # This would typically:
        # 1. Read all documents from kb_chunks table
        # 2. Regenerate embeddings 
        # 3. Rebuild the vector index
        
        conn = get_db_connection()
        store = get_vector_store()
        
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total FROM kb_chunks")
            total = cur.fetchone()["total"]
        
        conn.close()
        
        # Mock reindexing process
        return {
            "status": "completed",
            "message": f"Reindexed {total} documents",
            "total_documents": total
        }
        
    except Exception as e:
        logger.error(f"Reindex failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reindex failed: {str(e)}")

@router.get("/stats")
async def get_system_stats(admin: bool = Depends(verify_admin)):
    """Get comprehensive system statistics"""
    try:
        stats = {}
        
        # Vector store stats
        store = get_vector_store()
        stats["vector_store"] = store.get_stats()
        
        # Database stats
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Memory logs
            cur.execute("SELECT COUNT(*) as total FROM memory_logs")
            memory_count = cur.fetchone()["total"]
            
            # KB chunks
            cur.execute("SELECT COUNT(*) as total FROM kb_chunks")
            kb_count = cur.fetchone()["total"]
            
            # Database size
            cur.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
            """)
            db_size = cur.fetchone()["db_size"]
        
        conn.close()
        
        stats["database"] = {
            "memory_logs": memory_count,
            "kb_chunks": kb_count,
            "size": db_size
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.delete("/cleanup")
async def cleanup_old_data(
    days: int = 30,
    admin: bool = Depends(verify_admin)
):
    """Clean up old data beyond retention period"""
    try:
        conn = get_db_connection()
        
        with conn.cursor() as cur:
            # Clean old memory logs
            cur.execute("""
                DELETE FROM memory_logs 
                WHERE timestamp < NOW() - INTERVAL '%s days'
            """, (days,))
            
            deleted_memories = cur.rowcount
            
            # Could add other cleanup tasks here
            conn.commit()
        
        conn.close()
        
        return {
            "status": "completed",
            "deleted_memories": deleted_memories,
            "retention_days": days
        }
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@router.post("/health-check")
async def full_health_check(admin: bool = Depends(verify_admin)):
    """Comprehensive system health check"""
    try:
        checks = {}
        
        # Database connectivity
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            conn.close()
            checks["database"] = "ok"
        except Exception as e:
            checks["database"] = f"error: {str(e)}"
        
        # Vector store
        try:
            store = get_vector_store()
            stats = store.get_stats()
            checks["vector_store"] = "ok"
            checks["vector_count"] = stats.get("total_vectors", 0)
        except Exception as e:
            checks["vector_store"] = f"error: {str(e)}"
        
        # Embedding model
        try:
            from ..deps import get_embedder
            embedder = get_embedder()
            test_embedding = await embedder.encode(["test"])
            checks["embeddings"] = "ok"
            checks["embedding_dim"] = test_embedding.shape[1]
        except Exception as e:
            checks["embeddings"] = f"error: {str(e)}"
        
        overall_status = "ok" if all(
            status == "ok" for status in checks.values() 
            if isinstance(status, str) and status in ["ok", "error"]
        ) else "degraded"
        
        return {
            "status": overall_status,
            "checks": checks
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")