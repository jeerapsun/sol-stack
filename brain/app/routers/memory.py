from fastapi import APIRouter, HTTPException
from typing import List
import json
from datetime import datetime
from ..models.schemas import MemoryLogRequest, MemorySearchRequest
from ..deps import get_db_connection, get_embedder
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/log")
async def log_memory(request: MemoryLogRequest):
    """Log conversation to memory database"""
    try:
        conn = get_db_connection()
        
        # Get embedding for the user query
        embedder = get_embedder()
        embedding = await embedder.encode([request.user_query])
        
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO memory_logs (user_query, response, intent, meta, embedding)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                request.user_query,
                request.response,
                request.intent,
                json.dumps(request.meta),
                embedding[0].tolist()  # Convert numpy array to list
            ))
            
            log_id = cur.fetchone()["id"]
            conn.commit()
        
        conn.close()
        
        return {
            "logged": True,
            "id": log_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Memory logging failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to log memory: {str(e)}")

@router.post("/search")
async def search_memory(request: MemorySearchRequest):
    """Search similar memories based on query"""
    try:
        conn = get_db_connection()
        
        # Get embedding for search query
        embedder = get_embedder()
        query_embedding = await embedder.encode([request.query])
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, user_query, response, intent, meta, timestamp,
                       1 - (embedding <=> %s::vector) as similarity
                FROM memory_logs
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (
                query_embedding[0].tolist(),
                query_embedding[0].tolist(),
                request.k
            ))
            
            results = cur.fetchall()
        
        conn.close()
        
        memories = []
        for row in results:
            memories.append({
                "id": row["id"],
                "user_query": row["user_query"],
                "response": row["response"],
                "intent": row["intent"],
                "meta": row["meta"],
                "timestamp": row["timestamp"].isoformat(),
                "similarity": float(row["similarity"])
            })
        
        return {
            "query": request.query,
            "results": memories,
            "count": len(memories)
        }
        
    except Exception as e:
        logger.error(f"Memory search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search memory: {str(e)}")

@router.get("/stats")
async def get_memory_stats():
    """Get memory database statistics"""
    try:
        conn = get_db_connection()
        
        with conn.cursor() as cur:
            # Get total count
            cur.execute("SELECT COUNT(*) as total FROM memory_logs")
            total_logs = cur.fetchone()["total"]
            
            # Get recent activity
            cur.execute("""
                SELECT COUNT(*) as recent
                FROM memory_logs 
                WHERE timestamp > NOW() - INTERVAL '24 hours'
            """)
            recent_logs = cur.fetchone()["recent"]
            
            # Get top intents
            cur.execute("""
                SELECT intent, COUNT(*) as count
                FROM memory_logs
                WHERE intent IS NOT NULL
                GROUP BY intent
                ORDER BY count DESC
                LIMIT 5
            """)
            top_intents = cur.fetchall()
        
        conn.close()
        
        return {
            "total_logs": total_logs,
            "recent_24h": recent_logs,
            "top_intents": [{"intent": row["intent"], "count": row["count"]} for row in top_intents]
        }
        
    except Exception as e:
        logger.error(f"Memory stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get memory stats: {str(e)}")