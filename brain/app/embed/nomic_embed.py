from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)

class NomicEmbedder:
    """Nomic Embed Text model for fast embeddings"""
    
    def __init__(self):
        self.model_name = "nomic-ai/nomic-embed-text-v1"
        self.model = None
        self.embedding_dim = 768  # Nomic embed dimension
        
    def _load_model(self):
        """Lazy load the model"""
        if self.model is None:
            try:
                logger.info(f"Loading Nomic Embed model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name, trust_remote_code=True)
                logger.info("Nomic Embed model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Nomic Embed model: {e}")
                raise
    
    async def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts into embeddings"""
        try:
            # Convert single string to list
            if isinstance(texts, str):
                texts = [texts]
            
            # For now, return mock embeddings for testing
            # TODO: Implement actual Nomic model loading
            logger.warning("Using mock embeddings for testing")
            batch_size = len(texts)
            mock_embeddings = np.random.rand(batch_size, 768).astype(np.float32)
            
            # Pad to 1024 dimensions to match schema
            if mock_embeddings.shape[1] < 1024:
                padding = np.zeros((mock_embeddings.shape[0], 1024 - mock_embeddings.shape[1]))
                mock_embeddings = np.concatenate([mock_embeddings, padding], axis=1)
            
            return mock_embeddings
            
        except Exception as e:
            logger.error(f"Nomic embedding failed: {e}")
            raise
    
    def get_embedding_dim(self) -> int:
        """Get embedding dimension (padded to 1024)"""
        return 1024