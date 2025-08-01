"""
Data Models and Schemas
Small, focused data classes.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class SearchResult:
    """Search result data model."""
    text: str
    distance: float
    relevance_score: float
    metadata: Optional[Dict[str, Any]] = None
    index: int = -1
    
    def __post_init__(self):
        """Validate search result."""
        if self.distance < 0:
            raise ValueError("Distance cannot be negative")
        if not 0 <= self.relevance_score <= 1:
            raise ValueError("Relevance score must be between 0 and 1")


@dataclass
class AppConfig:
    """Application configuration."""
    vector_dimension: int = 384
    default_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    default_top_k: int = 5
    min_relevance_threshold: float = 0.3
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
