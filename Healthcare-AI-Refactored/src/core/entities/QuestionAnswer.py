"""Question-Answer entity."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class QuestionAnswer:
    """Question-Answer pair entity."""
    
    id: str
    question: str
    answer: str
    confidence: float
    processing_time: float
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if answer has high confidence."""
        return self.confidence >= 0.8
    
    @property
    def is_fast_response(self) -> bool:
        """Check if response was fast."""
        return self.processing_time <= 2.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'confidence': self.confidence,
            'processing_time': self.processing_time,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }