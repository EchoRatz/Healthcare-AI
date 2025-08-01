"""Cache management service."""
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from ...domain.entities.CacheEntry import CacheEntry
from ...domain.repositories.CacheRepository import CacheRepository


class CacheManager:
    """Service to manage knowledge cache."""
    
    def __init__(self, cache_repository: CacheRepository):
        self.cache_repository = cache_repository
    
    def add_extracted_information(self, extraction_data: Dict[str, Any]) -> None:
        """Add extracted information to cache."""
        if not extraction_data or not extraction_data.get("facts"):
            return
        
        relevance_score = extraction_data.get("relevance_score", 0)
        
        # Only cache information with decent relevance score
        if relevance_score >= 5:
            for fact in extraction_data["facts"]:
                cache_entry = self._create_cache_entry(fact)
                self.cache_repository.save_cache_entry(cache_entry)
    
    def search_knowledge(self, query: str, top_k: int = 3) -> List[CacheEntry]:
        """Search cached knowledge for relevant facts."""
        return self.cache_repository.search_cache(query, top_k)
    
    def get_cache_summary(self) -> Dict[str, Any]:
        """Get cache statistics and summary."""
        return self.cache_repository.get_cache_stats()
    
    def clear_all_cache(self) -> None:
        """Clear all cached data."""
        self.cache_repository.clear_cache()
    
    def _create_cache_entry(self, fact: Dict[str, Any]) -> CacheEntry:
        """Create cache entry from fact data."""
        # Create unique ID
        fact_hash = hashlib.md5(
            f"{fact['type']}:{fact['key']}:{fact['value']}".encode()
        ).hexdigest()[:8]
        
        return CacheEntry(
            id=fact_hash,
            fact_type=fact["type"],
            key=fact["key"],
            value=fact["value"],
            context=fact.get("context"),
            source_question=fact.get("source_question"),
            timestamp=datetime.now(),
            relevance_score=fact.get("relevance_score", 0.0)
        )