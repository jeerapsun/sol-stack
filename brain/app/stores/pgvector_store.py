import numpy as np
from typing import List, Dict, Any
import json
import logging
from ..deps import get_db_connection

logger = logging.getLogger(__name__)

class PgVectorStore:
    """PostgreSQL + pgvector store for similarity search"""
    
    def __init__(self):
        self.embedding_dim = 1024
        
    async def upsert(self, texts: List[str], embeddings: np.ndarray, metadata: List[Dict[str, Any]] = None) -> int:
        """Add or update vectors in PostgreSQL"""
        if metadata is None:
            metadata = [{"text": text} for text in texts]
        
        try:
            conn = get_db_connection()
            
            with conn.cursor() as cur:
                count = 0
                for i, (text, embedding, meta) in enumerate(zip(texts, embeddings, metadata)):
                    # Check if document already exists (based on source + chunk_index)
                    source = meta.get("source", f"text_{i}")
                    chunk_index = meta.get("chunk_index", 0)
                    
                    cur.execute("""
                        SELECT id FROM kb_chunks 
                        WHERE source = %s AND chunk_index = %s
                    """, (source, chunk_index))
                    
                    existing = cur.fetchone()
                    
                    if existing:
                        # Update existing
                        cur.execute("""
                            UPDATE kb_chunks 
                            SET content = %s, metadata = %s, embedding = %s
                            WHERE id = %s
                        """, (
                            text,
                            json.dumps(meta),
                            embedding.tolist(),
                            existing["id"]
                        ))
                    else:
                        # Insert new
                        cur.execute("""
                            INSERT INTO kb_chunks (content, source, chunk_index, metadata, embedding)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            text,
                            source,
                            chunk_index,
                            json.dumps(meta),
                            embedding.tolist()
                        ))
                    
                    count += 1
                
                conn.commit()
            
            conn.close()
            return count
            
        except Exception as e:
            logger.error(f"PgVector upsert failed: {e}")
            raise
    
    async def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors using cosine similarity"""
        try:
            conn = get_db_connection()
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, content, source, chunk_index, metadata,
                           1 - (embedding <=> %s::vector) as similarity
                    FROM kb_chunks
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (
                    query_embedding.tolist(),
                    query_embedding.tolist(),
                    k
                ))
                
                rows = cur.fetchall()
            
            conn.close()
            
            results = []
            for row in rows:
                result = {
                    "id": row["id"],
                    "text": row["content"],
                    "source": row["source"],
                    "chunk_index": row["chunk_index"],
                    "metadata": row["metadata"],
                    "score": float(row["similarity"])
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"PgVector search failed: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics"""
        try:
            conn = get_db_connection()
            
            with conn.cursor() as cur:
                # Total count
                cur.execute("SELECT COUNT(*) as total FROM kb_chunks")
                total = cur.fetchone()["total"]
                
                # Source breakdown
                cur.execute("""
                    SELECT source, COUNT(*) as count
                    FROM kb_chunks
                    GROUP BY source
                    ORDER BY count DESC
                    LIMIT 10
                """)
                sources = cur.fetchall()
                
                # Recent additions
                cur.execute("""
                    SELECT COUNT(*) as recent
                    FROM kb_chunks
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                """)
                recent = cur.fetchone()["recent"]
            
            conn.close()
            
            return {
                "total_vectors": total,
                "embedding_dim": self.embedding_dim,
                "recent_24h": recent,
                "top_sources": [{"source": row["source"], "count": row["count"]} for row in sources]
            }
            
        except Exception as e:
            logger.error(f"PgVector stats failed: {e}")
            return {
                "total_vectors": 0,
                "embedding_dim": self.embedding_dim,
                "error": str(e)
            }