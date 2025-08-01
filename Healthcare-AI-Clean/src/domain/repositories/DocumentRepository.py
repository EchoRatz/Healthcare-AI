"""Document repository interface."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class DocumentRepository(ABC):
    """Interface for document storage and retrieval."""
    
    @abstractmethod
    def load_documents(self) -> List[Dict[str, Any]]:
        """Load healthcare documents."""
        pass
    
    @abstractmethod
    def setup_vector_store(self) -> None:
        """Setup vector database."""
        pass
    
    @abstractmethod
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search documents by query."""
        pass
    
    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to vector store."""
        pass
    
    @abstractmethod
    def get_document_count(self) -> int:
        """Get total number of documents."""
        pass