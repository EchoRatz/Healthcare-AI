"""
Search Engine Module - Handles search logic and result processing.
Small, focused class that coordinates search operations.
"""

from typing import List, Optional, Dict, Any
import numpy as np

from config.models import SearchResult
from database.vector_store import VectorStore
from database.text_processor import TextProcessor
from utils.logger import get_logger

logger = get_logger(__name__)


class SearchEngine:
    """Handles search operations and result processing."""
    
    def __init__(self, vector_store: VectorStore, text_processor: TextProcessor):
        """Initialize search engine with vector store and text processor."""
        self.vector_store = vector_store
        self.text_processor = text_processor
        
        logger.info("Initialized search engine")
    
    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add text to the search index."""
        try:
            # Process text
            processed_text = self.text_processor.preprocess_text(text)
            
            # Generate embedding
            embedding = self.text_processor.encode_text(processed_text)
            
            # Add to vector store with text and metadata
            success = self.vector_store.add_vectors(
                embedding.reshape(1, -1), 
                texts=[processed_text], 
                metadata=[metadata or {}]
            )
            
            if success:
                logger.debug(f"Added text to search index: {text[:50]}...")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to add text to search index: {e}")
            return False
    
    def add_texts_from_list(self, texts: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None) -> int:
        """Add multiple texts from list with optional metadata."""
        count = 0
        
        # Ensure metadata_list has the same length as texts
        if metadata_list is None:
            metadata_list = [{}] * len(texts)
        elif len(metadata_list) != len(texts):
            # Pad with empty dicts if metadata_list is shorter
            metadata_list.extend([{}] * (len(texts) - len(metadata_list)))
        
        for i, text in enumerate(texts):
            if self.add_text(text, metadata_list[i]):
                count += 1
        
        logger.info(f"Added {count}/{len(texts)} texts to search index")
        return count
    
    def search(self, query: str, k: int = 5, min_relevance: float = 0.0) -> List[SearchResult]:
        """Search for similar texts."""
        try:
            if not query.strip():
                logger.warning("Empty query provided")
                return []
            
            if self.vector_store.size() == 0:
                logger.warning("No texts in search index")
                return []
            
            # Generate query embedding
            query_embedding = self.text_processor.encode_text(query)
            
            # Search vectors
            distances, indices = self.vector_store.search_vectors(query_embedding, k)
            
            # Process results
            results = []
            for i, (distance, idx) in enumerate(zip(distances, indices)):
                if idx >= self.vector_store.size():
                    continue
                
                # Convert distance to relevance score
                relevance_score = max(0.0, 1.0 - distance / 2.0)  # Simple conversion
                
                if relevance_score >= min_relevance:
                    result = SearchResult(
                        text=self.vector_store.get_text(idx),
                        distance=float(distance),
                        relevance_score=relevance_score,
                        metadata=self.vector_store.get_metadata(idx),
                        index=int(idx)
                    )
                    results.append(result)
            
            logger.debug(f"Search returned {len(results)} results for query: {query[:30]}...")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def size(self) -> int:
        """Get number of texts in index."""
        return self.vector_store.size()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics."""
        return {
            "total_texts": self.vector_store.size(),
            "vector_dimension": self.text_processor.get_dimension(),
            "index_size": self.vector_store.size()
        }