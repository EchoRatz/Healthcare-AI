"""Knowledge cache entry entity."""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class CacheEntry:
    """Knowledge cache entry."""
    id: str
    fact_type: str
    key: str
    value: str
    context: Optional[str] = None
    source_question: Optional[str] = None
    timestamp: Optional[datetime] = None
    relevance_score: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.fact_type,
            "key": self.key,
            "value": self.value,
            "context": self.context,
            "source_question": self.source_question,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "relevance_score": self.relevance_score
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CacheEntry':
        """Create from dictionary."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])
        
        return cls(
            id=data["id"],
            fact_type=data["type"],
            key=data["key"],
            value=data["value"],
            context=data.get("context"),
            source_question=data.get("source_question"),
            timestamp=timestamp,
            relevance_score=data.get("relevance_score", 0.0)
        )