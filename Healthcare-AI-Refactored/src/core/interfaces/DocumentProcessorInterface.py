"""Document processor interface."""

from abc import ABC, abstractmethod
from typing import List
from ..entities.Document import Document


class DocumentProcessorInterface(ABC):
    """Abstract interface for document processing."""
    
    @abstractmethod
    def process_text(self, text: str) -> List[str]:
        """Process text into chunks."""
        pass
    
    @abstractmethod
    def process_document(self, document: Document) -> List[Document]:
        """Process document into smaller documents."""
        pass
    
    @abstractmethod
    def extract_metadata(self, text: str) -> dict:
        """Extract metadata from text."""
        pass
    
    @abstractmethod
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        pass