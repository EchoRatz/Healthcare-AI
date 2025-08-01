"""
Logger Utility - Simple logging setup.
"""

import logging
import sys
from pathlib import Path


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Get configured logger."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(getattr(logging, level.upper()))
    
    return logger
