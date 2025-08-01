"""Search result entity."""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class SearchResult:
    """Search result entity."""
    
    document_id: str
    content: str
    score: float
    distance: float
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate search result."""
        if self.score < 0 or self.score > 1:
            raise ValueError("Score must be between 0 and 1")
        if self.distance < 0:
            raise ValueError("Distance cannot be negative")
    
    @property
    def relevance_percentage(self) -> float:
        """Get relevance as percentage."""
        return self.score * 100
    
    @property
    def is_highly_relevant(self) -> bool:
        """Check if result is highly relevant."""
        return self.score >= 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'document_id': self.document_id,
            'content': self.content,
            'score': self.score,
            'distance': self.distance,
            'metadata': self.metadata or {}
        }