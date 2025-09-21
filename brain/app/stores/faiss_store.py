import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class FAISSStore:
    """FAISS vector store for similarity search"""
    
    def __init__(self, index_path: str):
        self.index_path = index_path
        self.index = None
        self.metadata = []
        self.embedding_dim = 1024
        
    def _ensure_index(self):
        """Initialize or load FAISS index"""
        if self.index is None:
            if os.path.exists(self.index_path):
                self._load_index()
            else:
                self._create_index()
    
    def _create_index(self):
        """Create new FAISS index"""
        logger.info(f"Creating new FAISS index with dimension {self.embedding_dim}")
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for normalized vectors
        self.metadata = []
        
    def _load_index(self):
        """Load existing FAISS index"""
        try:
            logger.info(f"Loading FAISS index from {self.index_path}")
            self.index = faiss.read_index(self.index_path)
            
            # Load metadata
            metadata_path = self.index_path.replace('.index', '_metadata.pkl')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
            else:
                self.metadata = []
                
            logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            self._create_index()
    
    def _save_index(self):
        """Save FAISS index to disk"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Save index
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata
            metadata_path = self.index_path.replace('.index', '_metadata.pkl')
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
                
            logger.info(f"Saved FAISS index with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
            raise
    
    async def upsert(self, texts: List[str], embeddings: np.ndarray, metadata: List[Dict[str, Any]] = None) -> int:
        """Add or update vectors in the index"""
        self._ensure_index()
        
        if metadata is None:
            metadata = [{"text": text} for text in texts]
        
        # Normalize embeddings for cosine similarity
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Add to index
        start_id = self.index.ntotal
        self.index.add(embeddings.astype(np.float32))
        
        # Add metadata
        for i, meta in enumerate(metadata):
            meta["id"] = start_id + i
            meta["text"] = texts[i]
            self.metadata.append(meta)
        
        # Save to disk
        self._save_index()
        
        return len(texts)
    
    async def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        self._ensure_index()
        
        if self.index.ntotal == 0:
            return []
        
        # Normalize query embedding
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        
        # Search
        scores, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx >= 0 and idx < len(self.metadata):  # Valid index
                result = self.metadata[idx].copy()
                result["score"] = float(score)
                results.append(result)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics"""
        self._ensure_index()
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "embedding_dim": self.embedding_dim,
            "index_path": self.index_path,
            "index_exists": os.path.exists(self.index_path)
        }