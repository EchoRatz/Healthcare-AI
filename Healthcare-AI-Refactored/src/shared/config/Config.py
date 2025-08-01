"""Application configuration."""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import os
import json
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration."""
    vector_dimension: int = 384
    index_type: str = "L2"
    storage_path: str = "data/vectors"
    

@dataclass
class LLMConfig:
    """LLM configuration."""
    provider: str = "ollama"
    model_name: str = "llama2"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 1000


@dataclass
class ProcessingConfig:
    """Processing configuration."""
    csv_input_dir: str = "data/csv_input"
    csv_processed_dir: str = "data/csv_processed"
    csv_error_dir: str = "data/csv_errors"
    polling_interval: float = 1.0
    batch_size: int = 100


@dataclass
class AppConfig:
    """Main application configuration."""
    database: DatabaseConfig
    llm: LLMConfig
    processing: ProcessingConfig
    log_level: str = "INFO"
    
    @classmethod
    def from_file(cls, config_path: str) -> 'AppConfig':
        """Load configuration from file."""
        config_file = Path(config_path)
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        else:
            config_data = {}
        
        # Apply environment variable overrides
        config_data = cls._apply_env_overrides(config_data)
        
        return cls(
            database=DatabaseConfig(**config_data.get('database', {})),
            llm=LLMConfig(**config_data.get('llm', {})),
            processing=ProcessingConfig(**config_data.get('processing', {})),
            log_level=config_data.get('log_level', 'INFO')
        )
    
    @staticmethod
    def _apply_env_overrides(config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides."""
        # Override LLM settings from environment
        if 'OLLAMA_BASE_URL' in os.environ:
            config_data.setdefault('llm', {})['base_url'] = os.environ['OLLAMA_BASE_URL']
        
        if 'OLLAMA_MODEL' in os.environ:
            config_data.setdefault('llm', {})['model_name'] = os.environ['OLLAMA_MODEL']
        
        if 'LOG_LEVEL' in os.environ:
            config_data['log_level'] = os.environ['LOG_LEVEL']
        
        return config_data
    
    def save_to_file(self, config_path: str):
        """Save configuration to file."""
        config_data = {
            'database': {
                'vector_dimension': self.database.vector_dimension,
                'index_type': self.database.index_type,
                'storage_path': self.database.storage_path
            },
            'llm': {
                'provider': self.llm.provider,
                'model_name': self.llm.model_name,
                'base_url': self.llm.base_url,
                'temperature': self.llm.temperature,
                'max_tokens': self.llm.max_tokens
            },
            'processing': {
                'csv_input_dir': self.processing.csv_input_dir,
                'csv_processed_dir': self.processing.csv_processed_dir,
                'csv_error_dir': self.processing.csv_error_dir,
                'polling_interval': self.processing.polling_interval,
                'batch_size': self.processing.batch_size
            },
            'log_level': self.log_level
        }
        
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)