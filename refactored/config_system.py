#!/usr/bin/env python3
"""
Configuration Management System

Centralized configuration management for the Healthcare-AI system
with support for multiple configuration sources and validation.

Author: Healthcare-AI Team
Date: 2025-08-01
Version: 3.0.0
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ConfigSource(Enum):
    """Configuration source types."""
    DEFAULT = "default"
    FILE = "file"
    ENVIRONMENT = "environment"
    COMMAND_LINE = "command_line"


@dataclass
class VectorDatabaseConfig:
    """Vector database configuration."""
    
    model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    vector_dimension: int = 384
    index_type: str = "L2"
    index_file: str = "thai_vector_index.faiss"
    metadata_file: str = "thai_metadata.json"
    auto_save: bool = True
    save_interval: int = 100  # Save every N additions


@dataclass
class LLMConfig:
    """LLM client configuration."""
    
    client_type: str = "mock"
    model: str = "llama3"
    base_url: str = "http://localhost:11434"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 500
    timeout: int = 60
    
    # Thai-specific settings
    use_thai_optimization: bool = True
    thai_prompt_prefix: str = "ตอบเป็นภาษาไทย: "


@dataclass
class RAGConfig:
    """RAG system configuration."""
    
    default_top_k: int = 5
    min_relevance_threshold: float = 0.3
    distance_threshold: float = 2.0
    max_context_length: int = 2000
    context_overlap: int = 100
    
    # Prompt templates
    default_prompt_template: str = """ใช้ข้อมูลที่ให้มาด้านล่างเพื่อตอบคำถาม:

คำถาม: {query}

ข้อมูลอ้างอิง:
{context}

คำตอบ:"""
    
    no_context_template: str = """คำถาม: {query}

ไม่พบข้อมูลที่เกี่ยวข้องในฐานข้อมูล กรุณาตอบตามความรู้ทั่วไปของคุณ:"""


@dataclass
class DataProcessingConfig:
    """Data processing configuration."""
    
    chunk_size: int = 500
    chunk_overlap: int = 50
    clean_text: bool = True
    aggressive_cleaning: bool = False
    respect_sentences: bool = True
    auto_detect_encoding: bool = True
    supported_languages: List[str] = field(default_factory=lambda: ["thai", "english"])


@dataclass
class LoggingConfig:
    """Logging configuration."""
    
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = "healthcare_ai.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True


@dataclass
class ApplicationConfig:
    """Main application configuration."""
    
    # Component configurations
    vector_db: VectorDatabaseConfig = field(default_factory=VectorDatabaseConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    data_processing: DataProcessingConfig = field(default_factory=DataProcessingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Application settings
    app_name: str = "Healthcare-AI System"
    version: str = "3.0.0"
    debug: bool = False
    data_directory: str = "data"
    cache_directory: str = "cache"
    
    # Feature flags
    enable_web_search: bool = False
    enable_personal_question_filter: bool = True
    enable_thai_optimization: bool = True
    enable_batch_processing: bool = True


class ConfigurationManager:
    """
    Centralized configuration management system.
    
    Supports loading configuration from multiple sources with priority:
    1. Command line arguments (highest priority)
    2. Environment variables
    3. Configuration files
    4. Default values (lowest priority)
    """
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = Path(config_file) if config_file else None
        self._config = ApplicationConfig()
        self._config_sources: Dict[str, ConfigSource] = {}
        
        logger.info("Configuration manager initialized")
    
    def load_config(self) -> ApplicationConfig:
        """
        Load configuration from all sources.
        
        Returns:
            Loaded and merged configuration
        """
        # Start with defaults
        self._config = ApplicationConfig()
        
        # Load from file if specified
        if self.config_file and self.config_file.exists():
            self._load_from_file()
        
        # Override with environment variables
        self._load_from_environment()
        
        # Validate configuration
        self._validate_config()
        
        logger.info("Configuration loaded successfully")
        return self._config
    
    def save_config(self, file_path: Optional[Union[str, Path]] = None) -> bool:
        """
        Save current configuration to file.
        
        Args:
            file_path: Optional path to save to (defaults to current config file)
            
        Returns:
            True if successful, False otherwise
        """
        save_path = Path(file_path) if file_path else self.config_file
        
        if not save_path:
            logger.error("No save path specified")
            return False
        
        try:
            # Create directory if it doesn't exist
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert config to dictionary
            config_dict = asdict(self._config)
            
            # Save as JSON
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get_config(self) -> ApplicationConfig:
        """Get current configuration."""
        return self._config
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of configuration updates
        """
        self._apply_updates(self._config, updates)
        self._validate_config()
        logger.info("Configuration updated")
    
    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the value (e.g., "llm.temperature")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            value = self._config
            for key in key_path.split('.'):
                value = getattr(value, key)
            return value
        except (AttributeError, KeyError):
            return default
    
    def set_config_value(self, key_path: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the value
            value: New value to set
        """
        keys = key_path.split('.')
        config_obj = self._config
        
        # Navigate to the parent object
        for key in keys[:-1]:
            config_obj = getattr(config_obj, key)
        
        # Set the final value
        setattr(config_obj, keys[-1], value)
        logger.debug(f"Set {key_path} = {value}")
    
    def _load_from_file(self) -> None:
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            self._apply_updates(self._config, file_config)
            logger.info(f"Configuration loaded from {self.config_file}")
            
        except Exception as e:
            logger.warning(f"Failed to load config file {self.config_file}: {e}")
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            # Vector DB settings
            'HEALTHCARE_AI_VECTOR_MODEL': 'vector_db.model_name',
            'HEALTHCARE_AI_VECTOR_DIM': 'vector_db.vector_dimension',
            
            # LLM settings
            'HEALTHCARE_AI_LLM_TYPE': 'llm.client_type',
            'HEALTHCARE_AI_LLM_MODEL': 'llm.model',
            'HEALTHCARE_AI_LLM_BASE_URL': 'llm.base_url',
            'HEALTHCARE_AI_API_KEY': 'llm.api_key',
            'HEALTHCARE_AI_LLM_TEMPERATURE': 'llm.temperature',
            'HEALTHCARE_AI_LLM_MAX_TOKENS': 'llm.max_tokens',
            
            # RAG settings
            'HEALTHCARE_AI_TOP_K': 'rag.default_top_k',
            'HEALTHCARE_AI_MIN_RELEVANCE': 'rag.min_relevance_threshold',
            'HEALTHCARE_AI_CONTEXT_LENGTH': 'rag.max_context_length',
            
            # Application settings
            'HEALTHCARE_AI_DEBUG': 'debug',
            'HEALTHCARE_AI_DATA_DIR': 'data_directory',
            'HEALTHCARE_AI_LOG_LEVEL': 'logging.level'
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Type conversion
                value = self._convert_env_value(env_value)
                self.set_config_value(config_path, value)
                self._config_sources[config_path] = ConfigSource.ENVIRONMENT
                logger.debug(f"Set {config_path} from environment: {env_var}")
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer conversion
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float conversion
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _apply_updates(self, config_obj: Any, updates: Dict[str, Any]) -> None:
        """Recursively apply updates to configuration object."""
        for key, value in updates.items():
            if hasattr(config_obj, key):
                current_value = getattr(config_obj, key)
                
                if isinstance(current_value, (VectorDatabaseConfig, LLMConfig, RAGConfig, 
                                            DataProcessingConfig, LoggingConfig)):
                    # Recursively update nested config objects
                    if isinstance(value, dict):
                        self._apply_updates(current_value, value)
                    else:
                        setattr(config_obj, key, value)
                else:
                    setattr(config_obj, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        # Vector DB validation
        if self._config.vector_db.vector_dimension <= 0:
            raise ValueError("Vector dimension must be positive")
        
        # LLM validation
        if self._config.llm.temperature < 0 or self._config.llm.temperature > 2:
            logger.warning("LLM temperature outside recommended range (0-2)")
        
        if self._config.llm.max_tokens <= 0:
            raise ValueError("Max tokens must be positive")
        
        # RAG validation
        if self._config.rag.default_top_k <= 0:
            raise ValueError("Top K must be positive")
        
        if not 0 <= self._config.rag.min_relevance_threshold <= 1:
            raise ValueError("Min relevance threshold must be between 0 and 1")
        
        # Data processing validation
        if self._config.data_processing.chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        
        logger.debug("Configuration validation passed")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary."""
        return {
            "app_name": self._config.app_name,
            "version": self._config.version,
            "debug": self._config.debug,
            "vector_db": {
                "model": self._config.vector_db.model_name,
                "dimension": self._config.vector_db.vector_dimension
            },
            "llm": {
                "type": self._config.llm.client_type,
                "model": self._config.llm.model
            },
            "rag": {
                "top_k": self._config.rag.default_top_k,
                "relevance_threshold": self._config.rag.min_relevance_threshold
            }
        }


def create_default_config() -> ApplicationConfig:
    """Create default configuration."""
    return ApplicationConfig()


def load_config_from_file(file_path: Union[str, Path]) -> ApplicationConfig:
    """
    Load configuration from file.
    
    Args:
        file_path: Path to configuration file
        
    Returns:
        Loaded configuration
    """
    manager = ConfigurationManager(file_path)
    return manager.load_config()


# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)
    
    print("⚙️ Configuration Management System Test")
    print("=" * 50)
    
    # Create configuration manager
    config_manager = ConfigurationManager()
    
    # Load default configuration
    config = config_manager.load_config()
    
    print("\n📋 Default Configuration Summary:")
    summary = config_manager.get_summary()
    for section, values in summary.items():
        if isinstance(values, dict):
            print(f"  {section}:")
            for key, value in values.items():
                print(f"    {key}: {value}")
        else:
            print(f"  {section}: {values}")
    
    # Test configuration updates
    print("\n🔧 Testing configuration updates...")
    updates = {
        "llm": {
            "client_type": "ollama",
            "temperature": 0.8
        },
        "rag": {
            "default_top_k": 10
        }
    }
    
    config_manager.update_config(updates)
    
    # Test dot notation access
    print(f"\n🔍 LLM Temperature: {config_manager.get_config_value('llm.temperature')}")
    print(f"🔍 RAG Top K: {config_manager.get_config_value('rag.default_top_k')}")
    
    # Test saving configuration
    test_config_file = Path("test_config.json")
    if config_manager.save_config(test_config_file):
        print(f"✅ Configuration saved to {test_config_file}")
        
        # Clean up
        test_config_file.unlink()
        print("🧹 Test file cleaned up")
    
    print("\n✅ Configuration system test completed")
