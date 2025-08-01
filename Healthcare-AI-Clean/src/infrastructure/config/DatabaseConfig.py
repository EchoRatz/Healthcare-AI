"""Database configuration."""
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    
    # Vector Database
    vector_db_path: str = "./data/cache/thai_healthcare_db"
    vector_collection_name: str = "thai_healthcare"
    vector_search_k: int = 5
    
    # Cache Database
    cache_file_path: str = "./data/cache/knowledge_cache.json"
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_enabled: bool = False
    
    def __post_init__(self):
        """Initialize database directories."""
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create necessary directories."""
        db_dir = os.path.dirname(self.vector_db_path)
        cache_dir = os.path.dirname(self.cache_file_path)
        
        for directory in [db_dir, cache_dir]:
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
    
    def test_redis_connection(self) -> bool:
        """Test Redis connection."""
        try:
            import redis
            client = redis.Redis(
                host=self.redis_host, 
                port=self.redis_port, 
                db=self.redis_db, 
                decode_responses=True
            )
            client.ping()
            return True
        except Exception:
            return False