"""Redis-based cache implementation."""
import json
import redis
from typing import List, Dict, Any
from datetime import datetime
from ...domain.entities.CacheEntry import CacheEntry
from ...domain.repositories.CacheRepository import CacheRepository


class RedisCacheRepository(CacheRepository):
    """Redis implementation of cache repository."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        try:
            self.redis_client = redis.Redis(
                host=host, port=port, db=db, decode_responses=True
            )
            self.redis_client.ping()  # Test connection
            self.cache_key = "healthcare_cache"
        except redis.ConnectionError:
            raise ConnectionError("Unable to connect to Redis")
    
    def save_cache_entry(self, entry: CacheEntry) -> None:
        """Save a cache entry."""
        try:
            # Store each entry with unique key
            entry_key = f"{self.cache_key}:entry:{entry.id}"
            self.redis_client.hset(entry_key, mapping=entry.to_dict())
            
            # Add to index
            self.redis_client.sadd(f"{self.cache_key}:index", entry.id)
            
        except Exception as e:
            print(f"Error saving to Redis: {e}")
    
    def load_cache_entries(self) -> List[CacheEntry]:
        """Load all cache entries."""
        try:
            entry_ids = self.redis_client.smembers(f"{self.cache_key}:index")
            entries = []
            
            for entry_id in entry_ids:
                entry_key = f"{self.cache_key}:entry:{entry_id}"
                entry_data = self.redis_client.hgetall(entry_key)
                
                if entry_data:
                    entry = CacheEntry.from_dict(entry_data)
                    entries.append(entry)
            
            return entries
            
        except Exception as e:
            print(f"Error loading from Redis: {e}")
            return []
    
    def search_cache(self, query: str, top_k: int = 3) -> List[CacheEntry]:
        """Search cache entries."""
        entries = self.load_cache_entries()
        relevant_entries = []
        query_lower = query.lower()
        
        for entry in entries:
            score = 0
            text_to_search = f"{entry.key} {entry.value} {entry.context or ''}".lower()
            
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 2 and word in text_to_search:
                    score += 1
            
            if score > 0:
                relevant_entries.append((entry, score))
        
        relevant_entries.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, _ in relevant_entries[:top_k]]
    
    def clear_cache(self) -> None:
        """Clear all cache entries."""
        try:
            # Get all entry IDs
            entry_ids = self.redis_client.smembers(f"{self.cache_key}:index")
            
            # Delete all entries
            for entry_id in entry_ids:
                entry_key = f"{self.cache_key}:entry:{entry_id}"
                self.redis_client.delete(entry_key)
            
            # Clear index
            self.redis_client.delete(f"{self.cache_key}:index")
            
        except Exception as e:
            print(f"Error clearing Redis cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            entry_count = self.redis_client.scard(f"{self.cache_key}:index")
            
            return {
                "total_entries": entry_count,
                "storage_type": "Redis",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting Redis stats: {e}")
            return {"total_entries": 0, "storage_type": "Redis", "error": str(e)}