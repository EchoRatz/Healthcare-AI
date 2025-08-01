"""JSON file-based cache implementation."""
import json
import os
from typing import List, Dict, Any
from datetime import datetime
from ...domain.entities.CacheEntry import CacheEntry
from ...domain.repositories.CacheRepository import CacheRepository


class JsonCacheRepository(CacheRepository):
    """JSON file implementation of cache repository."""
    
    def __init__(self, cache_file: str = "./data/cache/knowledge_cache.json"):
        self.cache_file = cache_file
        self._ensure_cache_directory()
    
    def save_cache_entry(self, entry: CacheEntry) -> None:
        """Save a cache entry."""
        entries = self.load_cache_entries()
        
        # Check if entry already exists
        existing_ids = {e.id for e in entries}
        if entry.id not in existing_ids:
            entries.append(entry)
            self._save_entries(entries)
    
    def load_cache_entries(self) -> List[CacheEntry]:
        """Load all cache entries."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                entries = []
                for fact_data in data.get("facts", []):
                    entry = CacheEntry.from_dict(fact_data)
                    entries.append(entry)
                
                return entries
        
        except Exception as e:
            print(f"⚠️ Error loading cache: {e}")
        
        return []
    
    def search_cache(self, query: str, top_k: int = 3) -> List[CacheEntry]:
        """Search cache entries."""
        entries = self.load_cache_entries()
        relevant_entries = []
        query_lower = query.lower()
        
        for entry in entries:
            # Simple relevance scoring
            score = 0
            text_to_search = f"{entry.key} {entry.value} {entry.context or ''}".lower()
            
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 2 and word in text_to_search:
                    score += 1
            
            if score > 0:
                # Add search score to entry
                entry_dict = entry.to_dict()
                entry_dict["search_score"] = score
                relevant_entries.append((entry, score))
        
        # Sort by relevance score
        relevant_entries.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, _ in relevant_entries[:top_k]]
    
    def clear_cache(self) -> None:
        """Clear all cache entries."""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
        except Exception as e:
            print(f"Error clearing cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        entries = self.load_cache_entries()
        
        stats = {
            "total_entries": len(entries),
            "types": {},
            "last_updated": None
        }
        
        for entry in entries:
            # Count by type
            entry_type = entry.fact_type
            stats["types"][entry_type] = stats["types"].get(entry_type, 0) + 1
            
            # Find latest timestamp
            if entry.timestamp:
                if not stats["last_updated"] or entry.timestamp > stats["last_updated"]:
                    stats["last_updated"] = entry.timestamp
        
        return stats
    
    def _save_entries(self, entries: List[CacheEntry]) -> None:
        """Save entries to file."""
        try:
            cache_data = {
                "facts": [entry.to_dict() for entry in entries],
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _ensure_cache_directory(self) -> None:
        """Ensure cache directory exists."""
        cache_dir = os.path.dirname(self.cache_file)
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)