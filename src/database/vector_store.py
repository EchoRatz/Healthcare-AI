"""
Vector Store Module - Handles vector storage and indexing operations.
Small, focused class that only deals with vectors.
"""

import faiss
import numpy as np
from typing import List, Optional
import logging

from utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Handles vector storage and FAISS indexing operations."""
    
    def __init__(self, dimension: int = 384, index_type: str = "L2"):
        """Initialize vector store with specified dimension."""
        self.dimension = dimension
        self.index_type = index_type
        
        # Create FAISS index
        if index_type.upper() == "L2":
            self.index = faiss.IndexFlatL2(dimension)
        elif index_type.upper() == "IP":
            self.index = faiss.IndexFlatIP(dimension)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
        
        logger.info(f"Initialized vector store: {dimension}D, {index_type}")
    
    def add_vectors(self, vectors: np.ndarray) -> bool:
        """Add vectors to the index."""
        try:
            if len(vectors.shape) == 1:
                vectors = vectors.reshape(1, -1)
            
            if vectors.shape[1] != self.dimension:
                raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {vectors.shape[1]}")
            
            self.index.add(vectors.astype(np.float32))
            logger.debug(f"Added {len(vectors)} vectors to store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vectors: {e}")
            return False
    
    def search_vectors(self, query_vector: np.ndarray, k: int = 5) -> tuple:
        """Search for similar vectors."""
        try:
            if len(query_vector.shape) == 1:
                query_vector = query_vector.reshape(1, -1)
            
            distances, indices = self.index.search(query_vector.astype(np.float32), k)
            return distances[0], indices[0]
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return np.array([]), np.array([])
    
    def size(self) -> int:
        """Get number of vectors in store."""
        return self.index.ntotal
    
    def save(self, filepath: str) -> bool:
        """Save index to file."""
        try:
            faiss.write_index(self.index, filepath)
            logger.info(f"Saved vector index to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            return False
    
    def load(self, filepath: str) -> bool:
        """Load index from file."""
        try:
            self.index = faiss.read_index(filepath)
            logger.info(f"Loaded vector index from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
