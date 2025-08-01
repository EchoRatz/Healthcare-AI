#!/usr/bin/env python3
"""
Vector Database for Thai Text Processing

This module provides a clean, efficient vector database implementation
for Thai text storage and semantic search using FAISS and SentenceTransformers.

Author: Healthcare-AI Team
Date: 2025-08-01
Version: 3.0.0
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result from the vector database."""
    
    text: str
    distance: float
    relevance_score: float
    metadata: Optional[Dict[str, Any]] = None
    index: int = -1
    
    def __post_init__(self):
        """Validate and normalize the search result."""
        if self.distance < 0:
            raise ValueError("Distance cannot be negative")
        if not 0 <= self.relevance_score <= 1:
            raise ValueError("Relevance score must be between 0 and 1")


@dataclass 
class DatabaseStats:
    """Database statistics and information."""
    
    total_entries: int
    vector_dimension: int
    index_type: str
    model_name: str
    memory_usage_mb: float = 0.0
    categories: List[str] = field(default_factory=list)


class VectorDatabaseInterface(ABC):
    """Abstract interface for vector databases."""
    
    @abstractmethod
    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a text entry to the database."""
        pass
    
    @abstractmethod
    def search(self, query: str, k: int = 5, **kwargs) -> List[SearchResult]:
        """Search for similar texts."""
        pass
    
    @abstractmethod
    def save(self, filepath: Union[str, Path]) -> bool:
        """Save the database to disk."""
        pass
    
    @abstractmethod
    def load(self, filepath: Union[str, Path]) -> bool:
        """Load the database from disk."""
        pass


class ThaiTextVectorDatabase(VectorDatabaseInterface):
    """
    High-performance vector database optimized for Thai text processing.
    
    Features:
    - Thai language support with multilingual embeddings
    - Efficient FAISS indexing for fast similarity search
    - Persistent storage with JSON metadata
    - Comprehensive error handling and logging
    """
    
    DEFAULT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
    DEFAULT_DIMENSION = 384
    
    def __init__(
        self, 
        vector_dim: int = DEFAULT_DIMENSION,
        model_name: str = DEFAULT_MODEL,
        index_type: str = "L2"
    ):
        """
        Initialize the Thai text vector database.
        
        Args:
            vector_dim: Dimension of the embedding vectors
            model_name: Name of the SentenceTransformer model
            index_type: Type of FAISS index ("L2" or "IP")
        """
        self.vector_dim = vector_dim
        self.model_name = model_name
        self.index_type = index_type
        
        # Initialize FAISS index
        if index_type.upper() == "L2":
            self.index = faiss.IndexFlatL2(vector_dim)
        elif index_type.upper() == "IP":
            self.index = faiss.IndexFlatIP(vector_dim)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
        
        # Data storage
        self.vectors: List[np.ndarray] = []
        self.metadata: List[Dict[str, Any]] = []
        
        # Initialize the embedding model
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Initialized vector database with {vector_dim}D, model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize model {model_name}: {e}")
            raise

    
    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a text entry to the database.
        
        Args:
            text: The text to add
            metadata: Optional metadata associated with the text
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not text or not text.strip():
            logger.warning("Attempted to add empty text")
            return False
        
        try:
            # Generate embedding
            vector = self._encode_text(text)
            
            # Add to FAISS index
            self.index.add(np.array([vector], dtype=np.float32))
            
            # Store vector and metadata
            self.vectors.append(vector)
            self.metadata.append(self._prepare_metadata(text, metadata))
            
            logger.debug(f"Added text entry: {text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add text: {e}")
            return False
    
    def add_texts_from_file(
        self, 
        filepath: Union[str, Path], 
        encoding: str = "utf-8",
        skip_empty: bool = True
    ) -> int:
        """
        Add multiple texts from a file.
        
        Args:
            filepath: Path to the text file
            encoding: File encoding
            skip_empty: Whether to skip empty lines
            
        Returns:
            int: Number of texts successfully added
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return 0
        
        count = 0
        try:
            with open(filepath, "r", encoding=encoding) as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    
                    if skip_empty and not line:
                        continue
                    
                    metadata = {
                        "source_file": str(filepath),
                        "line_number": line_num
                    }
                    
                    if self.add_text(line, metadata):
                        count += 1
            
            logger.info(f"Added {count} texts from {filepath}")
            
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {e}")
        
        return count
    
    def search(
        self, 
        query: str, 
        k: int = 5, 
        distance_threshold: float = 2.0,
        min_relevance: float = 0.0
    ) -> List[SearchResult]:
        """
        Search for similar texts.
        
        Args:
            query: Query text
            k: Number of results to return
            distance_threshold: Maximum distance for results
            min_relevance: Minimum relevance score
            
        Returns:
            List of SearchResult objects
        """
        if self.size() == 0:
            logger.warning("Search called on empty database")
            return []
        
        if not query.strip():
            logger.warning("Empty query provided")
            return []
        
        try:
            # Encode query
            query_vector = self._encode_text(query)
            query_array = np.array([query_vector], dtype=np.float32)
            
            # Search in FAISS index
            distances, indices = self.index.search(query_array, min(k, self.size()))
            
            # Process results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx == -1:  # Invalid index
                    continue
                
                distance = float(distances[0][i])
                
                # Apply distance threshold
                if distance > distance_threshold:
                    continue
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(distance, distance_threshold)
                
                # Apply minimum relevance filter
                if relevance_score < min_relevance:
                    continue
                
                result = SearchResult(
                    text=self.metadata[idx].get("text", ""),
                    distance=distance,
                    relevance_score=relevance_score,
                    metadata=self.metadata[idx],
                    index=idx
                )
                results.append(result)
            
            logger.debug(f"Search for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def size(self) -> int:
        """Return the number of entries in the database."""
        return len(self.vectors)
    
    def save(
        self, 
        index_filepath: Union[str, Path] = "thai_vector_index.faiss",
        metadata_filepath: Union[str, Path] = "thai_metadata.json"
    ) -> bool:
        """
        Save the database to disk.
        
        Args:
            index_filepath: Path for the FAISS index file
            metadata_filepath: Path for the metadata JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            index_path = Path(index_filepath)
            metadata_path = Path(metadata_filepath)
            
            # Create directories if they don't exist
            index_path.parent.mkdir(parents=True, exist_ok=True)
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, str(index_path))
            
            # Save metadata
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump({
                    "metadata": self.metadata,
                    "config": {
                        "vector_dim": self.vector_dim,
                        "model_name": self.model_name,
                        "index_type": self.index_type,
                        "size": self.size()
                    }
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Database saved to {index_path} and {metadata_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save database: {e}")
            return False
    
    def load(
        self,
        index_filepath: Union[str, Path] = "thai_vector_index.faiss",
        metadata_filepath: Union[str, Path] = "thai_metadata.json"
    ) -> bool:
        """
        Load the database from disk.
        
        Args:
            index_filepath: Path to the FAISS index file
            metadata_filepath: Path to the metadata JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            index_path = Path(index_filepath)
            metadata_path = Path(metadata_filepath)
            
            if not index_path.exists() or not metadata_path.exists():
                logger.warning("Database files not found")
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(str(index_path))
            
            # Load metadata
            with open(metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.metadata = data["metadata"]
                
                # Validate configuration
                config = data.get("config", {})
                if config.get("vector_dim") != self.vector_dim:
                    logger.warning("Vector dimension mismatch")
                
                if config.get("model_name") != self.model_name:
                    logger.warning("Model name mismatch")
            
            logger.info(f"Database loaded: {self.size()} entries")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            return False
    
    def get_stats(self) -> DatabaseStats:
        """Get comprehensive database statistics."""
        categories = list(set(
            item.get("category", "unknown") 
            for item in self.metadata
        ))
        
        # Estimate memory usage
        memory_mb = 0.0
        if self.vectors:
            vector_memory = len(self.vectors) * self.vector_dim * 4  # 4 bytes per float32
            metadata_memory = sum(len(str(item)) for item in self.metadata)
            memory_mb = (vector_memory + metadata_memory) / (1024 * 1024)
        
        return DatabaseStats(
            total_entries=self.size(),
            vector_dimension=self.vector_dim,
            index_type=f"FAISS {self.index_type}",
            model_name=self.model_name,
            memory_usage_mb=round(memory_mb, 2),
            categories=categories
        )
    
    def clear(self) -> None:
        """Clear all data from the database."""
        self.vectors.clear()
        self.metadata.clear()
        
        # Recreate FAISS index
        if self.index_type.upper() == "L2":
            self.index = faiss.IndexFlatL2(self.vector_dim)
        else:
            self.index = faiss.IndexFlatIP(self.vector_dim)
        
        logger.info("Database cleared")
    
    def _encode_text(self, text: str) -> np.ndarray:
        """Encode text to vector using the embedding model."""
        return self.model.encode(text, convert_to_numpy=True)
    
    def _prepare_metadata(self, text: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare metadata for storage."""
        base_metadata = {
            "text": text,
            "text_length": len(text),
            "added_at": logger.name  # Placeholder for timestamp
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    def _calculate_relevance_score(self, distance: float, threshold: float) -> float:
        """Calculate relevance score from distance."""
        if distance >= threshold:
            return 0.0
        return max(0.0, 1.0 - (distance / threshold))


def create_thai_vector_database(
    model_name: str = ThaiTextVectorDatabase.DEFAULT_MODEL,
    vector_dim: int = ThaiTextVectorDatabase.DEFAULT_DIMENSION,
    **kwargs
) -> ThaiTextVectorDatabase:
    """
    Factory function to create a Thai vector database.
    
    Args:
        model_name: Name of the embedding model
        vector_dim: Vector dimension
        **kwargs: Additional arguments
        
    Returns:
        ThaiTextVectorDatabase instance
    """
    return ThaiTextVectorDatabase(
        vector_dim=vector_dim,
        model_name=model_name,
        **kwargs
    )


# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Create database
    db = create_thai_vector_database()
    
    # Add sample Thai texts
    thai_texts = [
        "สวัสดีครับ ยินดีที่ได้รู้จัก",
        "วันนี้อากาศดีมาก แสงแดดสวยงาม", 
        "ฉันชอบกินข้าวมันไก่ที่ร้านประจำ",
        "การเรียนรู้เป็นสิ่งสำคัญในชีวิต",
        "เทคโนโลยีช่วยให้ชีวิตสะดวกขึ้น"
    ]
    
    for text in thai_texts:
        db.add_text(text, {"category": "thai_example"})
    
    # Test search
    results = db.search("สวัสดี", k=3)
    
    print("Search Results:")
    for result in results:
        print(f"- {result.text} (relevance: {result.relevance_score:.2f})")
    
    # Print statistics
    stats = db.get_stats()
    print(f"\nDatabase Stats: {stats}")
