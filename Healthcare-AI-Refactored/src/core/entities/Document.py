"""Document entity for Healthcare AI system."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Document:
    """Core document entity."""
    
    id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    source: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def word_count(self) -> int:
        """Get word count of content."""
        return len(self.content.split())
    
    @property
    def is_valid(self) -> bool:
        """Check if document is valid."""
        return bool(self.id and self.content and self.content.strip())
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to document."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)