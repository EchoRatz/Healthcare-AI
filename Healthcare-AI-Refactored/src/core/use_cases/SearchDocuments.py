"""Search documents use case."""

from typing import List, Optional, Tuple
from pathlib import Path

from core.entities.Document import Document
from core.interfaces.VectorStoreInterface import VectorStoreInterface
from shared.logging.LoggerMixin import get_logger


class SearchDocuments:
    """Use case for searching documents."""
    
    def __init__(self, vector_store: VectorStoreInterface, text_processor=None):
        self.vector_store = vector_store
        self.text_processor = text_processor
        self.logger = get_logger(__name__)
    
    def search_by_query(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Search documents by text query."""
        try:
            # Generate query vector (placeholder - would use actual embedding model)
            if self.text_processor:
                query_vector = self.text_processor.generate_embedding(query)
            else:
                # Placeholder vector for testing
                query_vector = [0.0] * 384
            
            if not query_vector:
                self.logger.error("Failed to generate query vector")
                return []
            
            # Search in vector store
            results = self.vector_store.search(query_vector, top_k)
            
            self.logger.debug(f"Found {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def search_by_document_id(self, document_id: str) -> Optional[Document]:
        """Search for a specific document by ID."""
        try:
            # This would typically query the vector store or document repository
            # For now, return None as placeholder
            return None
            
        except Exception as e:
            self.logger.error(f"Document search failed: {e}")
            return None
    
    def search_similar_documents(self, document: Document, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Find documents similar to the given document."""
        try:
            if self.text_processor:
                doc_vector = self.text_processor.generate_embedding(document.content)
            else:
                # Placeholder vector
                doc_vector = [0.0] * 384
            
            if not doc_vector:
                self.logger.error("Failed to generate document vector")
                return []
            
            results = self.vector_store.search(doc_vector, top_k + 1)  # +1 to exclude self
            
            # Filter out the original document
            filtered_results = [(doc, score) for doc, score in results if doc.id != document.id]
            
            return filtered_results[:top_k]
            
        except Exception as e:
            self.logger.error(f"Similar document search failed: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get total number of documents in the store."""
        try:
            return self.vector_store.get_document_count()
        except Exception as e:
            self.logger.error(f"Failed to get document count: {e}")
            return 0