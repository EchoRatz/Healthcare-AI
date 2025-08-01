"""Vector store interface."""

from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np


class VectorStoreInterface(ABC):
    """Abstract interface for vector storage operations."""
    
    @abstractmethod
    def add_vectors(self, vectors: np.ndarray, ids: List[str]) -> bool:
        """Add vectors to the store."""
        pass
    
    @abstractmethod
    def search_vectors(self, query_vector: np.ndarray, k: int = 5) -> Tuple[List[float], List[int]]:
        """Search for similar vectors."""
        pass
    
    @abstractmethod
    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector by ID."""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get number of vectors in store."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all vectors."""
        pass
    
    @abstractmethod
    def save(self, filepath: str) -> bool:
        """Save index to file."""
        pass
    
    @abstractmethod
    def load(self, filepath: str) -> bool:
        """Load index from file."""
        pass