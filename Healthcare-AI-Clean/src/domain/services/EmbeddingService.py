"""Embedding service interface."""
from abc import ABC, abstractmethod
from typing import List


class EmbeddingService(ABC):
    """Interface for document embedding."""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        pass
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if service is available."""
        pass