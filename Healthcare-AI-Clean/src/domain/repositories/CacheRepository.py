"""Cache repository interface."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..entities.CacheEntry import CacheEntry


class CacheRepository(ABC):
    """Interface for cache storage."""
    
    @abstractmethod
    def save_cache_entry(self, entry: CacheEntry) -> None:
        """Save a cache entry."""
        pass
    
    @abstractmethod
    def load_cache_entries(self) -> List[CacheEntry]:
        """Load all cache entries."""
        pass
    
    @abstractmethod
    def search_cache(self, query: str, top_k: int = 3) -> List[CacheEntry]:
        """Search cache entries."""
        pass
    
    @abstractmethod
    def clear_cache(self) -> None:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass