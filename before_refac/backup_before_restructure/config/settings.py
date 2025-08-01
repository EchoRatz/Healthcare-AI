"""
Application Settings
Centralized configuration management.
"""

from config.models import AppConfig


# Default configuration
DEFAULT_CONFIG = AppConfig()

# File paths
DATA_DIR = "data"
LOGS_DIR = "logs"
DEFAULT_TEXT_FILE = "data/sample_data.txt"
DEFAULT_INDEX_FILE = "data/vector_index.faiss"
DEFAULT_METADATA_FILE = "data/metadata.json"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
