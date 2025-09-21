from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)

class BGE_M3Embedder:
    """BGE-M3 multilingual embedding model"""
    
    def __init__(self):
        self.model_name = "BAAI/bge-m3"
        self.model = None
        self.embedding_dim = 1024
        
    def _load_model(self):
        """Lazy load the model"""
        if self.model is None:
            try:
                logger.info(f"Loading BGE-M3 model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info("BGE-M3 model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load BGE-M3 model: {e}")
                raise
    
    async def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts into embeddings"""
        try:
            # Convert single string to list
            if isinstance(texts, str):
                texts = [texts]
            
            # For now, return mock embeddings for testing
            # TODO: Implement actual BGE-M3 model loading
            logger.warning("Using mock embeddings for testing")
            batch_size = len(texts)
            mock_embeddings = np.random.rand(batch_size, self.embedding_dim).astype(np.float32)
            
            return mock_embeddings
            
        except Exception as e:
            logger.error(f"BGE-M3 encoding failed: {e}")
            raise
    
    def get_embedding_dim(self) -> int:
        """Get embedding dimension"""
        return self.embedding_dim