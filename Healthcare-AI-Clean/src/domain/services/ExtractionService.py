"""Information extraction service interface."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..entities.CacheEntry import CacheEntry


class ExtractionService(ABC):
    """Interface for information extraction."""
    
    @abstractmethod
    def extract_information(self, question: str, answer: str) -> Optional[Dict[str, Any]]:
        """Extract key information from question-answer pair."""
        pass
    
    @abstractmethod
    def parse_extraction_result(self, result: str) -> Optional[Dict[str, Any]]:
        """Parse extraction result."""
        pass
    
    @abstractmethod
    def create_cache_entries(self, extraction_data: Dict[str, Any]) -> List[CacheEntry]:
        """Create cache entries from extraction data."""
        pass