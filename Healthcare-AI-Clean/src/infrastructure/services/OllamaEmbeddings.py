"""Ollama embeddings service."""
from typing import List
from langchain_ollama import OllamaEmbeddings
from ...domain.services.EmbeddingService import EmbeddingService


class OllamaEmbeddingService(EmbeddingService):
    """Ollama implementation of embedding service."""
    
    def __init__(self, model_name: str = "mxbai-embed-large"):
        try:
            self.embeddings = OllamaEmbeddings(model=model_name)
            self._available = True
        except Exception as e:
            print(f"Error initializing Ollama embeddings: {e}")
            self._available = False
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if not self._available:
            return []
        
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            print(f"Error embedding text: {e}")
            return []
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not self._available:
            return []
        
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            print(f"Error embedding documents: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if service is available."""
        return self._available
    
    def get_embeddings_instance(self):
        """Get the underlying embeddings instance."""
        return self.embeddings if self._available else None