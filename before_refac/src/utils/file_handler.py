"""
File Handler Utility - File operations.
"""

from pathlib import Path
from typing import List, Optional
import json

from utils.logger import get_logger

logger = get_logger(__name__)


class FileHandler:
    """Handles file operations."""
    
    @staticmethod
    def read_text_file(filepath: str, encoding: str = "utf-8") -> Optional[str]:
        """Read text file."""
        try:
            return Path(filepath).read_text(encoding=encoding)
        except Exception as e:
            logger.error(f"Failed to read {filepath}: {e}")
            return None
    
    @staticmethod
    def write_text_file(filepath: str, content: str, encoding: str = "utf-8") -> bool:
        """Write text file."""
        try:
            Path(filepath).write_text(content, encoding=encoding)
            return True
        except Exception as e:
            logger.error(f"Failed to write {filepath}: {e}")
            return False
    
    @staticmethod
    def read_lines(filepath: str, encoding: str = "utf-8") -> List[str]:
        """Read file lines."""
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Failed to read lines from {filepath}: {e}")
            return []
    
    @staticmethod
    def load_json(filepath: str) -> Optional[dict]:
        """Load JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON {filepath}: {e}")
            return None
    
    @staticmethod
    def save_json(filepath: str, data: dict) -> bool:
        """Save JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save JSON {filepath}: {e}")
            return False
