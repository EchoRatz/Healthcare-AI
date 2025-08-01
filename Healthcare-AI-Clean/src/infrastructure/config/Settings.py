"""Application settings configuration."""
from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Settings:
    """Application settings."""
    
    # Ollama Configuration
    ollama_host: str = os.getenv("OLLAMA_HOST", "localhost")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    ollama_embedding_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "mxbai-embed-large")
    
    # Redis Configuration
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    
    # Database Configuration
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "./data/cache/thai_healthcare_db")
    cache_file_path: str = os.getenv("CACHE_FILE_PATH", "./data/cache/knowledge_cache.json")
    
    # Processing Configuration
    default_batch_size: int = int(os.getenv("DEFAULT_BATCH_SIZE", "5"))
    enable_caching: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    
    # Data paths
    documents_path: str = "data/results_doc"
    input_path: str = "data/input"
    output_path: str = "data/output"
    
    def __post_init__(self):
        """Ensure directories exist."""
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories."""
        directories = [
            os.path.dirname(self.vector_db_path),
            os.path.dirname(self.cache_file_path),
            self.documents_path,
            self.input_path,
            self.output_path
        ]
        
        for directory in directories:
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)


# Global settings instance
settings = Settings()